from datetime import date

from pt_booking_shadow.config import FIELD_IDS
from pt_booking_shadow.service import ShadowAuditService


class FakeClient:
    contact_id = "cathy"

    def list_contacts(self):
        return [
            {
                "id": self.contact_id,
                "firstName": "Cathy",
                "lastName": "James",
                "tags": ["personal training"],
                "customFields": [
                    {
                        "id": FIELD_IDS["cancellation_type"],
                        "value": "PT",
                    },
                    {
                        "id": FIELD_IDS["cancellation_status"],
                        "value": "Notice Active",
                    },
                ],
            }
        ]

    def list_opportunities(self):
        return []

    def get_contact(self, contact_id):
        assert contact_id == self.contact_id
        raw = self.list_contacts()[0]
        raw["customFields"].append(
            {
                "id": FIELD_IDS["final_access"],
                "value": "2026-07-24",
            }
        )
        return raw


def test_status_sensitive_contact_is_hydrated_before_reconciliation():
    service = object.__new__(ShadowAuditService)
    service.client = FakeClient()

    cohort = service._resolve_full_cohort()

    assert len(cohort) == 1
    assert cohort[0].effective_status == "pt_cancellation"
    assert cohort[0].final_access == date(2026, 7, 24)
