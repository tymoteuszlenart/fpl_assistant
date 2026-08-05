"""Normalize official FPL payloads without changing unknown values to zero."""

from dataclasses import dataclass
from typing import Any, Mapping, Optional


@dataclass(frozen=True)
class NormalizedPlayer:
    fpl_player_id: int
    web_name: Optional[str]
    club_id: Optional[int]
    position_id: Optional[int]
    now_cost_tenths: Optional[int]
    availability_status: Optional[str]
    form: Optional[float]
    minutes: Optional[int]


@dataclass(frozen=True)
class NormalizedTeamState:
    fpl_team_id: int
    team_name: Optional[str]
    manager_name: Optional[str]
    overall_points: Optional[int]
    overall_rank: Optional[int]
    bank_tenths: Optional[int]
    free_transfers: Optional[int]


def _integer(value: Any) -> Optional[int]:
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def _decimal(value: Any) -> Optional[float]:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def normalize_player(payload: Mapping[str, Any]) -> NormalizedPlayer:
    player_id = _integer(payload.get("id"))
    if player_id is None:
        raise ValueError("Official player payload is missing an integer id")
    return NormalizedPlayer(
        fpl_player_id=player_id,
        web_name=payload.get("web_name"),
        club_id=_integer(payload.get("team")),
        position_id=_integer(payload.get("element_type")),
        now_cost_tenths=_integer(payload.get("now_cost")),
        availability_status=payload.get("status"),
        form=_decimal(payload.get("form")),
        minutes=_integer(payload.get("minutes")),
    )


def normalize_team_state(team_id: int, payload: Mapping[str, Any]) -> NormalizedTeamState:
    first_name = payload.get("player_first_name")
    last_name = payload.get("player_last_name")
    manager_name = " ".join(part for part in (first_name, last_name) if part) or None
    return NormalizedTeamState(
        fpl_team_id=team_id,
        team_name=payload.get("name"),
        manager_name=manager_name,
        overall_points=_integer(payload.get("summary_overall_points")),
        overall_rank=_integer(payload.get("summary_overall_rank")),
        bank_tenths=_integer(payload.get("last_deadline_bank")),
        free_transfers=_integer(payload.get("transfers_available")),
    )
