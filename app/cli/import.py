from datetime import datetime, time, timedelta

import click
import unidecode
from pydantic import BaseModel, Field

from app import app, gsheet


@app.cli.group("import")
def import_():
    pass


# Guest-of nicks whose real inviter can't be reliably parsed automatically
# (typos, missing closing paren, junk glued onto the name).
GUEST_INVITER_OVERRIDES = {
    '"+1 de koa (à copleter"': "koa",
    '"+3 de Nono"(à compléter)': "Nono",
}


def extract_invited_by_nick(nick: str) -> str | None:
    # e.g. "(+1 de Azerole)" -> "Azerole", "momoirokaichou +1" -> "momoirokaichou"
    if nick in GUEST_INVITER_OVERRIDES:
        return GUEST_INVITER_OVERRIDES[nick]
    words = nick.strip('() "').split()
    for i, word in enumerate(words):
        if not (word.startswith("+") and word[1:].isdigit()):
            continue
        if i > 0:
            return " ".join(words[:i])
        if i + 1 < len(words) and words[i + 1] == "de" and i + 2 < len(words):
            return " ".join(words[i + 2 :])
        return None
    return None


def is_guest_of_nick(nick: str) -> bool:
    return extract_invited_by_nick(nick) is not None


class SheetVisitor(BaseModel):
    last_name: str | None = Field(validation_alias="Nom")
    email: str | None = Field(validation_alias="Email")
    first_name: str | None = Field(validation_alias="Prénom")
    nick: str | None = Field(validation_alias="Pseudo")

    @property
    def full_name(self):
        if not self.first_name:
            return self.last_name
        if not self.last_name:
            return self.first_name
        return f"{self.first_name} {self.last_name}"

    def model_post_init(self, _context):
        def clean_from_multiple_spaces(s: str) -> str:
            if not s:
                return None
            return " ".join(s.split())

        if self.email:
            self.email = self.email.lower().strip() or None
        if self.first_name:
            self.first_name = self.first_name.title()
        if self.last_name:
            self.last_name = self.last_name.title()

        if self.nick:
            self.nick = self.nick.strip(' "')

        if self.nick in NICK_OVERRIDES:
            print(
                f"Overriding nick {self.nick!r} -> {NICK_OVERRIDES[self.nick]!r}"
            )
            self.nick = NICK_OVERRIDES[self.nick]
        elif self.nick and is_guest_of_nick(self.nick):
            print(f"Removing guest-of nick: {self.nick!r}")
            self.nick = None

        if self.nick and self.nick.find("(") != -1 and self.nick[-1] == ")":
            nick = unidecode.unidecode(self.nick)
            if nick.endswith(("(a completer)", "(a remplir)")):
                print("Removing suffix", nick[nick.find("(") :])
                self.nick = self.nick[: self.nick.find("(")].strip()

        if self.nick and self.nick == self.full_name:
            print("Removing nick equal to full name", self.nick)
            self.nick = None

        for attr in ["first_name", "last_name", "nick"]:
            if not getattr(self, attr):
                continue
            setattr(self, attr, clean_from_multiple_spaces(getattr(self, attr)))

    @property
    def is_empty(self):
        return not bool(
            self.first_name or self.last_name or self.email or self.nick
        )


# Raw sheet Pseudo values that need manual cleanup beyond the generic rules.
NICK_OVERRIDES = {
    "Sylvain (Coeuilly) Champigny joue (à compléter)": "Sylvain (Champigny joue)",
}

# Nicks that were renamed in the sheet at some point, without a stable id to
# match the old and new row - map the new nick to old nick(s) also in use.
# Used for matching/lookup fallback in both visitors() and openings().
NICK_ALIASES = {
    "Meta": ["Meta-Link"],
    "Kone": ["oneyu"],
    "Le grandgrand": ["Legrandgrand"],
    "pseud007 / natbeng": ["pseud007"],
    "Xjemomo": ["Yumeko"],
    "Sylvain (Champigny joue)": ["Sylvain (Coeuilly) Champigny joue"],
    "Razmotte": ["Morgane Dahuron"],
}

# Reverse of NICK_ALIASES (old alias -> canonical nick), so lookups work
# regardless of whether a sheet uses the canonical or the old spelling.
NICK_ALIASES_REVERSE = {
    alias: canonical
    for canonical, aliases in NICK_ALIASES.items()
    for alias in aliases
}

# Subset of confirmed renames (not just day-sheet spelling variants) that
# visitors() should actually apply to the db when found.
NICK_RENAMES = {
    "Meta": ["Meta-Link"],
    "Kone": ["oneyu"],
    "pseud007 / natbeng": ["pseud007"],
    "Xjemomo": ["Yumeko"],
}

# Known cases where a nick-only stub Visitor and a separate Visitor with the
# real name/email are actually the same person - merge the stub into the
# email-matched Visitor and delete the stub. "first_name" optionally
# overrides the kept visitor's first name (e.g. a misspelled duplicate row).
MERGE_NICK_INTO_EMAIL = {
    "yozakura": {"email": "zzzbbr2003@gmail.com"},
    "Razmotte": {"email": "spoonies@hotmail.fr", "first_name": "Morgan"},
}


def merge_visitor_duplicate(s, keep, remove):
    for visit in list(remove.visits):
        visit.visitor = keep
    for visit in list(remove.invitees):
        visit.invited_by = keep
    if not keep.nick and remove.nick:
        keep.nick = remove.nick
    s.delete(remove)


@import_.command()
def visitors():
    if not gsheet.is_ready:
        print("Google Sheets module is not ready")
        return

    from app.db import Visitor

    created = []
    sheet = gsheet.gc.open("Visiteurs")
    worksheet = sheet.get_worksheet(0)
    print("Got sheet", worksheet)
    expected_headers = [
        field.validation_alias for field in SheetVisitor.model_fields.values()
    ]
    for row in worksheet.get_all_records(expected_headers=expected_headers):
        sheet_visitor = SheetVisitor(**row)
        if sheet_visitor.is_empty:
            print("Skipping empty row", row)
            continue
        with app.session() as s:
            merge_info = MERGE_NICK_INTO_EMAIL.get(sheet_visitor.nick)
            if merge_info:
                nick_visitor = (
                    s.query(Visitor).filter_by(nick=sheet_visitor.nick).first()
                )
                email_visitor = (
                    s.query(Visitor)
                    .filter_by(email=merge_info["email"])
                    .first()
                )
                if (
                    nick_visitor
                    and email_visitor
                    and nick_visitor.id != email_visitor.id
                ):
                    print(f"  Merging {nick_visitor} into {email_visitor}")
                    merge_visitor_duplicate(
                        s, keep=email_visitor, remove=nick_visitor
                    )
                    if "first_name" in merge_info:
                        email_visitor.first_name = merge_info["first_name"]
                    s.commit()

            candidates = {}
            if sheet_visitor.email:
                v = (
                    s.query(Visitor)
                    .filter_by(email=sheet_visitor.email)
                    .first()
                )
                # An email can be shared by different family members - only
                # trust the match if the first name doesn't conflict (last
                # name is expected to match for a family sharing an email).
                name_conflict = (
                    v
                    and sheet_visitor.first_name
                    and v.first_name
                    and v.first_name != sheet_visitor.first_name
                )
                if v and not name_conflict:
                    candidates[v.id] = v
            if sheet_visitor.first_name and sheet_visitor.last_name:
                v = (
                    s.query(Visitor)
                    .filter(
                        Visitor.first_name == sheet_visitor.first_name,
                        Visitor.last_name == sheet_visitor.last_name,
                    )
                    .first()
                )
                if v:
                    candidates[v.id] = v
            if sheet_visitor.nick:
                nicks = [
                    sheet_visitor.nick,
                    *NICK_ALIASES.get(sheet_visitor.nick, []),
                ]
                for nick in nicks:
                    v = s.query(Visitor).filter_by(nick=nick).first()
                    if v:
                        candidates[v.id] = v

            if len(candidates) > 1:
                click.secho(
                    f"  Warning: {sheet_visitor} matches multiple existing"
                    f" visitors: {list(candidates.values())}",
                    fg="yellow",
                )

            db_visitor = next(iter(candidates.values()), None)
            if db_visitor:
                # Only rename known, pre-vetted pairs (NICK_ALIASES) - the
                # sheet has stale duplicate rows and family members sharing
                # an email, so blindly syncing on any match would cause
                # nicks to flip-flop between unrelated rows.
                if db_visitor.nick in NICK_RENAMES.get(sheet_visitor.nick, []):
                    print(
                        f"  Renaming {db_visitor}:"
                        f" {db_visitor.nick!r} -> {sheet_visitor.nick!r}"
                    )
                    db_visitor.nick = sheet_visitor.nick
                    s.commit()
                print("Skipping existing user", db_visitor)
                continue
            print("Creating user", sheet_visitor)
            db_visitor = Visitor(
                first_name=sheet_visitor.first_name,
                last_name=sheet_visitor.last_name,
                email=sheet_visitor.email,
                nick=sheet_visitor.nick,
            )
            s.add(db_visitor)
            s.commit()
            print("Created user", db_visitor)
            created.append(db_visitor)

    print("Created", len(created), "visitors")


def is_day_worksheet_title(title: str) -> bool:
    parts = title.split("-")
    return (
        len(parts) == 3
        and all(part.isdigit() for part in parts)
        and [len(part) for part in parts] == [4, 2, 2]
    )


def find_header_row(
    values: list[list[str]],
) -> tuple[int, dict[str, int]] | None:
    # Column order/extra columns vary by sheet era, so look up the header
    # row by name instead of assuming a fixed position.
    for row_index, row in enumerate(values):
        columns = {
            cell.strip(): index
            for index, cell in enumerate(row)
            if cell.strip()
        }
        if "Pseudo" in columns and "Arrivée" in columns:
            return row_index, columns
    return None


def get_cell(row: list[str], columns: dict[str, int], name: str) -> str:
    index = columns.get(name)
    if index is None or index >= len(row):
        return ""
    return row[index].strip()


def strip_parenthetical_suffix(nick: str) -> str:
    # Day sheets sometimes annotate the Pseudo cell, e.g. "Princesse (1j
    # gratos)" - the Visitor's actual nick doesn't include that suffix.
    if nick.endswith(")") and "(" in nick:
        return nick[: nick.rfind("(")].strip()
    return nick


def find_visitor_by_nick(s, Visitor, nick: str):
    db_visitor = s.query(Visitor).filter_by(nick=nick).first()
    lookup_nick = strip_parenthetical_suffix(nick)
    if not db_visitor and lookup_nick != nick:
        db_visitor = s.query(Visitor).filter_by(nick=lookup_nick).first()
    alt_nicks = [
        *NICK_ALIASES.get(lookup_nick, []),
        NICK_ALIASES_REVERSE.get(lookup_nick),
    ]
    for alias in alt_nicks:
        if db_visitor or not alias:
            break
        db_visitor = s.query(Visitor).filter_by(nick=alias).first()
    if not db_visitor:
        # Some visitors have no nick because it equalled their full name and
        # got stripped during import (see SheetVisitor.model_post_init) -
        # day-sheets still print the full name as the Pseudo, so fall back
        # to matching on that.
        for candidate in s.query(Visitor).filter(Visitor.nick.is_(None)):
            if candidate.full_name == lookup_nick:
                db_visitor = candidate
                break
    return db_visitor


def parse_time_cell(value: str) -> time | None:
    if not value:
        return None
    # Older sheets write times as "17h30" or bare "17h" instead of "17:30".
    parts = value.replace("h", ":").split(":")
    if not parts[0]:
        return None
    try:
        # Some sheets write past-midnight times as e.g. "25:23" for 01:23 the
        # next day - the day-rollover itself is handled where entry/exit are
        # combined with the day (exit < entry gets bumped by one day).
        hour = int(parts[0]) % 24
        minute = int(parts[1]) if len(parts) > 1 and parts[1] else 0
        return time(hour, minute)
    except ValueError:
        return None


def parse_tarif_cell(value: str) -> float | None:
    if not value:
        return None
    try:
        return float(value.replace(",", "."))
    except ValueError:
        return None


OPENINGS_FOLDER_ID = "1dJ0n7rkn-KheAWr6JTn1Wo6sCztlsb0q"


def is_month_sheet_name(name: str) -> bool:
    parts = name.split("-")
    return (
        len(parts) == 2
        and all(part.isdigit() for part in parts)
        and [len(part) for part in parts] == [4, 2]
    )


@import_.command()
@click.argument("month", required=False)
def openings(month=None):
    if not gsheet.is_ready:
        print("Google Sheets module is not ready")
        return

    from app.db import Opening, Visit, Visitor

    if month:
        months = [month]
    else:
        months = sorted(
            f["name"]
            for f in gsheet.gc.list_spreadsheet_files(
                folder_id=OPENINGS_FOLDER_ID
            )
            if is_month_sheet_name(f["name"])
        )

    for month_name in months:
        print(f"=== {month_name} ===")
        sheet = gsheet.gc.open(month_name)
        print("Got sheet", sheet)
        for worksheet in sheet.worksheets():
            if not is_day_worksheet_title(worksheet.title):
                print("Skipping worksheet", worksheet.title)
                continue
            day = datetime.strptime(worksheet.title, "%Y-%m-%d").date()

            values = worksheet.get_all_values()
            header = find_header_row(values)
            if header is None:
                print("  Could not find header row, skipping")
                continue
            header_row_index, columns = header

            with app.session() as s:
                start = datetime.combine(day, time(16, 0))
                opening = s.query(Opening).filter_by(start=start).first()
                if opening:
                    print("  Opening already exists for", day)
                else:
                    opening = Opening(
                        start=start,
                        end=datetime.combine(day, time(22, 0)),
                        scope=Opening.Scope.PUBLIC,
                    )
                    s.add(opening)
                    print("Created opening", opening)

                existing_visits_by_identity = {
                    (visit.visitor_id, visit.invited_by_id): visit
                    for visit in opening.visits
                }

                for row in values[header_row_index + 1 :]:
                    nick = get_cell(row, columns, "Pseudo")
                    if not nick or nick.startswith("LIMITE LEGALE"):
                        continue
                    if nick.upper() == "NON":
                        print("  Skipping placeholder row", nick)
                        continue

                    db_visitor = None
                    invited_by = None
                    if is_guest_of_nick(nick):
                        invited_by_nick = extract_invited_by_nick(nick)
                        if invited_by_nick:
                            invited_by = find_visitor_by_nick(
                                s, Visitor, invited_by_nick
                            )
                        if not invited_by and invited_by_nick:
                            click.secho(
                                f"  Creating new visitor for inviter"
                                f" {invited_by_nick!r} on {day}",
                                fg="yellow",
                            )
                            invited_by = Visitor(nick=invited_by_nick)
                            s.add(invited_by)
                            s.flush()
                    else:
                        db_visitor = find_visitor_by_nick(s, Visitor, nick)
                        if not db_visitor:
                            click.secho(
                                f"  Creating new visitor for nick {nick!r} on"
                                f" {day}",
                                fg="yellow",
                            )
                            db_visitor = Visitor(nick=nick)
                            s.add(db_visitor)
                            s.flush()

                    arrival = parse_time_cell(get_cell(row, columns, "Arrivée"))
                    departure = parse_time_cell(
                        get_cell(row, columns, "Sortie")
                    )
                    entry = datetime.combine(day, arrival) if arrival else None
                    exit_ = (
                        datetime.combine(day, departure) if departure else None
                    )
                    if entry and exit_ and exit_ < entry:
                        # Sortie is past midnight (e.g. entry 21:04, exit 00:03)
                        exit_ += timedelta(days=1)

                    payment = get_cell(row, columns, "CB / Liquide")
                    notes = get_cell(row, columns, "Notes")
                    supplement = get_cell(row, columns, "Supplément")
                    note = (
                        ", ".join(
                            part
                            for part in (payment, notes, supplement)
                            if part
                        )
                        or None
                    )

                    identity_key = (
                        db_visitor.id if db_visitor else None,
                        invited_by.id if invited_by else None,
                    )
                    existing_visit = existing_visits_by_identity.get(
                        identity_key
                    )
                    if existing_visit:
                        updated_fields = []
                        if entry is not None and existing_visit.entry is None:
                            existing_visit.entry = entry
                            updated_fields.append("entry")
                        if exit_ is not None and existing_visit.exit is None:
                            existing_visit.exit = exit_
                            updated_fields.append("exit")
                        if note is not None and existing_visit.note is None:
                            existing_visit.note = note
                            updated_fields.append("note")
                        if not existing_visit.paid and bool(
                            existing_visit.entry and existing_visit.exit
                        ):
                            existing_visit.paid = True
                            updated_fields.append("paid")
                        if updated_fields:
                            print(
                                f"  Updating visit for {nick}:"
                                f" {', '.join(updated_fields)}"
                            )
                        else:
                            print(
                                "  Visit already exists for",
                                nick,
                                entry,
                                exit_,
                            )
                        continue

                    visit = Visit(
                        opening=opening,
                        visitor=db_visitor,
                        invited_by=invited_by,
                        entry=entry,
                        exit=exit_,
                        paid=bool(entry and exit_),
                        billed_amount=parse_tarif_cell(
                            get_cell(row, columns, "Tarif")
                        ),
                        note=note,
                    )
                    s.add(visit)
                    existing_visits_by_identity[identity_key] = visit
                    print("  Created visit", nick, entry, exit_)

                s.commit()
