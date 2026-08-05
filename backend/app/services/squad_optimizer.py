"""Deterministic, constraint-aware full-squad builder for initial and wildcard modes."""

from collections import Counter
from typing import Any, Dict, Iterable, List, Mapping

from app.domain import get_ruleset, validate_squad
from app.services.transfer_planner import _best_lineup, _position


def _ranked_states(states, limit=800):
    # A modest price term keeps affordable paths alive in the bounded beam.
    return sorted(states, key=lambda state: (state['score'] - state['cost'] * 0.025, -state['cost']), reverse=True)[:limit]


def _build_squad(players: List[Mapping[str, Any]], values, budget: int, locked_ids, excluded_ids, diversity_ids=frozenset()):
    ruleset = get_ruleset()
    player_by_id = {player['id']: player for player in players if isinstance(player.get('id'), int)}
    locks = [player_by_id[player_id] for player_id in locked_ids if player_id in player_by_id]
    if len(locks) != len(locked_ids):
        return None, ['One or more locked players are unavailable in the player pool.']
    if set(locked_ids) & set(excluded_ids):
        return None, ['A player cannot be both locked and excluded.']
    if any(player.get('status') != 'a' for player in locks):
        return None, ['Unavailable players cannot be locked into a new squad.']
    if any(not isinstance(player.get('now_cost'), int) for player in locks):
        return None, ['Locked players must have known prices.']
    position_counts, clubs = Counter(_position(player) for player in locks), Counter(player.get('team') for player in locks)
    if any(position_counts[position] > count for position, count in ruleset.squad_position_counts.items()) or any(count > ruleset.max_players_per_club for count in clubs.values()):
        return None, ['Locked players violate squad composition or club limits.']
    if sum(player.get('now_cost', 0) for player in locks) > budget:
        return None, ['Locked players exceed the available budget.']
    states = [{'ids': tuple(player['id'] for player in locks), 'cost': sum(player['now_cost'] for player in locks),
               'score': sum(values.get(player['id'], 0) for player in locks), 'clubs': clubs, 'positions': position_counts}]
    for position, required_count in ruleset.squad_position_counts.items():
        additions = required_count - position_counts[position]
        candidates = [player for player in players if _position(player) == position and player.get('status') == 'a'
                      and player['id'] not in excluded_ids and player['id'] not in locked_ids]
        # Keep all cheap players and the strongest projected choices; the beam still validates all constraints.
        candidates = list({player['id']: player for player in (sorted(candidates, key=lambda player: player.get('now_cost', 10**9))[:40]
                     + sorted(candidates, key=lambda player: values.get(player['id'], 0), reverse=True)[:80])}.values())
        for _ in range(additions):
            next_states = []
            for state in states:
                for player in candidates:
                    price, club = player.get('now_cost'), player.get('team')
                    if player['id'] in state['ids'] or not isinstance(price, int) or club is None:
                        continue
                    if state['cost'] + price > budget or state['clubs'][club] >= ruleset.max_players_per_club:
                        continue
                    next_states.append({'ids': state['ids'] + (player['id'],), 'cost': state['cost'] + price,
                                        'score': state['score'] + values.get(player['id'], 0),
                                        'clubs': state['clubs'] + Counter([club]),
                                        'positions': state['positions'] + Counter([position])})
            states = _ranked_states(next_states)
            if not states:
                return None, ['No legal squad can be constructed within the budget and constraints.']
    ranked = sorted(states, key=lambda state: (state['score'], -state['cost']), reverse=True)
    for state in ranked:
        if diversity_ids and not (set(state['ids']) - diversity_ids):
            continue
        squad = [player_by_id[player_id] for player_id in state['ids']]
        if validate_squad(squad, ruleset, budget).valid:
            return squad, []
    return None, ['No legal squad remains after applying the requested diversity constraint.']


def optimize_squad(players: Iterable[Mapping[str, Any]], projection_values, gameweeks: List[int], budget_tenths: int,
                   locked_player_ids=None, excluded_player_ids=None, alternative_count=0):
    if not isinstance(budget_tenths, int) or budget_tenths < 0:
        return {'status': 'invalid_input', 'warnings': ['budget_tenths must be a non-negative integer.']}
    locks, exclusions = set(locked_player_ids or []), set(excluded_player_ids or [])
    pool = list(players)
    values = {player.get('id'): round(sum(projection_values.get((player.get('id'), gameweek), 0) for gameweek in gameweeks), 3) for player in pool}
    squad, warnings = _build_squad(pool, values, budget_tenths, locks, exclusions)
    if not squad:
        return {'status': 'infeasible', 'warnings': warnings, 'solutions': []}
    solutions = []
    for rank in range(1, max(0, alternative_count) + 2):
        if rank > 1:
            squad, alternative_warning = _build_squad(pool, values, budget_tenths, locks, exclusions, {player['id'] for player in solutions[0]['squad']})
            if not squad:
                if alternative_warning:
                    warnings.extend(alternative_warning)
                break
        lineup = _best_lineup(squad, values)
        solutions.append({'rank': rank, 'squad': [{'player_id': player['id'], 'price_tenths': player['now_cost']} for player in squad],
                          'projected_points': lineup['projected_points'], 'remaining_bank_tenths': budget_tenths - sum(player['now_cost'] for player in squad),
                          'lineup': lineup, 'validation_status': 'valid'})
    return {'status': 'feasible', 'warnings': sorted(set(warnings + ['Bounded-beam optimizer; solution is feasible but not proven optimal.'])), 'solutions': solutions}
