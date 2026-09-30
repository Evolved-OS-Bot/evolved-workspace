import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch
from cancellation_finalizer.integrations import ProductionIntegrations, FIELD_NAMES, ACTIVE_TABS, CANCELLED_MEMBER_STAGE_ID, CANCELLATION_PIPELINE_ID
from cancellation_finalizer.engine import FinalizationError

class ExitCleanupTest(unittest.TestCase):
    def test_discovery_uses_exact_ghl_identity_and_final_access(self):
        obj=self.integration();obj.settings.hub_base_url='https://hub.example';obj.settings.hub_current_people_read_key='key'
        row={'display':{'email':'a@example.com'},'source_identities':[{'source':'ghl','source_record_id':'c'}],'lifecycle':{'cancellation_status':'Notice Active','cancellation_type':'Membership','final_access_date':'2026-09-29'}}
        response=Mock(ok=True);response.json.return_value={'complete':True,'rows':[row,dict(row,lifecycle={'cancellation_status':'Cancelled'})],'source_freshness':[{'freshness':'fresh'}]}
        obj.session=Mock();obj.session.get.return_value=response
        self.assertEqual(len(obj.discover_boundary_cases()),1)
        self.assertEqual(obj.discover_boundary_cases()[0]['contact_id'],'c')

    def test_discovery_rejects_stale_hub(self):
        from cancellation_finalizer.engine import RetryLater
        obj=self.integration();obj.settings.hub_base_url='https://hub.example';obj.settings.hub_current_people_read_key='key'
        response=Mock(ok=True);response.json.return_value={'complete':True,'source_freshness':[{'freshness':'stale'}]}
        obj.session=Mock();obj.session.get.return_value=response
        with self.assertRaises(RetryLater):obj.discover_boundary_cases()

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
        obj=self.integration();sub.return_value=SimpleNamespace(status='canceled',customer='cus_x');customer.return_value=SimpleNamespace(email='different@example.com')
        with self.assertRaises(FinalizationError):obj.verify_billing({'email':'a@example.com','preflight':{'billing_result':'sub_abc','continuing_tabs':[]}})

    @patch('cancellation_finalizer.integrations.stripe.Subscription.list')
    @patch('cancellation_finalizer.integrations.stripe.Customer.retrieve')
    @patch('cancellation_finalizer.integrations.stripe.Subscription.retrieve')
    def test_past_due_continuing_contract_blocks_full_exit(self,sub,customer,subscriptions):
        obj=self.integration();sub.return_value=SimpleNamespace(status='canceled',customer='cus_x');customer.return_value=SimpleNamespace(email='a@example.com')
        subscriptions.return_value.auto_paging_iter.return_value=iter([SimpleNamespace(status='past_due')])
        with self.assertRaises(FinalizationError):obj.verify_billing({'email':'a@example.com','preflight':{'billing_result':'sub_abc','continuing_tabs':[]}})

    def preflight_fixture(self, extra=None):
        obj=self.integration();obj._fields=Mock(return_value={k:k for k in FIELD_NAMES})
        fields={'cancellation_status':'Notice Active','cancellation_type':'Membership','final_access_date':'2026-09-29','billing_status':'Succeeded','submitted_date':'2026-08-27',**(extra or {})}
        obj._contact=Mock(return_value={'email':'a@example.com','customFields':[{'id':k,'value':v} for k,v in fields.items()]})
        obj._roster_state=Mock(return_value={t:[] for t in ACTIVE_TABS});obj._ghl=Mock(return_value={'events':[],'notes':[]})
        return obj,{'contact_id':'c','email':'a@example.com','cancellation_type':'membership','final_access_date':'2026-09-29','scope':'service_only'}

    def test_pending_service_change_preserves_access(self):
        obj,payload=self.preflight_fixture({'service_change_status':'Pending Effective Date'})
        with self.assertRaisesRegex(FinalizationError,'unresolved service change'):obj.preflight(payload)
        obj._roster_state.assert_not_called()

    def test_appointment_boundary_is_brisbane_date(self):
        obj,payload=self.preflight_fixture()
        obj._ghl.return_value={'events':[{'startTime':'2026-09-29T20:00:00Z','appointmentStatus':'confirmed'}]}
        with self.assertRaisesRegex(FinalizationError,'future appointments'):obj.preflight(payload)

    def test_retained_sessions_preserve_access(self):
        obj,payload=self.preflight_fixture()
        obj._ghl.side_effect=[{'events':[]},{'notes':[{'body':'Retained sessions remain available. Do not deactivate.'}]}]
        with self.assertRaisesRegex(FinalizationError,'retained-session'):obj.preflight(payload)

    def test_changed_cancellation_episode_blocks_retry(self):
        obj,payload=self.preflight_fixture();payload['receipts']={'preflight':{'submitted_date':'2026-07-01'}}
        with self.assertRaisesRegex(FinalizationError,'episode changed'):obj.preflight(payload)

    @patch('cancellation_finalizer.integrations.stripe.SubscriptionSchedule.list')
    @patch('cancellation_finalizer.integrations.stripe.Subscription.list')
    @patch('cancellation_finalizer.integrations.stripe.Customer.retrieve')
    @patch('cancellation_finalizer.integrations.stripe.Subscription.retrieve')
    def test_future_schedule_preserves_access(self,sub,customer,subscriptions,schedules):
        obj=self.integration();sub.return_value=SimpleNamespace(status='canceled',customer='cus_x');customer.return_value=SimpleNamespace(email='a@example.com')
        subscriptions.return_value.auto_paging_iter.return_value=iter([])
        schedules.return_value.auto_paging_iter.return_value=iter([SimpleNamespace(status='not_started')])
        with self.assertRaisesRegex(FinalizationError,'future subscription schedule'):obj.verify_billing({'email':'a@example.com','preflight':{'billing_result':'sub_abc','continuing_tabs':[]}})

    def test_unused_pt_credit_blocks_deactivation(self):
        obj=self.integration();obj.settings.trainerize_api_base_url='https://api.example';obj.settings.trainerize_group_id='g';obj.settings.trainerize_api_token='t'
        obj._trainerize_rows=Mock(side_effect=[[{'id':42,'email':'a@example.com'}],[]])
        obj.session=Mock();obj.session.post.return_value.ok=True
        obj.session.post.return_value.json.return_value={'sessionCredits':[{'amount':2,'isExpired':False,'eventCategory':'appointment'}]}
        with self.assertRaisesRegex(FinalizationError,'unused non-class'):obj.reconcile_trainerize({'email':'a@example.com','preflight':{'deactivate_trainerize':True}})
        self.assertEqual(obj.session.post.call_count,1)
        self.assertTrue(obj.session.post.call_args.args[0].endswith('/getCreditList'))

    def test_naive_contact_list_uses_exact_calendar_event(self):
        obj,payload=self.preflight_fixture()
        obj._ghl.side_effect=[{'events':[{'id':'event-1','startTime':'2026-09-29 20:00:00','appointmentStatus':'confirmed'}]},{'appointment':{'startTime':'2026-09-29T20:00:00Z'}}]
        with self.assertRaisesRegex(FinalizationError,'future appointments'):obj.preflight(payload)
        self.assertEqual(obj._ghl.call_args.args[1],'/calendars/events/appointments/event-1')

    def test_unambiguously_old_naive_appointment_needs_no_timezone_guess(self):
        obj,payload=self.preflight_fixture()
        obj._ghl.side_effect=[{'events':[{'id':'event-1','startTime':'2026-06-03 08:30:00','appointmentStatus':'confirmed'}]},{'notes':[]}]
        self.assertTrue(obj.preflight(payload)['verified'])
        self.assertEqual(obj._ghl.call_count,2)

    @patch('cancellation_finalizer.integrations.stripe.SubscriptionSchedule.list')
    @patch('cancellation_finalizer.integrations.stripe.Subscription.list')
    @patch('cancellation_finalizer.integrations.stripe.Customer.retrieve')
    @patch('cancellation_finalizer.integrations.stripe.Subscription.retrieve')
    def test_stripe_sdk_customer_object_is_read_by_attribute(self,sub,customer,subscriptions,schedules):
        import stripe
        obj=self.integration();sub.return_value=SimpleNamespace(status='canceled',customer='cus_x')
        customer.return_value=stripe.Customer.construct_from({'id':'cus_x','email':'a@example.com'},'sk_test_unit')
        subscriptions.return_value.auto_paging_iter.return_value=iter([])
        schedules.return_value.auto_paging_iter.return_value=iter([])
        self.assertTrue(obj.verify_billing({'email':'a@example.com','preflight':{'billing_result':'sub_abc','continuing_tabs':[]}})['verified'])
