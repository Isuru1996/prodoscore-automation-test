from dataclasses import dataclass
from typing import Optional

from automation_lib.core import BaseModel


@dataclass
class OrganizationProdoscore(BaseModel):
    model_name: str = "OrganizationProdoscoreModel"
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
        self.logger.info(
            f"Committing changes for organization prodoscore (ID: {self.id}, Date: {self.date})"
        )
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
        self.logger.info(
            f"Changing organization prodoscore date from {self.date} to {new_date}"
        )
        self.date = new_date

    def change_score(self, new_score: float) -> None:
        self.logger.info(f"Changing organization prodoscore score to {new_score}")
        self.score = new_score

    def change_finalized(self, new_finalized: int) -> None:
        self.logger.info(
            f"Changing organization prodoscore finalized to {new_finalized}"
        )
        self.finalized = new_finalized

    def change_performance_alerts(self, new_performance_alerts: int) -> None:
        self.logger.info(
            f"Changing organization prodoscore performance_alerts to {new_performance_alerts}"
        )
        self.performance_alerts = new_performance_alerts

    def change_notifications(self, new_notifications: int) -> None:
        self.logger.info(
            f"Changing organization prodoscore notifications to {new_notifications}"
        )
        self.notifications = new_notifications

    def change_transcripts(self, new_transcripts: int) -> None:
        self.logger.info(
            f"Changing organization prodoscore transcripts to {new_transcripts}"
        )
        self.transcripts = new_transcripts

    def change_correlations(self, new_correlations: int) -> None:
        self.logger.info(
            f"Changing organization prodoscore correlations to {new_correlations}"
        )
        self.correlations = new_correlations

    def change_collaboration(self, new_collaboration: int) -> None:
        self.logger.info(
            f"Changing organization prodoscore collaboration to {new_collaboration}"
        )
        self.collaboration = new_collaboration

    def change_nlp_cost(self, new_nlp_cost: int) -> None:
        self.logger.info(f"Changing organization prodoscore nlp_cost to {new_nlp_cost}")
        self.nlp_cost = new_nlp_cost
