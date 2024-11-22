import unidecode
from pydantic import BaseModel, Field

from app import app, gsheet


@app.cli.group("import")
def import_():
    pass


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

        if self.nick and self.nick[0] == "+":
            words = self.nick.split()
            if len(words) > 1 and words[1] == "de":
                print('Removing nick "+X de <name>"')
                self.nick = None

        if self.nick and self.nick.find("(") != -1:
            if self.nick[-1] == ")":
                nick = unidecode.unidecode(self.nick)
                if nick.endswith("(a completer)") or nick.endswith(
                    "(a remplir)"
                ):
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
            if sheet_visitor.email:
                db_visitor = (
                    s.query(Visitor)
                    .filter_by(email=sheet_visitor.email)
                    .first()
                )
            elif sheet_visitor.first_name and sheet_visitor.last_name:
                db_visitor = (
                    s.query(Visitor)
                    .filter_by(
                        first_name=sheet_visitor.first_name,
                        last_name=sheet_visitor.last_name,
                    )
                    .first()
                )
            else:
                db_visitor = (
                    s.query(Visitor).filter_by(nick=sheet_visitor.nick).first()
                )
            if db_visitor:
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
