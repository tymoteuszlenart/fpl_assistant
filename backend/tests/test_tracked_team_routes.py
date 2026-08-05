from unittest.mock import patch

from app import create_app
from app.utils.fpl_api import FPLAPIError


TEAM = {
    "name": "Fixture Chasers",
    "player_first_name": "Ada",
    "player_last_name": "Lovelace",
    "summary_overall_points": 456,
    "summary_overall_rank": 12345,
    "transfers_available": 2,
}
PICKS = {
    "entry_history": {"bank": 17, "value": 1004, "points": 61, "event_transfers": 1, "event_transfers_cost": 4},
    "picks": [
        {"element": 11, "position": 1, "multiplier": 2, "is_captain": True, "is_vice_captain": False,
         "purchase_price": 50, "selling_price": 51},
        {"element": 12, "position": 2, "multiplier": 1, "is_captain": False, "is_vice_captain": True,
         "purchase_price": 45, "selling_price": 45},
    ],
}
HISTORY = {"current": [{"event": 1, "total_points": 50, "overall_rank": 200000, "points": 50, "bank": 10}]}


def _app(tmp_path):
    return create_app({"TESTING": True, "DATABASE": str(tmp_path / "tracker.sqlite3")})


def _refresh(client):
    with patch("app.routes.tracked_team_routes.FPLAPIClient.get_current_gameweek", return_value=2), \
         patch("app.routes.tracked_team_routes.FPLAPIClient.get_team_data", return_value=TEAM), \
         patch("app.routes.tracked_team_routes.FPLAPIClient.get_team_picks", return_value=PICKS), \
         patch("app.routes.tracked_team_routes.FPLAPIClient.get_team_history", return_value=HISTORY):
        return client.post("/api/tracked-teams/99/refresh")


def test_refresh_creates_current_and_historical_snapshots(tmp_path):
    client = _app(tmp_path).test_client()

    response = _refresh(client)

    assert response.status_code == 200
    assert response.get_json()["team"]["refresh_status"] == "current"
    snapshots = client.get("/api/tracked-teams/99/snapshots").get_json()["snapshots"]
    assert [snapshot["gameweek"] for snapshot in snapshots] == [2, 1]
    assert snapshots[0]["import_status"] == "complete"
    assert snapshots[1]["warnings"] == ["Historical picks were not imported."]


def test_refresh_is_idempotent_for_same_gameweek(tmp_path):
    client = _app(tmp_path).test_client()

    _refresh(client)
    _refresh(client)

    assert len(client.get("/api/tracked-teams/99/snapshots").get_json()["snapshots"]) == 2


def test_snapshot_changes_require_two_complete_squad_imports(tmp_path):
    app = _app(tmp_path)
    client = app.test_client()
    _refresh(client)
    next_picks = {**PICKS, "picks": [{**PICKS["picks"][0], "element": 13}]}
    with patch("app.routes.tracked_team_routes.FPLAPIClient.get_current_gameweek", return_value=3), \
         patch("app.routes.tracked_team_routes.FPLAPIClient.get_team_data", return_value=TEAM), \
         patch("app.routes.tracked_team_routes.FPLAPIClient.get_team_picks", return_value=next_picks), \
         patch("app.routes.tracked_team_routes.FPLAPIClient.get_team_history", return_value=HISTORY):
        client.post("/api/tracked-teams/99/refresh")

    changes = client.get("/api/tracked-teams/99/snapshots/3/changes").get_json()
    assert changes == {"available": True, "from_gameweek": 2, "to_gameweek": 3,
                       "transferred_in": [13], "transferred_out": [11, 12]}


def test_failed_refresh_records_freshness_error(tmp_path):
    client = _app(tmp_path).test_client()
    with patch("app.routes.tracked_team_routes.FPLAPIClient.get_current_gameweek", side_effect=FPLAPIError("Unavailable")):
        response = client.post("/api/tracked-teams/99/refresh")

    assert response.status_code == 502
    team = client.get("/api/tracked-teams/99").get_json()
    assert team["refresh_status"] == "failed"
    assert team["refresh_error"] == "Unavailable"
