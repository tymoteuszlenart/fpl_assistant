"""Phase 4 strategy state: remaining chips and actionable squad alerts."""

from datetime import datetime, timezone
from typing import Any, Dict, Iterable, Mapping


CHIPS = {'wildcard': 'Wildcard', 'freehit': 'Free Hit', 'bboost': 'Bench Boost', '3xc': 'Triple Captain'}


def strategy_state(used_chips):
    used = {chip['chip_name'] for chip in used_chips}
    return {'used_chips': used_chips, 'remaining_chips': [
        {'id': chip_id, 'name': label, 'available': chip_id not in used} for chip_id, label in CHIPS.items()
    ]}


def squad_alerts(team: Mapping[str, Any], snapshot: Mapping[str, Any], picks: Iterable[Mapping[str, Any]], players: Iterable[Mapping[str, Any]], now=None):
    now = now or datetime.now(timezone.utc)
    alerts = []
    if team.get('refresh_status') == 'failed':
        alerts.append({'type': 'refresh_failed', 'severity': 'warning', 'message': team.get('refresh_error') or 'The last refresh failed.'})
    as_of = snapshot.get('as_of') if snapshot else None
    try:
        age_hours = (now - datetime.fromisoformat(as_of)).total_seconds() / 3600
        if age_hours > 24:
            alerts.append({'type': 'stale_squad', 'severity': 'warning', 'message': f'Squad data is {round(age_hours)} hours old; refresh before planning.'})
    except (TypeError, ValueError):
        alerts.append({'type': 'freshness_unknown', 'severity': 'info', 'message': 'Squad freshness is unknown.'})
    owned_ids = {pick['fpl_player_id'] for pick in picks}
    for player in players:
        if player.get('id') in owned_ids and player.get('status') != 'a':
            news = player.get('news') or 'Availability is uncertain.'
            alerts.append({'type': 'player_unavailable', 'severity': 'warning', 'player_id': player['id'],
                           'message': f"{player.get('web_name', 'A squad player')} is unavailable: {news}"})
    return alerts
