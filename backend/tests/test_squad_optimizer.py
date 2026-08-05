from app.services.squad_optimizer import optimize_squad


def _player(player_id, position, team, cost=50):
    return {'id': player_id, 'element_type': position, 'team': team, 'now_cost': cost, 'status': 'a'}


def _pool():
    positions = [1, 1] + [2] * 5 + [3] * 5 + [4] * 3
    return [_player(index + 1, position, (index % 5) + 1) for index, position in enumerate(positions)]


def test_squad_optimizer_returns_legal_xi_and_captain():
    pool = _pool()
    projections = {(player['id'], 1): float(player['id']) for player in pool}

    result = optimize_squad(pool, projections, [1], 750)

    assert result['status'] == 'feasible'
    solution = result['solutions'][0]
    assert len(solution['squad']) == 15
    assert len(solution['lineup']['starter_ids']) == 11
    assert solution['lineup']['captain_id'] in solution['lineup']['starter_ids']
    assert solution['remaining_bank_tenths'] == 0


def test_squad_optimizer_explains_infeasible_locks():
    pool = _pool()
    result = optimize_squad(pool, {}, [1], 750, locked_player_ids=[1], excluded_player_ids=[1])

    assert result['status'] == 'infeasible'
    assert 'cannot be both locked and excluded' in result['warnings'][0]
