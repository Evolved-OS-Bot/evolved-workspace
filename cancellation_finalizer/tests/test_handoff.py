import json
import secrets
import time
import unittest
from types import SimpleNamespace
from unittest.mock import Mock
from cancellation_finalizer.app import create_app
from cancellation_finalizer.config import Settings
from cancellation_finalizer.engine import Finalizer, normalize_payload
from cancellation_finalizer.integrations import ProductionIntegrations
from cancellation_finalizer.repository import Repository
from cancellation_finalizer.security import calculate_signature
from dataclasses import replace

class HandoffTest(unittest.TestCase):
    def setUp(self):
        self.repo = Repository('sqlite:///:memory:'); self.repo.create_schema()
        self.external = Mock()
        self.settings = replace(Settings.from_env(), database_url='sqlite:///:memory:', webhook_signing_secret='a'*40, admin_secret='b'*40, worker_enabled=False)
        self.app = create_app(self.settings, repository=self.repo, integrations=self.external).test_client()
        self.payload = dict(contact_id='contact',email='member@example.com',cancellation_type='pt',final_access_date='2099-10-11',scope='service_only')
    def post(self, payload=None, nonce=None):
        body=json.dumps(payload or self.payload).encode(); stamp=str(int(time.time())); nonce=nonce or secrets.token_hex(16)
        sig=calculate_signature(self.settings.webhook_signing_secret,stamp,nonce,body)
        return self.app.post('/api/v1/cancellations/queue',data=body,headers={'Content-Type':'application/json','X-Cancellation-Timestamp':stamp,'X-Cancellation-Nonce':nonce,'X-Cancellation-Signature':sig})
    def test_signed_queue_persists_without_closure_and_replays_idempotently(self):
        a=self.post(); b=self.post(); self.assertEqual(a.status_code,200);self.assertEqual(a.json,b.json)
        self.assertTrue(a.json['durable']); self.external.preflight.assert_not_called();self.external.reconcile_trainerize.assert_not_called()
        self.assertEqual(self.repo.get(a.json['idempotency_key']).status,'queued')
    def test_invalid_signature_and_nonce_replay_fail(self):
        self.assertEqual(self.app.post('/api/v1/cancellations/queue',json=self.payload).status_code,401)
        self.assertEqual(self.post(nonce='n'*32).status_code,200)
        self.assertEqual(self.post(nonce='n'*32).status_code,409)
    def test_missing_date_is_never_queued(self):
        self.assertEqual(self.post(dict(self.payload,final_access_date='')).status_code,422)
    def test_existing_task_preserved(self):
        old=normalize_payload(dict(self.payload,final_task_id='task'));self.repo.upsert(old,now=__import__('datetime').datetime.now(__import__('datetime').UTC))
        self.assertEqual(self.post().status_code,200);self.assertEqual(self.repo.get(old['idempotency_key']).payload['final_task_id'],'task')
    def test_changed_source_rejected(self):
        self.external.verify_queue_boundary.side_effect=ValueError('changed')
        self.assertEqual(self.post().status_code,422)
    def test_durable_intake_issues_require_admin(self):
        self.repo.record_intake_issue('contact:x','Missing date')
        self.assertEqual(self.app.get('/api/v1/admin/intake-issues').status_code,401)
        r=self.app.get('/api/v1/admin/intake-issues',headers={'X-Cancellation-Admin-Secret':'b'*40});self.assertEqual(len(r.json['issues']),1)
        self.repo.record_intake_issue('contact:x','',active=False);self.assertEqual(self.repo.intake_issues(),[])
    def test_discovery_failure_is_durable(self):
        self.external.discover_boundary_cases.side_effect=RuntimeError('offline')
        Finalizer(self.repo,self.external).process_due();self.assertEqual(self.repo.intake_issues()[0]['key'],'discovery')
    def test_invalid_row_does_not_hide_later_row(self):
        self.external.discovery_issues={};self.external.discover_boundary_cases.return_value=[dict(self.payload,contact_id='bad',final_access_date='invalid'),self.payload]
        Finalizer(self.repo,self.external).process_due();self.assertIsNotNone(self.repo.get(normalize_payload(self.payload)['idempotency_key']))
        self.assertEqual(self.repo.intake_issues()[0]['key'],'contact:bad')
    def test_fresh_lifecycle_can_discover_when_unrelated_source_stale(self):
        obj=ProductionIntegrations(SimpleNamespace(stripe_api_key='',hub_base_url='https://example.com',hub_current_people_read_key='key'),session=Mock())
        row={'person_id':'p','display':{'email':'member@example.com'},'source_identities':[{'source':'ghl','source_record_id':'contact'}],'lifecycle':{'cancellation_status':'Notice Active','cancellation_type':'PT','final_access_date':'2099-10-11'}}
        obj.session.get.return_value.json.return_value={'complete':False,'blocked_reasons':['legacy stale'],'source_freshness':[{'source':'membership_reconciliation','freshness':'fresh'},{'source':'pt_minder','freshness':'stale'}],'rows':[row,dict(row,person_id='missing',source_identities=[{'source':'ghl','source_record_id':'missing'}],lifecycle={'cancellation_status':'Notice Active'})]}
        self.assertEqual(len(obj.discover_boundary_cases()),1);self.assertIn('contact:missing',obj.discovery_issues)
