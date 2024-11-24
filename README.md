# LAP'admin

The admin web UI for Le LAP, a community-ran hobbyist arcade in Paris.

Production: https://admin.lelap.in

## Requirements

- Python 3.12 or later
- **(Only for importing from Google Sheet)** A Google Service Account
  credentials JSON file placed in `keys/google.json`, see [package
  documentation](https://docs.gspread.org/en/v6.1.3/oauth2.html#for-bots-using-service-account)
  for instructions
- **(Only to force Discord login for private routes)** A Discord client ID and
  token filled as `DISCORD_CLIENT_ID` and `DISCORD_CLIENT_SECRET` in
  `config.yml`

## Running

### Running locally for development

Using the helper script:

```bash
python run.py
```

This take care of creating a virtual environment for you, and runs the app on
port 5000 by default, which you can override with `python run.py --port <PORT>`.

Or instead, do it all manually:

```bash
python -m venv .venv

# Linux / MacOS
source .venv/bin/activate
# Windows
.\.venv\Scripts\activate.bat

pip install -r requirements.txt

# Optional: import visitors from old gsheet data
flask import visitors

# Linux / MacOS
FLASK_APP=app:create_app flask run --debug [-p PORT]
# Windows
set FLASK_APP=app:create_app
flask run --debug [-p PORT]
```

You can now explore the app at http://localhost:5000.

In debug mode, the database is automatically created, but if you modify the
tables, you'll have to create a new migration. Use `flask db migration` to check
what changed, and use `flask db migraiton [your message]` to create the new
migration. Then restart the app to apply it, or run `alembic upgrade head`.

### Running in production

Run database migrations, then serve `app:create_app()` with a WSGI compatible
server.

Real-world example, with gunicorn:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
pip install gunicorn
gunicorn 'app:create_app()' -b 127.0.0.1:5000 -w 4
```

## License

MIT.
