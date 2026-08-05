# FPL Assistant Data and API Specification

Status: Draft

Version: 0.1

Last updated: 2026-08-05

## 1. Purpose

This specification defines the persistent data model and HTTP contracts required for squad tracking, projections, squad optimization, and transfer planning.

The first implementation may use SQLite locally. The schema and service boundaries should remain portable to PostgreSQL.

## 2. Design principles

- Preserve raw source meaning: unknown is not zero.
- Keep historical snapshots immutable after a gameweek is finalized.
- Version rules, projections, and optimizer results.
- Make imports idempotent.
- Keep official-source data separate from calculated data and user overrides.
- Store enough input metadata to reproduce every recommendation.
- Return explicit freshness, warning, and solver status fields.

## 3. Data sources

### Official public FPL API

The existing client uses these public endpoints:

- `/bootstrap-static/`: seasons' gameweeks, clubs, players, positions, and current player state;
- `/fixtures/`: fixtures, results, and official fixture difficulty;
- `/entry/{team_id}/`: public team summary;
- `/entry/{team_id}/event/{gameweek}/picks/`: squad picks and gameweek entry state;
- `/entry/{team_id}/history/`: gameweek history and chip history, to be added;
- `/element-summary/{player_id}/`: player fixture and match history, to be added.

Upstream fields and endpoint availability can change. Provider responses must pass through an adapter and normalized validation layer before domain services consume them.

### Optional supplementary data

Expected-minutes, injury-news, and expected-stat sources may be added later. Every stored value must retain `source`, `source_recorded_at`, and licensing/provenance metadata where applicable.

## 4. Persistence model

Identifiers may be UUIDs internally. Official FPL identifiers are stored in separate clearly named columns.

### 4.1 `rulesets`

Versioned rules used by validation and optimization.

| Field | Type | Notes |
|---|---|---|
| `id` | text PK | Stable version, for example `2026-v1`. |
| `season` | text | FPL season identifier. |
| `effective_from_gw` | integer | Inclusive. |
| `effective_to_gw` | integer nullable | Inclusive. |
| `rules_json` | JSON | Position, budget, club, transfer, captaincy, bench, and chip rules. |
| `created_at` | timestamp | UTC. |

### 4.2 `tracked_teams`

| Field | Type | Notes |
|---|---|---|
| `id` | UUID PK | Internal ID. |
| `fpl_team_id` | integer unique | Public official Team ID. |
| `team_name` | text nullable | Last imported name. |
| `manager_name` | text nullable | Last imported public manager name. |
| `season` | text | Prevents cross-season ambiguity. |
| `created_at` | timestamp | UTC. |
| `last_refresh_at` | timestamp nullable | Last attempted refresh. |
| `last_successful_refresh_at` | timestamp nullable | Last complete or usable partial refresh. |
| `refresh_status` | enum | `never`, `current`, `partial`, `failed`. |
| `refresh_error` | text nullable | Safe user-facing summary. |

A later account system may add ownership through a join table without changing the FPL Team ID.

### 4.3 `team_snapshots`

One canonical snapshot per tracked team, season, and gameweek.

| Field | Type | Notes |
|---|---|---|
| `id` | UUID PK | Snapshot ID. |
| `tracked_team_id` | UUID FK | Parent team. |
| `gameweek` | integer | Official gameweek. |
| `as_of` | timestamp | Source observation time. |
| `deadline_time` | timestamp nullable | Official deadline. |
| `is_final` | boolean | True once results/state are no longer expected to change. |
| `overall_points` | integer nullable | Season total. |
| `overall_rank` | integer nullable | Overall rank. |
| `gameweek_points` | integer nullable | Before or after hits according to a documented field mapping. |
| `bank_tenths` | integer nullable | Store official money units exactly. |
| `team_value_tenths` | integer nullable | When public data supplies it. |
| `free_transfers` | integer nullable | Never inferred silently. |
| `gameweek_transfer_count` | integer nullable | Public history when available. |
| `gameweek_transfer_cost` | integer nullable | Point cost. |
| `active_chip` | text nullable | Normalized chip identifier. |
| `source_payload_hash` | text | Detect source changes and support idempotency. |
| `import_status` | enum | `complete`, `partial`. |
| `warnings_json` | JSON | Missing or inferred field warnings. |
| `created_at` | timestamp | UTC. |
| `updated_at` | timestamp | UTC; final snapshots do not change except by repair migration. |

Unique constraint: `(tracked_team_id, season, gameweek)`.

### 4.4 `squad_picks`

| Field | Type | Notes |
|---|---|---|
| `snapshot_id` | UUID FK | Composite PK component. |
| `fpl_player_id` | integer | Composite PK component. |
| `squad_position` | integer | Official pick order. |
| `multiplier` | integer | Official scoring multiplier. |
| `is_captain` | boolean | Imported. |
| `is_vice_captain` | boolean | Imported. |
| `purchase_price_tenths` | integer nullable | When supplied. |
| `selling_price_tenths` | integer nullable | Required for exact transfer planning. |

### 4.5 `player_snapshots`

A normalized historical copy of relevant player state at an observation time.

| Field | Type | Notes |
|---|---|---|
| `id` | UUID PK | Internal ID. |
| `fpl_player_id` | integer | Official ID. |
| `season` | text | Season. |
| `gameweek` | integer | Associated gameweek. |
| `as_of` | timestamp | Observation time. |
| `club_id` | integer | Official club ID. |
| `position` | enum | `GK`, `DEF`, `MID`, `FWD`. |
| `price_tenths` | integer | Exact official unit. |
| `status` | text nullable | Official availability state. |
| `news` | text nullable | Official player news. |
| `news_added_at` | timestamp nullable | Source timestamp. |
| `chance_next_round` | integer nullable | Percentage when supplied. |
| `minutes` | integer nullable | Season-to-date official value. |
| `total_points` | integer nullable | Season-to-date. |
| `form` | decimal nullable | Official form. |
| `selected_percent` | decimal nullable | Official ownership. |
| `stats_json` | JSON | Remaining normalized features. |
| `source_payload_hash` | text | Deduplication. |

Index: `(season, gameweek, fpl_player_id, as_of)`.

### 4.6 `fixtures`

| Field | Type | Notes |
|---|---|---|
| `fpl_fixture_id` | integer PK | Official fixture ID. |
| `season` | text | Season. |
| `gameweek` | integer nullable | Null for unscheduled fixture. |
| `home_club_id` | integer | Official ID. |
| `away_club_id` | integer | Official ID. |
| `kickoff_time` | timestamp nullable | UTC. |
| `status` | enum | `scheduled`, `started`, `finished`, `postponed`, `unknown`. |
| `home_difficulty` | integer nullable | Official FDR. |
| `away_difficulty` | integer nullable | Official FDR. |
| `source_updated_at` | timestamp | UTC. |

### 4.7 `projection_sets` and `player_projections`

`projection_sets` identifies one immutable generation run:

| Field | Type | Notes |
|---|---|---|
| `id` | UUID PK | Projection-set ID. |
| `season` | text | Season. |
| `generated_at` | timestamp | UTC. |
| `model_version` | text | Reproducible model identifier. |
| `feature_data_as_of` | timestamp | Latest input cutoff. |
| `parameters_json` | JSON | Model configuration. |
| `status` | enum | `complete`, `partial`, `failed`. |
| `warnings_json` | JSON | Coverage warnings. |

`player_projections` contains:

| Field | Type | Notes |
|---|---|---|
| `projection_set_id` | UUID FK | Composite PK component. |
| `fpl_player_id` | integer | Composite PK component. |
| `gameweek` | integer | Composite PK component. |
| `expected_points` | decimal | Includes expected minutes. |
| `expected_minutes` | decimal | 0-90+ for doubles as documented. |
| `appearance_probability` | decimal | 0-1. |
| `risk` | decimal | Documented model scale. |
| `fixture_count` | integer | Supports blanks and doubles. |
| `components_json` | JSON | Explainable projection components. |

### 4.8 `optimization_runs`

| Field | Type | Notes |
|---|---|---|
| `id` | UUID PK | Run ID. |
| `kind` | enum | `squad_builder`, `transfer_plan`, `wildcard`. |
| `tracked_team_id` | UUID nullable | Required for transfer plans. |
| `snapshot_id` | UUID nullable | Starting state. |
| `projection_set_id` | UUID FK | Input projections. |
| `ruleset_id` | text FK | Input rules. |
| `request_json` | JSON | Canonical request. |
| `request_hash` | text | Cache and idempotency key. |
| `optimizer_version` | text | Code/model version. |
| `solver_name` | text | Solver implementation. |
| `solver_version` | text | Solver version. |
| `status` | enum | From the optimization specification. |
| `objective_value` | decimal nullable | Full solver objective. |
| `runtime_ms` | integer nullable | Runtime. |
| `optimality_gap` | decimal nullable | When available. |
| `warnings_json` | JSON | Assumptions and pruning. |
| `created_at` | timestamp | UTC. |

### 4.9 `optimization_solutions`

One run has a primary solution and zero or more alternatives.

| Field | Type | Notes |
|---|---|---|
| `id` | UUID PK | Solution ID. |
| `run_id` | UUID FK | Parent run. |
| `rank` | integer | `1` is primary. |
| `is_recommended` | boolean | May be false when no-transfer is best. |
| `gross_gain` | decimal nullable | Versus baseline. |
| `hit_cost` | integer | FPL points. |
| `net_gain` | decimal nullable | Versus baseline. |
| `risk_adjustment` | decimal | Report separately. |
| `terminal_adjustment` | decimal | Report separately. |
| `remaining_bank_tenths` | integer | Final bank. |
| `solution_json` | JSON | Squads, moves, lineups, captaincy, and per-GW breakdown. |
| `validation_status` | enum | `valid`, `invalid`, `not_run`. |
| `stale_at` | timestamp nullable | When invalidated by changed inputs. |
| `stale_reasons_json` | JSON | Human-readable reasons. |

Normalized move and lineup tables may be added when query requirements justify them. The immutable JSON is the reproducibility record.

### 4.10 `user_overrides`

| Field | Type | Notes |
|---|---|---|
| `id` | UUID PK | Override ID. |
| `tracked_team_id` | UUID FK | Team. |
| `effective_gameweek` | integer | Start gameweek. |
| `field` | enum | Initially `free_transfers`, `bank_tenths`, or player `selling_price_tenths`. |
| `fpl_player_id` | integer nullable | Required for player field. |
| `value_json` | JSON | Validated value. |
| `reason` | text nullable | User note. |
| `created_at` | timestamp | UTC. |

Overrides never overwrite imported source values; input resolution records which value won.

## 5. Import behavior

### 5.1 Track a team

1. Validate Team ID format and fetch the public entry.
2. Upsert `tracked_teams` by Team ID and season.
3. Fetch current gameweek picks and public history.
4. Upsert snapshots using source hashes.
5. Import picks transactionally with each snapshot.
6. Return the most recent usable snapshot even if optional history calls fail.

### 5.2 Refresh a team

- Refresh is idempotent.
- A failed upstream call must not delete or replace the last good data.
- Current, not-final snapshots may be updated.
- Final snapshots are immutable except through an explicit repair migration.
- A partial import lists missing fields and endpoints.
- Changed snapshot, fixture, player, projection, or ruleset inputs mark dependent solutions stale.

### 5.3 Historical comparison

Differences between consecutive snapshots are derived, not treated as the source of truth. Match transferred-out and transferred-in players by snapshot membership. Official transfer counts and costs are retained separately and may reveal wildcard or chip behavior.

## 6. API conventions

- Base path for new contracts: `/api/v1`.
- JSON field names use `snake_case`.
- Money uses integer tenths in machine fields; formatted millions are a presentation concern.
- Timestamps use UTC ISO 8601.
- IDs are strings in JSON except official integer IDs.
- Unknown optional fields are `null`, not `0` or empty strings.
- Validation failures return `400`; missing resources `404`; upstream temporary failures `502` or `503`; internal failures `500`.
- Error bodies follow:

```json
{
  "error": {
    "code": "missing_team_state",
    "message": "Selling prices are unavailable for three owned players.",
    "details": {},
    "retryable": false
  }
}
```

Current unversioned endpoints remain temporarily available as legacy read-only endpoints. New frontend work uses `/api/v1`.

## 7. Tracking endpoints

### `POST /api/v1/tracked-teams`

Create or return a tracked team and perform the first import.

Request:

```json
{ "fpl_team_id": 123456 }
```

Response: `201 Created` for a new record or `200 OK` if already tracked.

```json
{
  "tracked_team": {
    "id": "team_uuid",
    "fpl_team_id": 123456,
    "team_name": "Example XI",
    "season": "2026-27",
    "refresh_status": "current",
    "last_successful_refresh_at": "2026-08-05T10:00:00Z"
  },
  "latest_snapshot_id": "snapshot_uuid",
  "warnings": []
}
```

### `GET /api/v1/tracked-teams`

List tracked teams with latest snapshot summaries.

### `GET /api/v1/tracked-teams/{tracked_team_id}`

Return team identity, refresh state, latest snapshot summary, and active stale warnings.

### `POST /api/v1/tracked-teams/{tracked_team_id}/refresh`

Refresh official team, player, and fixture data. The initial local implementation may run synchronously and return `200`. A later job-backed implementation may return `202` with a job resource.

### `GET /api/v1/tracked-teams/{tracked_team_id}/snapshots`

Return paginated snapshot summaries, newest first.

Query parameters: `from_gameweek`, `to_gameweek`, `cursor`, `limit`.

### `GET /api/v1/tracked-teams/{tracked_team_id}/snapshots/{gameweek}`

Return snapshot, squad picks, resolved money state, source freshness, and warnings.

### `GET /api/v1/tracked-teams/{tracked_team_id}/changes`

Return derived changes between two snapshots.

Query parameters: `from_gameweek` and `to_gameweek`.

```json
{
  "from_gameweek": 3,
  "to_gameweek": 4,
  "players_out": [{"fpl_player_id": 1, "name": "Player A"}],
  "players_in": [{"fpl_player_id": 2, "name": "Player B"}],
  "bank_change_tenths": 5,
  "rank_change": -1200,
  "warnings": []
}
```

## 8. Projection endpoints

### `GET /api/v1/projections/latest`

Return projection-set metadata and coverage, not the entire player matrix by default.

### `GET /api/v1/projections/latest/players`

Query parameters: `gameweeks`, `position`, `club_id`, `fpl_player_ids`, `available_only`, `cursor`, `limit`.

### `POST /api/v1/projections/refresh`

Administrative/local action that generates a new immutable projection set. This endpoint must not be publicly writable without authorization in a deployed environment.

## 9. Optimization endpoints

### `POST /api/v1/optimizations/squad`

Build a new squad without a tracked-team starting state.

```json
{
  "budget_tenths": 1000,
  "gameweeks": [1, 2, 3, 4],
  "risk_profile": "balanced",
  "locked_player_ids": [],
  "excluded_player_ids": [],
  "excluded_club_ids": [],
  "alternative_count": 3,
  "time_limit_ms": 8000
}
```

### `POST /api/v1/tracked-teams/{tracked_team_id}/optimizations/transfers`

Plan changes from the latest snapshot or an explicit snapshot.

```json
{
  "snapshot_id": "snapshot_uuid",
  "gameweeks": [4, 5, 6, 7],
  "risk_profile": "balanced",
  "max_transfers": 2,
  "max_hit_points": 4,
  "minimum_net_gain": 0.5,
  "chip": null,
  "locked_player_ids": [],
  "excluded_player_ids": [],
  "excluded_club_ids": [],
  "overrides": {
    "free_transfers": 1,
    "selling_prices_tenths": {}
  },
  "alternative_count": 3,
  "time_limit_ms": 8000
}
```

The server resolves the latest compatible ruleset and projection set unless explicit IDs are supplied. The response always identifies the resolved versions.

### Optimization response

```json
{
  "run": {
    "id": "run_uuid",
    "kind": "transfer_plan",
    "status": "optimal",
    "runtime_ms": 742,
    "optimality_gap": 0,
    "snapshot_id": "snapshot_uuid",
    "projection_set_id": "projection_uuid",
    "ruleset_id": "2026-v1",
    "optimizer_version": "optimizer-0.1"
  },
  "baseline": {
    "projected_points": 201.4,
    "by_gameweek": [
      {"gameweek": 4, "projected_points": 49.2}
    ]
  },
  "solutions": [
    {
      "rank": 1,
      "is_recommended": true,
      "transfers": [
        {
          "gameweek": 4,
          "out_player_id": 1,
          "in_player_id": 2,
          "sell_price_tenths": 75,
          "buy_price_tenths": 77
        }
      ],
      "projected_points": 207.0,
      "gross_gain": 5.6,
      "hit_cost": 0,
      "net_gain": 5.6,
      "risk_adjustment": -0.4,
      "terminal_adjustment": 0.1,
      "remaining_bank_tenths": 3,
      "by_gameweek": [],
      "lineups": [],
      "explanations": [],
      "validation_status": "valid"
    }
  ],
  "warnings": []
}
```

### `GET /api/v1/optimizations/{run_id}`

Return a stored run and all solutions. Useful for cached results and future asynchronous execution.

### `POST /api/v1/optimizations/{run_id}/stale-check`

Compare the run's immutable inputs with the latest data and return stale reasons. Normal dashboard reads may perform this check automatically.

## 10. Override endpoints

### `PUT /api/v1/tracked-teams/{tracked_team_id}/overrides/{gameweek}`

Set validated rules-critical overrides without changing imported source data.

### `DELETE /api/v1/tracked-teams/{tracked_team_id}/overrides/{override_id}`

Remove an override and mark dependent optimizer results stale.

## 11. Caching and freshness

- Official bootstrap and fixture responses use short TTL caching plus source hashes.
- Snapshot endpoints may use ETags based on snapshot ID and update time.
- Identical optimization requests may reuse a completed run only when snapshot, projection set, ruleset, optimizer version, and canonical request hash all match.
- The API response includes `generated_at`, `data_as_of`, and `stale` where recommendations are shown.
- Stale cached recommendations may be displayed for continuity, but never as current.

## 12. Transactions and failure handling

- Snapshot plus squad picks commit in one transaction.
- Projection-set metadata becomes `complete` only after all expected rows commit.
- An optimization solution commits only after independent validation.
- Import and solver failures retain the last good snapshot and solution.
- External error messages are sanitized; diagnostic detail belongs in server logs.

## 13. Migration from the current application

1. Keep current Flask blueprints operational as legacy endpoints.
2. Add a storage package, migrations, normalized provider adapter, and repository layer.
3. Make Team ID submission call `POST /api/v1/tracked-teams`.
4. Replace direct repeated FPL calls in analyzers with snapshot repositories.
5. Add the projection pipeline and immutable projection tables.
6. Add legality validation before the optimizer.
7. Add optimizer endpoints and move the frontend's Smart Swaps view to net-gain plans.
8. Deprecate heuristic recommendation endpoints only after feature parity in the new UI.

The current recommendation engine may remain as an explanatory player-ranking tool, but its scores are not stored as expected points.

## 14. Required API tests

- create and re-create the same tracked team;
- invalid and unavailable Team IDs;
- idempotent same-gameweek refresh;
- partial upstream failure preserving prior data;
- history pagination and snapshot differences;
- null handling for unknown bank, selling prices, and free transfers;
- override create, resolution, and deletion;
- optimization validation errors;
- legal squad and transfer-plan response fixtures;
- infeasible and timeout solver states;
- stale-result detection;
- request hash cache hit and invalidation;
- legacy endpoint regression until deprecation.

## 15. Related specifications

- [Product specification](PRODUCT_SPEC.md)
- [Optimization specification](OPTIMIZATION_SPEC.md)
