from app.domain import get_ruleset, validate_squad, validate_transfer


RULESET = get_ruleset()


def player(player_id, position, team, cost=50):
    return {"id": player_id, "position": position, "team": team, "now_cost": cost}


def legal_squad():
    positions = ["GK", "GK"] + ["DEF"] * 5 + ["MID"] * 5 + ["FWD"] * 3
    return [player(index + 1, position, (index % 5) + 1) for index, position in enumerate(positions)]


def test_standard_ruleset_is_versioned_and_has_standard_composition():
    assert RULESET.id == "2026-v1"
    assert RULESET.squad_size == 15
    assert RULESET.squad_position_counts == {"GK": 2, "DEF": 5, "MID": 5, "FWD": 3}


def test_legal_squad_passes_validation_at_exact_budget():
    squad = legal_squad()
    assert validate_squad(squad, RULESET, budget_tenths=sum(p["now_cost"] for p in squad)).valid


def test_validator_rejects_club_limit_and_one_tenth_overspend():
    squad = legal_squad()
    for index in range(4):
        squad[index]["team"] = 99
    result = validate_squad(squad, RULESET, budget_tenths=sum(p["now_cost"] for p in squad) - 1)
    assert not result.valid
    assert "club_limit_exceeded" in result.errors
    assert "budget_exceeded" in result.errors


def test_validator_does_not_turn_unknown_price_into_zero():
    squad = legal_squad()
    squad[0].pop("now_cost")
    result = validate_squad(squad, RULESET, budget_tenths=1000)
    assert result.errors == ("price_unknown",)


def test_transfer_uses_selling_price_not_current_outgoing_market_price():
    squad = legal_squad()
    squad[0]["now_cost"] = 100
    incoming = player(99, "GK", 6, cost=106)
    affordable = validate_transfer(squad, 1, incoming, 5, RULESET, selling_price_tenths=105)
    unaffordable = validate_transfer(squad, 1, incoming, 5, RULESET, selling_price_tenths=100)
    assert affordable.valid
    assert "insufficient_funds" in unaffordable.errors


def test_transfer_rejects_unknown_rules_critical_state_and_club_limit():
    squad = legal_squad()
    squad[1]["team"] = squad[2]["team"] = squad[3]["team"] = 6
    incoming = player(100, "GK", 6, cost=50)
    result = validate_transfer(squad, 1, incoming, None, RULESET, selling_price_tenths=None)
    assert "bank_unknown" in result.errors
    assert "selling_price_unknown" in result.errors
    assert "club_limit_exceeded" in result.errors
