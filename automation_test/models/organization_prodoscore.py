from dataclasses import dataclass
from typing import Optional


@dataclass
class OrganizationProdoscore:
    id: Optional[int] = None
    domain_id: int = 0
    date: str = ""
    score: float = 0.0
    finalized: int = 0
    performance_alerts: int = 1
    notifications: int = 0
    transcripts: int = 0
    correlations: int = 0
    collaboration: int = 0
    nlp_cost: int = 0

    def commit(self, db_util) -> None:
        """
        Commits the current state of the OrganizationProdoscore object to the database.
        Args:
            db_util: Database utility with an update_data method
        """
        row_to_update = {
            "domain_id": self.domain_id,
            "date": self.date,
            "score": self.score,
            "finalized": self.finalized,
            "performance_alerts": self.performance_alerts,
            "notifications": self.notifications,
            "transcripts": self.transcripts,
            "correlations": self.correlations,
            "collaboration": self.collaboration,
            "nlp_cost": self.nlp_cost,
        }
        db_util.update_data(
            "proapp_organization_prodoscore", row_to_update, f"id = '{self.id}'"
        )

    def change_date(self, new_date: str) -> None:
        self.date = new_date

    def change_score(self, new_score: float) -> None:
        self.score = new_score

    def change_finalized(self, new_finalized: int) -> None:
        self.finalized = new_finalized

    def change_performance_alerts(self, new_performance_alerts: int) -> None:
        self.performance_alerts = new_performance_alerts

    def change_notifications(self, new_notifications: int) -> None:
        self.notifications = new_notifications

    def change_transcripts(self, new_transcripts: int) -> None:
        self.transcripts = new_transcripts

    def change_correlations(self, new_correlations: int) -> None:
        self.correlations = new_correlations

    def change_collaboration(self, new_collaboration: int) -> None:
        self.collaboration = new_collaboration

    def change_nlp_cost(self, new_nlp_cost: int) -> None:
        self.nlp_cost = new_nlp_cost
