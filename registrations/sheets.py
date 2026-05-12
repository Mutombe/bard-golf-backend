"""Google Sheets writer for Kwekwe Golf Day registrations.

Appends one row per registration in submission order. Tab created lazily
with a header row on first call.
"""
import json
import logging
from datetime import datetime, timezone

import gspread
from django.conf import settings
from google.oauth2.service_account import Credentials


log = logging.getLogger(__name__)

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive',
]

# Column order — keep stable so the spreadsheet stays consistent across deploys.
HEADERS = [
    'Submitted At (UTC)',
    'Event',
    'Full Name',
    'Email',
    'Phone',
    'Company',
    'Handicap',
    'Home Club',
    'Caddy Required',
    'Prize-Giving Attendance',
    'Heard About',
    'Tee Preference',
    'Team Name',
    'Player 2 Name',
    'Player 3 Name',
    'Player 4 Name',
    'Dietary Requirements',
    'Special Requests',
    'Source IP',
    'User Agent',
]


NEWSLETTER_HEADERS = [
    'Subscribed At (UTC)',
    'Email',
    'Source',
    'Source IP',
    'User Agent',
]


_client = None
_spreadsheet = None
_tab = None
_newsletter_tab = None


def _get_credentials() -> Credentials:
    """Resolve service-account credentials from JSON env or file path."""
    raw = settings.GOOGLE_SHEETS_CREDENTIALS_JSON
    if raw:
        info = json.loads(raw)
        return Credentials.from_service_account_info(info, scopes=SCOPES)
    return Credentials.from_service_account_file(
        settings.GOOGLE_SHEETS_CREDENTIALS, scopes=SCOPES
    )


def _get_client():
    global _client
    if _client is None:
        _client = gspread.authorize(_get_credentials())
    return _client


def _get_spreadsheet():
    global _spreadsheet
    if _spreadsheet is None:
        if not settings.GOOGLE_SHEET_ID:
            raise RuntimeError('GOOGLE_SHEET_ID is not configured.')
        _spreadsheet = _get_client().open_by_key(settings.GOOGLE_SHEET_ID)
    return _spreadsheet


def _get_tab():
    global _tab
    if _tab is None:
        ss = _get_spreadsheet()
        existing = {ws.title: ws for ws in ss.worksheets()}
        if settings.KWEKWE_TAB_NAME in existing:
            _tab = existing[settings.KWEKWE_TAB_NAME]
        else:
            _tab = ss.add_worksheet(
                title=settings.KWEKWE_TAB_NAME,
                rows=1000,
                cols=len(HEADERS),
            )
            _tab.update('A1', [HEADERS])
            _tab.format('A1:Z1', {'textFormat': {'bold': True}})
    return _tab


def _get_newsletter_tab():
    """Return (and lazily create) the Newsletter Subscribers tab."""
    global _newsletter_tab
    if _newsletter_tab is None:
        ss = _get_spreadsheet()
        existing = {ws.title: ws for ws in ss.worksheets()}
        if settings.NEWSLETTER_TAB_NAME in existing:
            _newsletter_tab = existing[settings.NEWSLETTER_TAB_NAME]
        else:
            _newsletter_tab = ss.add_worksheet(
                title=settings.NEWSLETTER_TAB_NAME,
                rows=1000,
                cols=len(NEWSLETTER_HEADERS),
            )
            _newsletter_tab.update('A1', [NEWSLETTER_HEADERS])
            _newsletter_tab.format('A1:Z1', {'textFormat': {'bold': True}})
    return _newsletter_tab


def append_newsletter(email: str, source: str = '', source_ip: str = '', user_agent: str = '') -> str:
    """Append one newsletter subscriber row. Returns the updated range string."""
    tab = _get_newsletter_tab()
    subscribed_at = datetime.now(timezone.utc).isoformat(timespec='seconds')
    row = [subscribed_at, email, source, source_ip, user_agent[:500]]
    result = tab.append_row(row, value_input_option='USER_ENTERED')
    updated_range = result.get('updates', {}).get('updatedRange', '')
    log.info('Appended newsletter subscriber: %s', updated_range)
    return updated_range


def append_registration(payload: dict, source_ip: str = '', user_agent: str = '') -> int:
    """Append one registration row. Returns the new row index (1-based)."""
    tab = _get_tab()
    submitted_at = datetime.now(timezone.utc).isoformat(timespec='seconds')
    row = [
        submitted_at,
        payload.get('event', ''),
        payload.get('full_name', ''),
        payload.get('email', ''),
        payload.get('phone', ''),
        payload.get('company', ''),
        payload.get('handicap', ''),
        payload.get('home_club', ''),
        payload.get('caddy', ''),
        payload.get('prize_giving', ''),
        payload.get('heard_about', ''),
        payload.get('tee_preference', ''),
        payload.get('team_name', ''),
        payload.get('player_2_name', ''),
        payload.get('player_3_name', ''),
        payload.get('player_4_name', ''),
        payload.get('dietary_requirements', ''),
        payload.get('special_requests', ''),
        source_ip,
        user_agent[:500],
    ]
    result = tab.append_row(row, value_input_option='USER_ENTERED')
    # gspread returns dict with updates.updatedRange — extract row number for logging
    updated_range = result.get('updates', {}).get('updatedRange', '')
    log.info('Appended registration to sheet: %s', updated_range)
    return updated_range
