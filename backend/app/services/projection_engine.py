"""Transparent, versioned baseline projections from official FPL fields."""

from collections import defaultdict
from typing import Any, Dict, Iterable, List


def build_baseline_projections(players: Iterable[Dict[str, Any]], fixtures: Iterable[Dict[str, Any]], gameweeks: List[int]):
    """Use official form, availability, and FDR as an auditable interim model.

    ``form`` is FPL's recent points per match. It is adjusted independently for
    each fixture, so blank and double gameweeks naturally receive zero and two
    fixture contributions respectively.
    """
    by_team_gw = defaultdict(list)
    for fixture in fixtures:
        gameweek = fixture.get('event')
        if gameweek in gameweeks:
            by_team_gw[(fixture.get('team_h'), gameweek)].append(fixture.get('team_h_difficulty'))
            by_team_gw[(fixture.get('team_a'), gameweek)].append(fixture.get('team_a_difficulty'))
    warnings, result = [], []
    for player in players:
        player_id, team_id = player.get('id'), player.get('team')
        if not isinstance(player_id, int) or not isinstance(team_id, int):
            continue
        try:
            form = float(player.get('form'))
        except (TypeError, ValueError):
            form = 0.0
            warnings.append(f"Player {player_id} has no official form; a zero baseline was used.")
        chance = player.get('chance_of_playing_next_round')
        availability = 1.0 if player.get('status') == 'a' else (chance / 100 if isinstance(chance, int) else 0.0)
        for gameweek in gameweeks:
            difficulties = [value for value in by_team_gw[(team_id, gameweek)] if isinstance(value, int)]
            fixture_count = len(difficulties)
            fdr_multiplier = sum(1 + (3 - difficulty) * 0.1 for difficulty in difficulties)
            expected_points = round(form * availability * fdr_multiplier, 3)
            result.append({
                'fpl_player_id': player_id, 'gameweek': gameweek, 'expected_points': expected_points,
                'expected_minutes': round(90 * availability * fixture_count, 1),
                'appearance_probability': availability if fixture_count else 0.0,
                'risk': round(1 - availability, 3), 'fixture_count': fixture_count,
                'components': {'official_form': form, 'availability': availability, 'fdr_multiplier': round(fdr_multiplier, 3)},
            })
    return result, sorted(set(warnings))
