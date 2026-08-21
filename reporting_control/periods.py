from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date, timedelta


@dataclass(frozen=True)
class ReportingPeriod:
    """Explicit service and posting dates for one weekly KPI column."""

    service_start: date
    service_end: date
    posting_date: date
    stock_as_of: date

    @classmethod
    def from_kpi_posting_date(cls, posting_date: date) -> "ReportingPeriod":
        if posting_date.weekday() != 0:
            raise ValueError("A weekly KPI posting date must be a Monday")
        return cls(
            service_start=posting_date - timedelta(days=7),
            service_end=posting_date - timedelta(days=1),
            posting_date=posting_date,
            stock_as_of=posting_date,
        )

    @property
    def label(self) -> str:
        if (
            self.service_start.year == self.service_end.year
            and self.service_start.month == self.service_end.month
        ):
            return (
                f"{self.service_start.day}–"
                f"{self.service_end.strftime('%d %b %Y')}"
            )
        if self.service_start.year == self.service_end.year:
            return (
                f"{self.service_start.strftime('%d %b')}–"
                f"{self.service_end.strftime('%d %b %Y')}"
            )
        return (
            f"{self.service_start.strftime('%d %b %Y')}–"
            f"{self.service_end.strftime('%d %b %Y')}"
        )

    def to_dict(self) -> dict[str, str]:
        return {
            key: value.isoformat()
            for key, value in asdict(self).items()
        } | {"label": self.label}
