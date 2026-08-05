"""Versioned FPL rules used by validation and later optimization."""

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class FPLRuleset:
    """The rules required to validate a standard FPL squad and a transfer."""

    id: str
    season: str
    squad_size: int
    squad_position_counts: Mapping[str, int]
    max_players_per_club: int
    initial_budget_tenths: int
    point_cost_per_extra_transfer: int
    max_bank_tenths: int


# Kept as data in one place so a seasonal update does not require changes to
# validation or optimizer code. This is the baseline standard-game ruleset.
STANDARD_2026_V1 = FPLRuleset(
    id="2026-v1",
    season="2026-27",
    squad_size=15,
    squad_position_counts={"GK": 2, "DEF": 5, "MID": 5, "FWD": 3},
    max_players_per_club=3,
    initial_budget_tenths=1000,
    point_cost_per_extra_transfer=4,
    max_bank_tenths=1000,
)

RULESETS = {STANDARD_2026_V1.id: STANDARD_2026_V1}


def get_ruleset(ruleset_id: str = STANDARD_2026_V1.id) -> FPLRuleset:
    """Return a known ruleset or fail explicitly instead of using defaults."""
    try:
        return RULESETS[ruleset_id]
    except KeyError as error:
        raise ValueError(f"Unknown FPL ruleset: {ruleset_id}") from error
