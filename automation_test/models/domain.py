from dataclasses import dataclass
from typing import Optional

from automation_lib.core import BaseModel


@dataclass
class Domain(BaseModel):
    model_name: str = "DomainModel"
    id: Optional[int] = None
    title: str = ""
    origin: str = ""
    show_details: int = 0
    workingdays: str = ""
    timezone: str = ""
    workshift_enable: int = 0
    daystart: str = ""
    dayend: str = ""
    gap_time: int = 0
    active_time: int = 0
    gap_time_start: str = ""
    gap_time_end: str = ""
    ipscanner_enabled: int = 0
    ipscanner_method: int = 0
    crx_modules: str = ""
    collab_enabled: int = 0
    collab_modules: int = 0
    workplace_prod: int = 0

    def commit(self, db_client):
        self.logger.info(f"Committing changes for domain {self.title} (ID: {self.id})")
        row_to_update = {
            "title": self.title,
            "origin": self.origin,
            "show_details": self.show_details,
            "workingdays": self.workingdays,
            "timezone": self.timezone,
            "workshift_enable": self.workshift_enable,
            "daystart": self.daystart,
            "dayend": self.dayend,
            "gap_time": self.gap_time,
            "active_time": self.active_time,
            "gap_time_start": self.gap_time_start,
            "gap_time_end": self.gap_time_end,
            "ipscanner_enabled": self.ipscanner_enabled,
            "ipscanner_method": self.ipscanner_method,
            "crx_modules": self.crx_modules,
            "collab_enabled": self.collab_enabled,
            "collab_modules": self.collab_modules,
            "workplace_prod": self.workplace_prod,
        }
        set_clause = ", ".join(f"{k} = %s" for k in row_to_update)
        values = list(row_to_update.values())
        sql = f"UPDATE proapp_domain SET {set_clause} WHERE id = %s"
        db_client.execute_update(sql, tuple(values + [self.id]))

    def change_title(self, new_title):
        self.logger.info(f"Changing domain title from {self.title} to {new_title}")
        self.title = new_title

    def change_timezone(self, new_timezone):
        self.logger.info(f"Changing {self.title} timezone to {new_timezone}")
        self.timezone = new_timezone

    def change_workingdays(self, new_workingdays):
        self.logger.info(f"Changing {self.title} workingdays to {new_workingdays}")
        self.workingdays = new_workingdays

    def change_daystart(self, new_daystart):
        self.logger.info(f"Changing {self.title} daystart to {new_daystart}")
        self.daystart = new_daystart

    def change_dayend(self, new_dayend):
        self.logger.info(f"Changing {self.title} dayend to {new_dayend}")
        self.dayend = new_dayend

    def change_gap_time(self, new_gap_time):
        self.logger.info(f"Changing {self.title} gap_time to {new_gap_time}")
        self.gap_time = new_gap_time

    def change_active_time(self, new_active_time):
        self.logger.info(f"Changing {self.title} active_time to {new_active_time}")
        self.active_time = new_active_time

    def change_collab_enabled(self, new_collab_enabled):
        self.logger.info(
            f"Changing {self.title} collab_enabled to {new_collab_enabled}"
        )
        self.collab_enabled = new_collab_enabled

    def change_collab_modules(self, new_collab_modules):
        self.logger.info(
            f"Changing {self.title} collab_modules to {new_collab_modules}"
        )
        self.collab_modules = new_collab_modules

    def change_workplace_prod(self, new_workplace_prod):
        self.logger.info(
            f"Changing {self.title} workplace_prod to {new_workplace_prod}"
        )
        self.workplace_prod = new_workplace_prod
