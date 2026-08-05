"""Independent legality checks for squads and one-for-one transfer states."""

from collections import Counter
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Optional

from .rulesets import FPLRuleset

POSITION_IDS = {1: "GK", 2: "DEF", 3: "MID", 4: "FWD"}


@dataclass(frozen=True)
class ValidationResult:
    valid: bool
    errors: tuple[str, ...]


def _position(player: Mapping[str, Any]) -> Optional[str]:
    value = player.get("position", player.get("element_type"))
    if isinstance(value, int):
        return POSITION_IDS.get(value)
    return value if value in POSITION_IDS.values() else None


def _player_id(player: Mapping[str, Any]) -> Any:
    return player.get("id", player.get("player_id", player.get("element")))


def validate_squad(
    players: Iterable[Mapping[str, Any]],
    ruleset: FPLRuleset,
    budget_tenths: Optional[int] = None,
) -> ValidationResult:
    """Validate static squad composition, club cap, uniqueness and affordability.

    Player prices must be supplied in integer tenths under ``now_cost`` or
    ``price_tenths``. An omitted price is reported as unknown, never treated as
    zero.
    """
    squad = list(players)
    errors: list[str] = []
    ids = [_player_id(player) for player in squad]
    if any(player_id is None for player_id in ids):
        errors.append("player_id_missing")
    if len(ids) != len(set(ids)):
        errors.append("duplicate_player")
    if len(squad) != ruleset.squad_size:
        errors.append("invalid_squad_size")

    positions = Counter(_position(player) for player in squad)
    if positions.get(None):
        errors.append("unknown_position")
    for position, required_count in ruleset.squad_position_counts.items():
        if positions[position] != required_count:
            errors.append(f"invalid_{position.lower()}_count")

    clubs = [player.get("team", player.get("club_id")) for player in squad]
    if any(club is None for club in clubs):
        errors.append("club_missing")
    elif any(count > ruleset.max_players_per_club for count in Counter(clubs).values()):
        errors.append("club_limit_exceeded")

    if budget_tenths is not None:
        prices = [player.get("now_cost", player.get("price_tenths")) for player in squad]
        if any(not isinstance(price, int) for price in prices):
            errors.append("price_unknown")
        elif sum(prices) > budget_tenths:
            errors.append("budget_exceeded")

    return ValidationResult(valid=not errors, errors=tuple(errors))


def validate_transfer(
    current_squad: Iterable[Mapping[str, Any]],
    outgoing_player_id: Any,
    incoming_player: Mapping[str, Any],
    bank_tenths: Optional[int],
    ruleset: FPLRuleset,
    selling_price_tenths: Optional[int],
) -> ValidationResult:
    """Validate a one-for-one transfer using the manager's known sale price."""
    errors: list[str] = []
    squad = list(current_squad)
    outgoing = next((player for player in squad if _player_id(player) == outgoing_player_id), None)
    if outgoing is None:
        return ValidationResult(False, ("outgoing_player_not_owned",))
    if _player_id(incoming_player) in {_player_id(player) for player in squad}:
        errors.append("incoming_player_already_owned")
    if _position(outgoing) != _position(incoming_player):
        errors.append("position_change_not_allowed")
    if bank_tenths is None:
        errors.append("bank_unknown")
    if selling_price_tenths is None:
        errors.append("selling_price_unknown")
    incoming_cost = incoming_player.get("now_cost", incoming_player.get("price_tenths"))
    if not isinstance(incoming_cost, int):
        errors.append("incoming_price_unknown")
    if not errors and incoming_cost > selling_price_tenths + bank_tenths:
        errors.append("insufficient_funds")

    proposed_squad = [player for player in squad if _player_id(player) != outgoing_player_id]
    proposed_squad.append(incoming_player)
    squad_result = validate_squad(proposed_squad, ruleset)
    errors.extend(squad_result.errors)
    return ValidationResult(valid=not errors, errors=tuple(dict.fromkeys(errors)))
