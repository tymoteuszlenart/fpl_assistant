"""Deterministic one-transfer planner built on the shared legality validator."""

from collections import defaultdict
from typing import Any, Dict, Iterable, List, Mapping

from app.domain import get_ruleset, validate_transfer


def _position(player):
    return {1: 'GK', 2: 'DEF', 3: 'MID', 4: 'FWD'}.get(player.get('element_type', player.get('position')))


def _best_lineup(players: Iterable[Mapping[str, Any]], values: Mapping[int, float]):
    grouped = defaultdict(list)
    for player in players:
        grouped[_position(player)].append(player)
    for position, required in {'GK': 1, 'DEF': 3, 'MID': 2, 'FWD': 1}.items():
        if len(grouped[position]) < required:
            return None
    for players_in_position in grouped.values():
        players_in_position.sort(key=lambda player: values.get(player['id'], 0), reverse=True)
    best = None
    for defenders in range(3, min(5, len(grouped['DEF'])) + 1):
        for midfielders in range(2, min(5, len(grouped['MID'])) + 1):
            forwards = 10 - defenders - midfielders
            if not 1 <= forwards <= min(3, len(grouped['FWD'])):
                continue
            eleven = grouped['GK'][:1] + grouped['DEF'][:defenders] + grouped['MID'][:midfielders] + grouped['FWD'][:forwards]
            score = sum(values.get(player['id'], 0) for player in eleven)
            captain = max(eleven, key=lambda player: values.get(player['id'], 0))
            score += values.get(captain['id'], 0)
            if best is None or score > best['projected_points']:
                best = {'projected_points': round(score, 3), 'starter_ids': [player['id'] for player in eleven], 'captain_id': captain['id']}
    return best


def plan_one_transfer(snapshot: Mapping[str, Any], picks: List[Mapping[str, Any]], player_pool: List[Mapping[str, Any]], projection_values, gameweeks: List[int], overrides=None):
    """Return the no-transfer baseline and all improving legal one-transfer plans."""
    overrides = overrides or {}
    players = {player.get('id'): player for player in player_pool if isinstance(player.get('id'), int)}
    owned = []
    selling_prices = {}
    for pick in picks:
        player = players.get(pick['fpl_player_id'])
        if player:
            owned.append(player)
            selling_prices[player['id']] = pick.get('selling_price_tenths')
    bank = overrides.get('bank_tenths', snapshot.get('bank_tenths'))
    free_transfers = overrides.get('free_transfers', snapshot.get('free_transfers'))
    if not isinstance(bank, int) or not isinstance(free_transfers, int):
        return {'status': 'invalid_input', 'warnings': ['Bank or free transfers are unknown; provide an override.']}
    values = {player_id: round(sum(projection_values.get((player_id, gameweek), 0) for gameweek in gameweeks), 3) for player_id in players}
    baseline = _best_lineup(owned, values)
    if not baseline:
        return {'status': 'invalid_input', 'warnings': ['The tracked snapshot does not contain a legal squad.']}
    ruleset = get_ruleset()
    owned_ids, candidates = {player['id'] for player in owned}, []
    for outgoing in owned:
        sale_price = overrides.get('selling_prices_tenths', {}).get(str(outgoing['id']), selling_prices[outgoing['id']])
        for incoming in player_pool:
            if incoming.get('id') in owned_ids or incoming.get('status') != 'a' or _position(incoming) != _position(outgoing):
                continue
            if not validate_transfer(owned, outgoing['id'], incoming, bank, ruleset, sale_price).valid:
                continue
            replacement = [incoming if player['id'] == outgoing['id'] else player for player in owned]
            lineup = _best_lineup(replacement, values)
            if not lineup:
                continue
            hit_cost = max(0, 1 - free_transfers) * ruleset.point_cost_per_extra_transfer
            gross_gain = round(lineup['projected_points'] - baseline['projected_points'], 3)
            net_gain = round(gross_gain - hit_cost, 3)
            candidates.append({'transfers': [{'gameweek': gameweeks[0], 'out_player_id': outgoing['id'], 'in_player_id': incoming['id'],
                                               'sell_price_tenths': sale_price, 'buy_price_tenths': incoming.get('now_cost')}],
                               'projected_points': lineup['projected_points'], 'gross_gain': gross_gain, 'hit_cost': hit_cost,
                               'net_gain': net_gain, 'lineup': lineup, 'remaining_bank_tenths': bank + sale_price - incoming['now_cost']})
    candidates.sort(key=lambda candidate: (candidate['net_gain'], candidate['gross_gain']), reverse=True)
    return {'status': 'optimal', 'baseline': baseline, 'solutions': candidates,
            'warnings': ['Initial planner evaluates no-transfer and one-transfer plans only.']}
