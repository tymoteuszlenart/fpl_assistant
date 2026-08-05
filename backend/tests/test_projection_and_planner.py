from app.services.projection_engine import build_baseline_projections
from app.services.transfer_planner import plan_one_transfer


def _player(player_id, position, team, form=2.0, cost=50):
    return {'id': player_id, 'element_type': position, 'team': team, 'form': str(form), 'now_cost': cost, 'status': 'a'}


def _squad():
    positions = [1, 1] + [2] * 5 + [3] * 5 + [4] * 3
    return [_player(index + 1, position, (index % 5) + 1) for index, position in enumerate(positions)]


def test_baseline_projection_represents_blank_and_double_gameweeks():
    projections, warnings = build_baseline_projections(
        [_player(1, 3, 10, form=5)],
        [{'event': 1, 'team_h': 10, 'team_a': 20, 'team_h_difficulty': 2, 'team_a_difficulty': 4},
         {'event': 1, 'team_h': 30, 'team_a': 10, 'team_h_difficulty': 3, 'team_a_difficulty': 2}],
        [1, 2],
    )
    by_gameweek = {item['gameweek']: item for item in projections}
    assert by_gameweek[1]['fixture_count'] == 2
    assert by_gameweek[1]['expected_points'] > 5
    assert by_gameweek[2]['fixture_count'] == 0
    assert by_gameweek[2]['expected_points'] == 0
    assert warnings == []


def test_planner_reports_no_transfer_baseline_and_net_gain():
    squad = _squad()
    incoming = _player(99, 1, 6, form=10, cost=51)
    picks = [{'fpl_player_id': player['id'], 'selling_price_tenths': player['now_cost'], 'squad_position': index + 1}
             for index, player in enumerate(squad)]
    values = {(player['id'], 1): float(player['id']) for player in squad}
    values[(99, 1)] = 30

    result = plan_one_transfer({'bank_tenths': 5, 'free_transfers': 1}, picks, squad + [incoming], values, [1])

    assert result['status'] == 'optimal'
    best = result['solutions'][0]
    assert best['hit_cost'] == 0
    assert best['gross_gain'] == best['net_gain']
    assert best['transfers'][0]['in_player_id'] == 99
