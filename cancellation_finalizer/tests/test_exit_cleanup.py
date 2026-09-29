import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch
from cancellation_finalizer.integrations import ProductionIntegrations, FIELD_NAMES, ACTIVE_TABS, CANCELLED_MEMBER_STAGE_ID, CANCELLATION_PIPELINE_ID
from cancellation_finalizer.engine import FinalizationError

class ExitCleanupTest(unittest.TestCase):
    def integration(self):
        obj=ProductionIntegrations(SimpleNamespace(stripe_api_key='',google_spreadsheet_id='sheet',ghl_location_id='location'))
        obj._require_writes=Mock()
        return obj

    def test_roster_re_resolves_moved_row_and_preserves_other_services(self):
        obj=self.integration();service=Mock();obj._sheets=Mock(return_value=service)
        obj._sheet_matches=Mock(side_effect=[[42],[12],[],[],[12],[]])
        result=obj.reconcile_roster({'email':'a@example.com','preflight':{'roster_before':{'Active SGPT':[5],'Active PT':[8],'Active Online':[]},'ending_tabs':['Active SGPT'],'continuing_tabs':['Active PT']}})
        self.assertEqual(result['cleared_ranges'],["'Active SGPT'!A42:K42"])

    def test_new_continuing_service_blocks_clear(self):
        obj=self.integration();obj._sheets=Mock();obj._sheet_matches=Mock(side_effect=[[42],[12],[]])
        with self.assertRaises(FinalizationError):
            obj.reconcile_roster({'email':'a@example.com','preflight':{'roster_before':{'Active SGPT':[5],'Active PT':[],'Active Online':[]},'ending_tabs':['Active SGPT'],'continuing_tabs':[]}})
        obj._sheets.return_value.spreadsheets.assert_not_called()

    def test_already_closed_opportunity_is_idempotent(self):
        obj=self.integration();row={'id':'o','contactId':'c','pipelineId':CANCELLATION_PIPELINE_ID,'pipelineStageId':CANCELLED_MEMBER_STAGE_ID,'status':'lost'}
        obj._ghl=Mock(return_value={'opportunities':[row]})
        self.assertEqual(obj._cancellation_opportunity('c'),row)

    def test_ambiguous_opportunity_is_rejected(self):
        obj=self.integration();row={'id':'o','contactId':'c','pipelineId':CANCELLATION_PIPELINE_ID,'status':'open'}
        obj._ghl=Mock(return_value={'opportunities':[row,dict(row,id='other')]})
        with self.assertRaises(FinalizationError):obj._cancellation_opportunity('c')

    def test_exceptions_never_create_staff_tasks(self):
        obj=self.integration();obj._ghl=Mock()
        self.assertTrue(obj.create_exception({},'failed')['held']);obj._ghl.assert_not_called()

    def test_pt_already_absent_from_roster_can_finish(self):
        obj=self.integration();obj._fields=Mock(return_value={k:k for k in FIELD_NAMES})
        obj._contact=Mock(return_value={'email':'a@example.com','customFields':[{'id':k,'value':v} for k,v in {'cancellation_status':'Notice Active','cancellation_type':'PT','final_access_date':'2026-09-01','billing_status':'Succeeded','submitted_date':'2026-08-01'}.items()]})
        obj._roster_state=Mock(return_value={t:[] for t in ACTIVE_TABS})
        obj._ghl=Mock(return_value={'events':[]})
        r=obj.preflight({'contact_id':'c','email':'a@example.com','cancellation_type':'pt','final_access_date':'2026-09-01','scope':'service_only'})
        self.assertTrue(r['verified'])

    @patch('cancellation_finalizer.integrations.stripe.Customer.retrieve')
    @patch('cancellation_finalizer.integrations.stripe.Subscription.retrieve')
    def test_wrong_subscription_owner_rejected(self,sub,customer):
        obj=self.integration();sub.return_value=SimpleNamespace(status='canceled',customer='cus_x');customer.return_value={'email':'different@example.com'}
        with self.assertRaises(FinalizationError):obj.verify_billing({'email':'a@example.com','preflight':{'billing_result':'sub_abc','continuing_tabs':[]}})

    @patch('cancellation_finalizer.integrations.stripe.Subscription.list')
    @patch('cancellation_finalizer.integrations.stripe.Customer.retrieve')
    @patch('cancellation_finalizer.integrations.stripe.Subscription.retrieve')
    def test_past_due_continuing_contract_blocks_full_exit(self,sub,customer,subscriptions):
        obj=self.integration();sub.return_value=SimpleNamespace(status='canceled',customer='cus_x');customer.return_value={'email':'a@example.com'}
        subscriptions.return_value.auto_paging_iter.return_value=iter([SimpleNamespace(status='past_due')])
        with self.assertRaises(FinalizationError):obj.verify_billing({'email':'a@example.com','preflight':{'billing_result':'sub_abc','continuing_tabs':[]}})
