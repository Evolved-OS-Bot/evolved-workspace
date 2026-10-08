import copy
import unittest
from types import SimpleNamespace
from unittest.mock import Mock
from cancellation_finalizer.integrations import ProductionIntegrations
from cancellation_finalizer.engine import RetryLater

class ReportingScopeTests(unittest.TestCase):
    def setUp(self):
        self.context={'contact_id':'contact-1','cancellation_type':'pt','scope':'service_only','final_access_date':'2026-10-04','preflight':{'continuing_tabs':[]},'receipts':{s:{'verified':True,'verified_at':'2026-10-08T03:00:00+00:00'} for s in ['billing','trainerize','roster','ghl']}}
        self.context['receipts']['billing']['subscription_status']='canceled'
        self.row={'source_identities':[{'source':'ghl','source_record_id':'contact-1'}], 'person_id':'person-1','lifecycle':{'source':'membership_reconciliation','source_snapshot_id':'membership_reconciliation-snapshot','confidence':'verified','status':'cancelled','final_access_date':'2026-10-04'},'service_relationships':[],'payment_accounts':[{'source':'stripe','status':'cancelled','source_snapshot_id':'commercial_evidence_stripe-snapshot'}]}
        self.payload={'complete':False,'blocked_reasons':['stale required sources: pt_minder'],'rows':[self.row],'source_freshness':[{'source':s,'freshness':'stale' if s=='pt_minder' else 'fresh','observed_at':'2026-10-08T07:45:00+00:00','source_snapshot_id':s+'-snapshot'} for s in ['membership_reconciliation','active_client_cohort','commercial_evidence_stripe','pt_minder']]}
        response=Mock(ok=True);response.json.return_value=self.payload;session=Mock();session.get.return_value=response
        self.integration=ProductionIntegrations(SimpleNamespace(stripe_api_key='',hub_base_url='https://hub.example',hub_current_people_read_key='key'),session=session)
    def test_exact_terminal_stripe_only_case_passes(self):
        result=self.integration.verify_reporting(self.context)
        self.assertTrue(result['verified']);self.assertEqual(result['unrelated_stale_source'],'pt_minder')
    def test_each_missing_or_stale_required_source_blocks(self):
        for index in range(3):
            with self.subTest(index=index):
                prior=copy.deepcopy(self.payload['source_freshness'])
                self.payload['source_freshness'][index]['freshness']='stale'
                with self.assertRaises(RetryLater):self.integration.verify_reporting(self.context)
                self.payload['source_freshness']=prior
    def test_legacy_payment_account_blocks(self):
        self.row['payment_accounts'].append({'source':'pt_minder','status':'cancelled'})
        with self.assertRaises(RetryLater):self.integration.verify_reporting(self.context)
    def test_old_lifecycle_snapshot_blocks(self):
        self.row['lifecycle']['source_snapshot_id']='old'
        with self.assertRaises(RetryLater):self.integration.verify_reporting(self.context)
    def test_preclosure_observation_blocks(self):
        self.payload['source_freshness'][0]['observed_at']='2026-10-07T07:45:00+00:00'
        with self.assertRaises(RetryLater):self.integration.verify_reporting(self.context)
    def test_missing_source_receipt_blocks(self):
        del self.context['receipts']['trainerize']
        with self.assertRaises(RetryLater):self.integration.verify_reporting(self.context)
    def test_continuing_service_blocks(self):
        self.row['service_relationships']=[{'service_type':'sgpt','status':'active'}]
        with self.assertRaises(RetryLater):self.integration.verify_reporting(self.context)
    def test_other_projection_error_blocks(self):
        self.payload['blocked_reasons'].append('unresolved identity')
        with self.assertRaises(RetryLater):self.integration.verify_reporting(self.context)
    def test_wrong_boundary_blocks(self):
        self.row['lifecycle']['final_access_date']='2026-10-05'
        with self.assertRaises(RetryLater):self.integration.verify_reporting(self.context)
    def test_nonterminal_account_blocks(self):
        self.row['payment_accounts'][0]['status']='active'
        with self.assertRaises(RetryLater):self.integration.verify_reporting(self.context)
    def test_duplicate_identity_blocks(self):
        self.payload['rows'].append(copy.deepcopy(self.row))
        with self.assertRaises(RetryLater):self.integration.verify_reporting(self.context)
    def test_old_payment_snapshot_blocks(self):
        self.row['payment_accounts'][0]['source_snapshot_id']='old'
        with self.assertRaises(RetryLater):self.integration.verify_reporting(self.context)

    def test_corrected_historical_notice_clears_intake_issue(self):
        self.row['lifecycle']['cancellation_status']='Cancelled'
        cases=self.integration.discover_boundary_cases()
        self.assertEqual(cases,[])
        self.assertEqual(self.integration.discovery_issues,{'contact:contact-1':''})
