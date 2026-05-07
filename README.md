# Bard Golf — Registration Backend

Django + DRF service that receives Kwekwe Golf Day registration POSTs from the
React frontend and appends each registration as a row to a Google Sheet (in
submission order). The sheet is the single source of truth — the team checks
it directly.

## Endpoints

- `GET  /api/health/` — liveness probe (returns `{"status": "ok"}`)
- `POST /api/register/` — accepts a JSON registration; returns concierge-tone
  thank-you and the sheet reference cell.

## Local setup

```sh
cd C:\Users\PC\documents\bard-golf-backend
python -m venv .venv
.venv\Scripts\activate         # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env         # then edit values
copy <path-to>\service_account.json service_account.json
python manage.py runserver 0.0.0.0:8000
```

## Required environment variables

- `SECRET_KEY` — any 50+ random chars in production
- `GOOGLE_SHEET_ID` — the destination sheet's ID (from its URL)
- `GOOGLE_SHEETS_CREDENTIALS` — path to the service-account JSON, OR
- `GOOGLE_SHEETS_CREDENTIALS_JSON` — the entire JSON inlined (preferred for Render)
- `CORS_ALLOWED_ORIGINS` — comma-separated React origins
- `KWEKWE_TAB_NAME` — defaults to `Kwekwe Registrations`

## Google Sheet setup

1. Create or pick a Google Sheet.
2. Share it with the service-account email (found in the JSON's `client_email`)
   as **Editor**.
3. Set `GOOGLE_SHEET_ID` to the ID in the URL
   (`https://docs.google.com/spreadsheets/d/<THIS-PART>/edit`).
4. The first POST creates the `Kwekwe Registrations` tab and writes a header row
   automatically. Subsequent POSTs append below.

## Deploy on Render

- Web service, Python 3.12
- Build: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
- Start: `gunicorn config.wsgi --bind 0.0.0.0:$PORT --workers 2 --timeout 60`
- Set env vars in the Render dashboard (paste the entire service-account JSON
  into `GOOGLE_SHEETS_CREDENTIALS_JSON`).

## Submission payload

```json
{
  "full_name": "Tendai Moyo",
  "email": "tendai@example.com",
  "phone": "+263 77 123 4567",
  "company": "Acme Holdings",
  "handicap": "12",
  "team_name": "Acme Foursome",
  "player_2_name": "...",
  "player_3_name": "...",
  "player_4_name": "...",
  "tee_preference": "Morning",
  "dietary_requirements": "Vegetarian",
  "special_requests": "..."
}
```

`full_name`, `email`, `phone` are required; everything else is optional.
