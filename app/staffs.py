from dataclasses import dataclass
from pathlib import Path

import yaml

from app import DATA_DIR, app
from app.db import Staff


@dataclass
class StaffEntry:
    name: str
    discord_id: str


def reset():
    with (DATA_DIR / "staffs.yml").open() as f:
        staffs = [
            StaffEntry(name, discord_id)
            for name, discord_id in yaml.safe_load(f).items()
        ]
    with app.session() as s:
        db_staffs = s.query(Staff).all()
        db_staff_by_name = {staff.name: staff for staff in db_staffs}
        for staff in staffs:
            if staff.name not in db_staff_by_name:
                s.add(Staff(name=staff.name, discord_id=staff.discord_id))
                s.commit()
                continue
            db_staff = db_staff_by_name[staff.name]
            if db_staff.discord_id != staff.discord_id:
                db_staff.discord_id = staff.discord_id
                s.commit()
