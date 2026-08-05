# FPL Optimization Specification

Status: Draft

Version: 0.1

Last updated: 2026-08-05

## 1. Purpose

This document defines how FPL Assistant turns player projections and a manager's team state into legal, reproducible squad and transfer recommendations.

It covers two related problems:

1. **Squad builder:** choose a complete squad, lineups, captaincy, and bench under a budget.
2. **Transfer planner:** choose a sequence of changes from an existing squad, including the cost of transfers.

The optimizer consumes projections; it does not create them. Prediction quality and optimization correctness must be tested separately.

## 2. Terminology

- **Horizon:** the ordered gameweeks included in a run.
- **Expected points (xP):** mean projected FPL points for a player in a gameweek, including expected minutes.
- **No-transfer baseline:** the best legal lineup and captaincy plan if the squad makes no transfers.
- **Gross gain:** projected points difference before transfer-hit costs.
- **Net gain:** gross gain minus point-hit costs and configured risk penalties.
- **Ruleset:** versioned FPL constraints and chip behavior for a season.
- **Optimal:** solver-proven best feasible solution for the exact inputs and objective.
- **Alternative:** a feasible solution made materially different through explicit diversity constraints.

## 3. Inputs

Every optimization run must store or reference an immutable input bundle:

- tracked team and snapshot, when planning transfers;
- ordered gameweek horizon;
- player pool with club, position, price, and availability;
- manager-specific selling price for owned players when available;
- bank and free-transfer state;
- versioned per-player, per-gameweek xP and risk values;
- versioned ruleset;
- chip state and selected chip mode;
- locked and excluded players or clubs;
- risk profile;
- optimizer version and numeric parameters.

Unknown rules-critical input must not be converted silently to zero. The run must either reject the request or record an explicit fallback assumption.

## 4. Ruleset

Rules vary by FPL season and must be data, not constants scattered through services.

At minimum, a ruleset contains:

- squad position counts;
- starting-XI position minimums and maximums;
- squad size and bench size;
- maximum players per club;
- initial budget;
- free-transfer accumulation and cap rules;
- point cost per additional transfer;
- selling-price rules;
- captain and vice-captain multipliers;
- auto-substitution approximation policy;
- chip inventory and behavior;
- season and effective gameweek range.

The legality validator and optimizer must consume the same ruleset.

## 5. Projection contract

For each eligible player `p` and gameweek `g`, the optimizer receives:

- `xp[p,g]`: mean projected points;
- `expected_minutes[p,g]`;
- `appearance_probability[p,g]`;
- `risk[p,g]`: uncertainty measure on a documented scale;
- fixture count and fixture identifiers;
- availability state and freshness timestamp.

The projection layer must represent blank gameweeks as zero fixtures and double gameweeks as multiple fixture contributions. It must not double-apply expected-minutes adjustments already included in xP.

### Baseline projection model

The first model should be transparent and backtestable. A suitable baseline combines:

- recent and season-long per-90 production with shrinkage for small samples;
- expected minutes based on recent starts, substitutions, and availability;
- opponent strength, home advantage, and fixture count;
- position-specific goal, assist, clean-sheet, save, card, and bonus expectations where data permits.

Official `form` and FDR may be features, but neither should be treated as a calibrated points forecast by itself. Ownership is excluded from expected points.

## 6. Shared decision variables

An implementation may use mixed-integer programming, constraint programming, or another exact method. Conceptually it must model:

- `squad[p,g] ∈ {0,1}`: player is owned for gameweek `g`;
- `start[p,g] ∈ {0,1}`: player is in the starting XI;
- `bench[p,b,g] ∈ {0,1}`: player occupies bench slot `b`;
- `captain[p,g] ∈ {0,1}`;
- `vice_captain[p,g] ∈ {0,1}`;
- `transfer_in[p,g] ∈ {0,1}`;
- `transfer_out[p,g] ∈ {0,1}`;
- `paid_transfers[g] ≥ 0`, integer;
- `bank[g] ≥ 0`.

Chip-specific variables are added only for supported chip modes.

## 7. Legality constraints

### 7.1 Squad

For every gameweek state:

- squad size equals the ruleset squad size;
- each position count equals its required squad count;
- players from any one club do not exceed the club limit;
- unavailable or excluded players are not newly acquired;
- locked players remain present for their lock interval;
- bank never becomes negative.

### 7.2 Starting XI and bench

For every gameweek:

- XI size equals 11 unless the ruleset says otherwise;
- exactly one goalkeeper starts;
- outfield position bounds follow the ruleset;
- every starter and benched player is in the squad;
- every non-starting squad player occupies exactly one bench slot;
- captain and vice-captain are distinct starters;
- exactly one captain and one vice-captain are selected.

The initial version may approximate auto-substitutions with a bench-value factor. The UI must label this approximation. A later version may use appearance scenarios.

### 7.3 Transfers and money

- A player cannot be transferred in and out in the same gameweek.
- Squad state changes equal transfers in minus transfers out.
- Transfer-in count equals transfer-out count outside a squad-resetting chip.
- Money gained from a transfer out uses manager-specific selling price when known.
- Money spent on a transfer in uses the applicable market price for that deadline state.
- Free transfers evolve according to the ruleset.
- Paid transfers equal transfers above those available for free, except under chips that alter transfer cost.

The planner must not assume `now_cost` equals the manager's selling price.

### 7.4 Chips

Wildcard mode removes ordinary transfer-hit costs for the activation gameweek and permits rebuilding the squad, while preserving the budget defined by current selling value plus bank. Other chip semantics must be added to the ruleset and covered by dedicated tests before use.

## 8. Objective

### 8.1 Gameweek squad value

For each gameweek, the objective includes:

- starter xP;
- the captain's additional xP from the captain multiplier;
- a configurable expected bench contribution or scenario-based auto-substitution value;
- optional vice-captain contingency value when captain appearance risk is modeled.

### 8.2 Multi-gameweek objective

The default Balanced objective is:

```text
maximize Σg discount[g] × (
    expected_lineup_points[g]
  + expected_bench_contingency[g]
  - risk_weight × lineup_risk[g]
  - hit_cost[g]
) + terminal_value
```

Where:

- `discount[g]` defaults to 1.0 and may decrease for distant gameweeks;
- `hit_cost[g]` comes from the active ruleset;
- `terminal_value` is a small, bounded estimate of value beyond the horizon;
- `risk_weight` comes from the selected recommendation mode.

The primary reported `net_gain` is the optimized objective's expected-points component minus the no-transfer baseline's equivalent component and point hits. Risk and terminal adjustments must also be shown separately so they do not obscure the points comparison.

### 8.3 Value and ownership

- Price efficiency may be a tie-breaker or terminal-value feature.
- Unspent bank may receive a small bounded value, but must not dominate projected points.
- Ownership is not part of the default expected-points objective.
- Aggressive mode may apply a small, explicit differential preference after projected points and legality. The UI must identify this preference.

## 9. No-transfer baseline

Every transfer-planning run must solve the same lineup and captaincy problem while holding the starting squad fixed and allowing zero transfers. The baseline uses the same horizon, projections, risk profile, and ruleset as candidate plans.

The API must return:

- baseline projected points by gameweek;
- optimized plan projected points by gameweek;
- gross gain;
- point-hit cost;
- net gain;
- risk adjustment and terminal-value adjustment, if used.

A plan should be labelled `recommended` only if it improves the configured objective and passes a configurable minimum net-gain threshold. Otherwise, the primary recommendation is to roll or make no transfer.

## 10. Alternative solutions

After finding the primary solution, the solver should generate alternatives with one or more diversity constraints, such as:

- at least one different transfer;
- at least two different players in a rebuilt squad;
- a different captain;
- a lower hit count;
- a lower-risk solution within a defined xP tolerance.

Alternatives must be sorted by the same objective and must remain legal. Superficially reordered benches do not count as materially distinct alternatives.

## 11. Solver result states

An optimization response has one of these states:

- `optimal`: best solution proven for the exact model;
- `feasible`: valid solution found, optimality not proven within limits;
- `infeasible`: no solution satisfies the constraints;
- `invalid_input`: required inputs are missing or contradictory;
- `timeout`: no usable solution found within the time limit;
- `failed`: unexpected solver or system error.

The UI must not label `feasible` as optimal. Responses include runtime, optimality gap when available, and warnings.

## 12. Reproducibility

Every run records:

- canonicalized request parameters and a request hash;
- snapshot ID;
- projection set ID and model version;
- ruleset version;
- optimizer version;
- solver name and version;
- random seed, if relevant;
- time limit;
- result state and objective components.

The same immutable inputs and deterministic solver configuration should reproduce the same primary result.

## 13. Validation

Optimization output must pass an independent legality validator before being stored or returned. The validator must not reuse the solver's decision constraints as its only implementation.

Required automated tests include:

- exact position counts and squad size;
- club-limit edge cases;
- budget equality and one-unit overspend;
- current price versus selling-price differences;
- zero, one, and accumulated free transfers under each supported ruleset;
- point-hit calculation;
- locked and excluded player conflicts;
- blank and double gameweeks;
- unavailable player handling;
- no-transfer recommendation when no plan clears the threshold;
- wildcard rebuilding;
- infeasible requests;
- alternative diversity;
- stable reproduction from stored inputs.

Property-based tests should generate random player pools and assert that every returned solution is legal.

## 14. Performance limits

Default local limits:

- planning horizon: 1-6 gameweeks;
- ordinary transfer candidates: configurable shortlist per position, with all owned players retained;
- primary solver time limit: 8 seconds;
- alternative generation: 2 additional seconds;
- cached identical request: under 1 second.

Candidate pruning must be deterministic and must retain locked players, owned players, high-projection players, and enough low-price players to preserve feasibility. If pruning can affect optimality, the result is optimal only with respect to the pruned pool and must say so.

## 15. Initial implementation recommendation

Use a well-supported integer optimization library behind a small adapter interface:

```text
ProjectionSet + TeamState + Ruleset + UserConstraints
                         ↓
                  Optimizer adapter
                         ↓
             Result + objective breakdown
                         ↓
              Independent validator
```

Keep current heuristic scores available as exploratory player indicators, but do not use their rank as a substitute for the constrained optimizer.

## 16. Related specifications

- [Product specification](PRODUCT_SPEC.md)
- [Data and API specification](DATA_AND_API_SPEC.md)
