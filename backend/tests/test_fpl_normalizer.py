from app.utils.fpl_normalizer import normalize_player, normalize_team_state


def test_normalize_player_preserves_unknown_values():
    player = normalize_player({"id": 12, "web_name": "Sample", "form": "", "now_cost": None})
    assert player.fpl_player_id == 12
    assert player.form is None
    assert player.now_cost_tenths is None
    assert player.minutes is None


def test_normalize_team_state_preserves_unknown_money_and_transfers():
    team = normalize_team_state(123, {"name": "Example", "player_first_name": "Ada"})
    assert team.manager_name == "Ada"
    assert team.bank_tenths is None
    assert team.free_transfers is None
