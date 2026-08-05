# FPL Assistant Product Specification

Status: Draft canonical specification

Version: 0.1

Last updated: 2026-08-05

## 1. Product statement

FPL Assistant helps a Fantasy Premier League manager build the most valuable legal squad, track how their own squad changes and performs over time, and decide which transfers to make as new gameweeks, prices, fixtures, and player availability change.

In this specification, **most valuable** means the squad or transfer plan with the highest projected FPL points over a chosen planning horizon, subject to FPL rules and the manager's real budget. Value-for-money is an input and tie-breaker, not the sole objective.

The app advises. It does not submit transfers to the official FPL site.

## 2. Problem

The current application can load a public team by Team ID, show its latest squad, and rank individual replacement candidates. It does not yet:

- optimize a complete legal 15-player squad;
- retain squad snapshots or measure changes over time;
- compare transfer combinations over multiple gameweeks;
- account fully for transfer costs, selling prices, chips, lineups, captaincy, or uncertainty;
- explain the expected benefit of a plan versus making no changes.

Managers therefore receive interesting player lists, but not a complete, stateful decision recommendation.

## 3. Target users

### Primary user

An active FPL manager who reviews their team at least once per gameweek and wants a clear, data-supported transfer plan.

### Secondary user

A manager preparing a new squad or using a squad-resetting chip who wants the best legal squad for a budget and planning horizon.

### User assumptions

- The user knows or can find their public FPL Team ID.
- The user makes final decisions and executes them on the official FPL site.
- The user may prefer either safe, balanced, or differential-heavy recommendations.

## 4. Product goals

1. Produce a valid, high-projection 15-player squad for a configurable budget and horizon.
2. Import and retain a manager's squad state for each gameweek.
3. Recommend legal one- or multi-transfer plans and quantify their expected net gain.
4. Refresh recommendations when relevant inputs change.
5. Explain recommendations in terms a manager can verify: projected points, fixtures, minutes, availability, price, risk, and transfer cost.
6. Make uncertainty visible rather than presenting estimates as facts.

## 5. Non-goals for the first release

- Executing or confirming official FPL transfers.
- Handling FPL credentials or private authenticated endpoints.
- Guaranteeing future points or rank improvement.
- Real-time match commentary or live-score replacement.
- Mini-league opponent modeling.
- Training a bespoke machine-learning model before a reliable baseline and evaluation set exist.

## 6. Core user journeys

### 6.1 Track my squad

1. The user enters a public FPL Team ID.
2. The app validates the team and creates or updates a tracked-team record.
3. It imports the latest available squad and gameweek state.
4. The dashboard shows the current squad, bank, rank, points, active chip when known, and the last successful refresh time.
5. The user can view prior snapshots and the changes between gameweeks.

If a value cannot be obtained reliably from public data, the UI labels it as unknown and allows a manual override where that value affects optimization.

### 6.2 Improve my current squad

1. The user selects a planning horizon, transfer limit, and risk profile.
2. The app calculates a **no-transfer baseline**.
3. It evaluates legal transfer plans using the user's squad, bank, selling prices, and transfer-cost rules.
4. It returns a primary recommendation and meaningful alternatives.
5. Each plan shows transfers, projected points by gameweek, gross gain, point-hit cost, net gain versus baseline, remaining bank, and key risks.
6. The user can lock players, exclude players or clubs, and rerun the plan.

### 6.3 Build the best squad

1. The user chooses a budget, starting gameweek, horizon, and risk profile.
2. The user may lock or exclude players and choose whether to optimize for an initial squad or a squad-resetting chip.
3. The app returns a legal 15-player squad, recommended starting XI, captain, vice-captain, and bench order for each gameweek in the horizon.
4. It also returns alternative squads so the user can understand important trade-offs.

### 6.4 Review what changed

1. After a refresh, the app compares the new snapshot with the previous one.
2. It highlights actual transfers, price changes, injuries or availability changes, and projection changes.
3. When a saved recommendation is no longer valid or materially worse, it is marked stale and the app explains why.

## 7. Functional requirements

### 7.1 Team import and tracking

- FR-TRACK-01: Accept and validate a numeric public FPL Team ID.
- FR-TRACK-02: Store the tracked team independently of a browser session.
- FR-TRACK-03: Store at most one canonical snapshot per team and gameweek, while allowing a snapshot to be refreshed before it is finalized.
- FR-TRACK-04: Backfill publicly available gameweek history when a team is first tracked.
- FR-TRACK-05: Record the data source and fetch timestamp for imported values.
- FR-TRACK-06: Show the latest successful refresh and any partial-import warnings.
- FR-TRACK-07: Calculate changes between consecutive snapshots, including players in/out, squad points, rank, bank, and team value when available.
- FR-TRACK-08: Never infer an unavailable rules-critical value without labelling the inference.

### 7.2 Player projections

- FR-PROJ-01: Produce projected points per player and gameweek.
- FR-PROJ-02: Include expected minutes and appearance probability.
- FR-PROJ-03: account for fixture difficulty, home/away status, blanks, and double gameweeks.
- FR-PROJ-04: Include availability status and known news freshness.
- FR-PROJ-05: Store the projection model version and generation time.
- FR-PROJ-06: Expose a confidence or risk measure alongside the mean projection.
- FR-PROJ-07: Preserve old projections so recommendation quality can be evaluated after a gameweek.

### 7.3 Full-squad builder

- FR-SQUAD-01: Build exactly 15 players with the position counts defined by the active FPL ruleset.
- FR-SQUAD-02: Enforce the budget and maximum players per real club.
- FR-SQUAD-03: Select a legal starting XI, captain, vice-captain, and ordered bench.
- FR-SQUAD-04: Optimize over a configurable horizon, initially 1-6 gameweeks.
- FR-SQUAD-05: Support locked players, excluded players, excluded clubs, and maximum budget.
- FR-SQUAD-06: Return at least three materially distinct feasible alternatives when they exist.
- FR-SQUAD-07: Clearly state when no feasible squad exists under the supplied constraints.

### 7.4 Transfer planner

- FR-PLAN-01: Always calculate the expected result of making no transfer.
- FR-PLAN-02: Evaluate legal sequences of zero or more transfers over the selected horizon.
- FR-PLAN-03: Use the manager's selling prices when known; do not substitute current market price silently.
- FR-PLAN-04: Apply free-transfer and point-hit rules from a versioned ruleset.
- FR-PLAN-05: Enforce squad composition, club limits, budget, and player availability at every step.
- FR-PLAN-06: Support a user-defined maximum number of transfers and maximum acceptable hit.
- FR-PLAN-07: Support player locks and exclusions.
- FR-PLAN-08: Return net expected gain versus no transfer, not merely the incoming player's score.
- FR-PLAN-09: Explain which gameweeks drive the recommendation and identify important risks.
- FR-PLAN-10: Mark a plan stale when its inputs change materially.

### 7.5 Chips

- FR-CHIP-01: Model chips through the versioned ruleset rather than hardcoded assumptions.
- FR-CHIP-02: The first optimizer release must support a squad-resetting wildcard mode.
- FR-CHIP-03: Free Hit, Bench Boost, and Triple Captain planning may follow after ordinary transfers and wildcard are reliable.
- FR-CHIP-04: A chip recommendation must be compared with saving the chip.

### 7.6 Recommendation explanations

- FR-EXPLAIN-01: Display projected points for incoming and outgoing players over the same horizon.
- FR-EXPLAIN-02: Separate gross projected gain, transfer cost, and net projected gain.
- FR-EXPLAIN-03: Show remaining bank and legality checks.
- FR-EXPLAIN-04: Surface availability, minutes, rotation, fixture, and model-confidence risks.
- FR-EXPLAIN-05: State the data and model refresh times.
- FR-EXPLAIN-06: Avoid claims such as "optimal" unless the solver completed with a proven feasible optimum for the stated inputs.

### 7.7 Dynamic refresh

Recommendations are dynamic when they are recomputed after any of these events:

- a new gameweek or deadline state;
- a player price change;
- a fixture addition, postponement, blank, or double;
- a meaningful availability or expected-minutes change;
- a new squad snapshot;
- a projection-model version change;
- a user constraint change.

The UI must show whether a result is current, stale, or failed. Scheduled background refresh is desirable but not required for the first local release; refresh-on-open and explicit refresh are required.

## 8. Recommendation modes

The default mode is **Balanced**.

| Mode | Behavior |
|---|---|
| Safe | Penalizes uncertain minutes, injury doubts, and high projection variance more strongly. |
| Balanced | Maximizes risk-adjusted projected points with moderate uncertainty penalties. |
| Aggressive | Accepts more minutes uncertainty and may apply a small differential preference as a tie-breaker. |

Low ownership must not be treated as intrinsically valuable in the main optimizer. It may influence tie-breaks or an explicitly selected strategy.

## 9. Primary screens

### Dashboard

- team identity and refresh status;
- current gameweek, points, rank, bank, and team value when known;
- current squad arranged as a pitch plus bench;
- urgent availability warnings;
- recommended next action and its net expected gain.

### Transfer planner

- horizon, risk, transfer, hit, lock, and exclusion controls;
- no-transfer baseline;
- recommended plan and alternatives;
- gameweek-by-gameweek projection comparison;
- explanations and stale-data warnings.

### Squad builder

- budget and constraint controls;
- optimized squad, XI, captaincy, and bench;
- projected points and budget use;
- alternative solutions and trade-offs.

### History

- squad snapshots by gameweek;
- transfers and squad-value changes;
- saved recommendation versus actual outcome where enough data exists;
- projection accuracy summary by model version.

## 10. Success measures

### Product measures

- A returning user can refresh a tracked squad and reach a legal recommendation without re-entering its Team ID.
- At least 90% of successful planner runs produce one primary plan plus two feasible alternatives when the player pool permits.
- Users can understand the net expected gain and major risk of the primary recommendation without opening raw data.

### Quality measures

- 100% of returned squads and transfer states pass legality validation.
- No plan spends unavailable funds according to known selling prices and bank.
- Projection backtests report mean absolute error and calibration by position and horizon.
- Every recommendation is reproducible from stored input, ruleset, projection version, and optimizer version.

### Operational measures

- Cached team dashboard response: target under 1 second locally.
- Typical 1-6 gameweek optimization: target under 10 seconds locally.
- External API failures return a partial-data or retryable status rather than corrupting the last good snapshot.

## 11. Delivery phases

### Phase 0: Correctness foundation

- Add a versioned FPL ruleset and legality validator.
- Normalize official API data and distinguish unknown from zero.
- Add automated tests for import, scoring, constraints, and routes.
- Remove claims in existing guides that are not supported by tests or implementation.

### Phase 1: Stateful squad tracker

- Add persistence and tracked teams.
- Import current and historical snapshots.
- Show snapshot history and changes.
- Add data freshness and error states.

### Phase 2: Projection baseline and transfer planner

- Generate versioned per-player, per-gameweek projections.
- Implement no-transfer baseline.
- Implement legal one- and multi-transfer optimization with net-gain calculations.
- Expose primary and alternative plans with explanations.

### Phase 3: Full-squad optimizer

- Implement initial-squad and wildcard modes.
- Optimize XI, bench, and captaincy across the horizon.
- Add locks, exclusions, alternatives, and infeasibility explanations.

### Phase 4: Advanced strategy

- Add remaining chips, richer uncertainty modeling, scheduled refresh, alerts, and recommendation evaluation.
- Consider mini-league strategy only as an explicit, separately evaluated mode.

## 12. Acceptance scenarios for the first useful release

1. Given a valid Team ID, importing twice in the same gameweek updates one canonical snapshot without duplicating its picks.
2. Given a prior snapshot, a new import identifies the exact players transferred in and out.
3. Given a legal current squad, known bank, selling prices, and projections, the planner returns a legal no-transfer baseline and at least one legal plan or explains why no improving plan exists.
4. A plan with a point hit reports gross gain, hit cost, and net gain separately.
5. A recommended incoming player never causes more than the ruleset's allowed players from one club.
6. A squad builder result has the exact required position counts, stays within budget, and supplies a legal XI.
7. A blank or double gameweek changes player and plan projections appropriately.
8. If selling prices or free transfers are unknown, the planner requests an override or uses a clearly labelled conservative assumption.
9. After projections or squad state change, previously saved plans are marked stale.
10. Every result records enough versioned input to reproduce it.

## 13. Open product decisions

These decisions should be made before implementing the corresponding feature:

- Whether the first release is local/single-user or includes accounts and cloud sync.
- Whether scheduled refresh and alerts are required before deployment.
- Which external data, if any, supplements the official FPL API for expected minutes, injury news, or expected statistics.
- Whether users can manually edit projections or only lock/exclude players.
- Which chip types are in scope for the first public release.

Until decided, this specification assumes a local single-user app, public FPL data, refresh-on-open, ordinary transfers plus wildcard, and optional manual overrides for unavailable team state.

## 14. Related specifications

- [Optimization specification](OPTIMIZATION_SPEC.md)
- [Data and API specification](DATA_AND_API_SPEC.md)
- [Current architecture](../api/ARCHITECTURE.md)
- [Current feature guide](../features/FEATURES_GUIDE.md)
