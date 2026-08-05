from datetime import datetime, timedelta, timezone

from app.services.strategy_service import squad_alerts, strategy_state


def test_strategy_state_distinguishes_used_and_remaining_chips():
    state = strategy_state([{'chip_name': 'wildcard', 'gameweek': 4}])

    chips = {chip['id']: chip['available'] for chip in state['remaining_chips']}
    assert chips['wildcard'] is False
    assert chips['freehit'] is True


def test_alerts_report_stale_data_and_unavailable_owned_players():
    old = (datetime.now(timezone.utc) - timedelta(hours=25)).isoformat()
    alerts = squad_alerts({'refresh_status': 'current'}, {'as_of': old}, [{'fpl_player_id': 8}],
                          [{'id': 8, 'web_name': 'Sample', 'status': 'i', 'news': 'Knee injury'}])

    assert {alert['type'] for alert in alerts} == {'stale_squad', 'player_unavailable'}
