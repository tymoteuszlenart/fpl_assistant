"""SQLite persistence for the Phase 1 local, single-user squad tracker."""

import hashlib
import json
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Dict, List, Mapping, Optional


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def _connection(database_path: str):
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def initialize_database(database_path: str) -> None:
    with _connection(database_path) as connection:
        connection.executescript("""
            PRAGMA foreign_keys = ON;
            CREATE TABLE IF NOT EXISTS tracked_teams (
                id INTEGER PRIMARY KEY,
                fpl_team_id INTEGER NOT NULL UNIQUE,
                team_name TEXT,
                manager_name TEXT,
                season TEXT NOT NULL,
                created_at TEXT NOT NULL,
                last_refresh_at TEXT,
                last_successful_refresh_at TEXT,
                refresh_status TEXT NOT NULL DEFAULT 'never',
                refresh_error TEXT
            );
            CREATE TABLE IF NOT EXISTS team_snapshots (
                id INTEGER PRIMARY KEY,
                tracked_team_id INTEGER NOT NULL REFERENCES tracked_teams(id),
                season TEXT NOT NULL,
                gameweek INTEGER NOT NULL,
                as_of TEXT NOT NULL,
                overall_points INTEGER,
                overall_rank INTEGER,
                gameweek_points INTEGER,
                bank_tenths INTEGER,
                team_value_tenths INTEGER,
                free_transfers INTEGER,
                gameweek_transfer_count INTEGER,
                gameweek_transfer_cost INTEGER,
                active_chip TEXT,
                source_payload_hash TEXT NOT NULL,
                import_status TEXT NOT NULL,
                warnings_json TEXT NOT NULL DEFAULT '[]',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(tracked_team_id, season, gameweek)
            );
            CREATE TABLE IF NOT EXISTS squad_picks (
                snapshot_id INTEGER NOT NULL REFERENCES team_snapshots(id) ON DELETE CASCADE,
                fpl_player_id INTEGER NOT NULL,
                squad_position INTEGER NOT NULL,
                multiplier INTEGER,
                is_captain INTEGER NOT NULL DEFAULT 0,
                is_vice_captain INTEGER NOT NULL DEFAULT 0,
                purchase_price_tenths INTEGER,
                selling_price_tenths INTEGER,
                PRIMARY KEY(snapshot_id, fpl_player_id)
            );
            CREATE TABLE IF NOT EXISTS projection_sets (
                id TEXT PRIMARY KEY,
                season TEXT NOT NULL,
                generated_at TEXT NOT NULL,
                model_version TEXT NOT NULL,
                gameweeks_json TEXT NOT NULL,
                status TEXT NOT NULL,
                warnings_json TEXT NOT NULL DEFAULT '[]'
            );
            CREATE TABLE IF NOT EXISTS player_projections (
                projection_set_id TEXT NOT NULL REFERENCES projection_sets(id),
                fpl_player_id INTEGER NOT NULL,
                gameweek INTEGER NOT NULL,
                expected_points REAL NOT NULL,
                expected_minutes REAL NOT NULL,
                appearance_probability REAL NOT NULL,
                risk REAL NOT NULL,
                fixture_count INTEGER NOT NULL,
                components_json TEXT NOT NULL,
                PRIMARY KEY(projection_set_id, fpl_player_id, gameweek)
            );
            CREATE TABLE IF NOT EXISTS chip_usage (
                tracked_team_id INTEGER NOT NULL REFERENCES tracked_teams(id),
                chip_name TEXT NOT NULL,
                gameweek INTEGER NOT NULL,
                PRIMARY KEY(tracked_team_id, chip_name)
            );
        """)


def _payload_hash(payload: Mapping[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(canonical.encode()).hexdigest()


class TrackedTeamStore:
    def __init__(self, database_path: str):
        self.database_path = database_path

    def list_teams(self) -> List[Dict[str, Any]]:
        with _connection(self.database_path) as connection:
            rows = connection.execute("SELECT * FROM tracked_teams ORDER BY last_successful_refresh_at DESC, id DESC").fetchall()
        return [self._team(row) for row in rows]

    def get_team(self, fpl_team_id: int) -> Optional[Dict[str, Any]]:
        with _connection(self.database_path) as connection:
            row = connection.execute("SELECT * FROM tracked_teams WHERE fpl_team_id = ?", (fpl_team_id,)).fetchone()
        return self._team(row) if row else None

    def snapshots(self, fpl_team_id: int) -> Optional[List[Dict[str, Any]]]:
        with _connection(self.database_path) as connection:
            team = connection.execute("SELECT id FROM tracked_teams WHERE fpl_team_id = ?", (fpl_team_id,)).fetchone()
            if not team:
                return None
            rows = connection.execute(
                "SELECT * FROM team_snapshots WHERE tracked_team_id = ? ORDER BY gameweek DESC", (team['id'],)
            ).fetchall()
        return [self._snapshot(row) for row in rows]

    def snapshot_changes(self, fpl_team_id: int, gameweek: int) -> Optional[Dict[str, Any]]:
        """Compare a complete snapshot with its immediately preceding snapshot."""
        with _connection(self.database_path) as connection:
            team = connection.execute("SELECT id FROM tracked_teams WHERE fpl_team_id = ?", (fpl_team_id,)).fetchone()
            if not team:
                return None
            current = connection.execute("""
                SELECT * FROM team_snapshots WHERE tracked_team_id = ? AND gameweek = ?
            """, (team['id'], gameweek)).fetchone()
            if not current:
                return {'available': False, 'reason': 'Snapshot was not found.'}
            previous = connection.execute("""
                SELECT * FROM team_snapshots WHERE tracked_team_id = ? AND season = ? AND gameweek < ?
                ORDER BY gameweek DESC LIMIT 1
            """, (team['id'], current['season'], gameweek)).fetchone()
            if not previous:
                return {'available': False, 'reason': 'No earlier snapshot is available.'}
            if current['import_status'] != 'complete' or previous['import_status'] != 'complete':
                return {'available': False, 'reason': 'Both snapshots need imported squad picks to calculate changes.'}
            current_ids = self._pick_ids(connection, current['id'])
            previous_ids = self._pick_ids(connection, previous['id'])
        return {
            'available': True,
            'from_gameweek': previous['gameweek'],
            'to_gameweek': current['gameweek'],
            'transferred_in': sorted(current_ids - previous_ids),
            'transferred_out': sorted(previous_ids - current_ids),
        }

    def latest_squad_state(self, fpl_team_id: int) -> Optional[Dict[str, Any]]:
        """Return the latest complete imported snapshot and its official picks."""
        with _connection(self.database_path) as connection:
            team = connection.execute("SELECT * FROM tracked_teams WHERE fpl_team_id = ?", (fpl_team_id,)).fetchone()
            if not team:
                return None
            snapshot = connection.execute("""
                SELECT * FROM team_snapshots WHERE tracked_team_id = ? AND import_status = 'complete'
                ORDER BY gameweek DESC LIMIT 1
            """, (team['id'],)).fetchone()
            if not snapshot:
                return {'team': self._team(team), 'snapshot': None, 'picks': []}
            picks = [dict(row) for row in connection.execute(
                'SELECT * FROM squad_picks WHERE snapshot_id = ? ORDER BY squad_position', (snapshot['id'],)
            )]
        return {'team': self._team(team), 'snapshot': self._snapshot(snapshot), 'picks': picks}

    def save_projection_set(self, season: str, gameweeks: List[int], projections: List[Mapping[str, Any]], warnings: List[str]) -> Dict[str, Any]:
        projection_set_id, now = str(uuid.uuid4()), utcnow()
        with _connection(self.database_path) as connection:
            connection.execute("""
                INSERT INTO projection_sets (id, season, generated_at, model_version, gameweeks_json, status, warnings_json)
                VALUES (?, ?, ?, 'baseline-0.1', ?, 'complete', ?)
            """, (projection_set_id, season, now, json.dumps(gameweeks), json.dumps(warnings)))
            connection.executemany("""
                INSERT INTO player_projections (projection_set_id, fpl_player_id, gameweek, expected_points, expected_minutes,
                    appearance_probability, risk, fixture_count, components_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [(projection_set_id, item['fpl_player_id'], item['gameweek'], item['expected_points'], item['expected_minutes'],
                     item['appearance_probability'], item['risk'], item['fixture_count'], json.dumps(item['components'])) for item in projections])
        return self.get_projection_set(projection_set_id)

    def get_projection_set(self, projection_set_id: str) -> Optional[Dict[str, Any]]:
        with _connection(self.database_path) as connection:
            row = connection.execute('SELECT * FROM projection_sets WHERE id = ?', (projection_set_id,)).fetchone()
        return self._projection_set(row) if row else None

    def latest_projection_set(self) -> Optional[Dict[str, Any]]:
        with _connection(self.database_path) as connection:
            row = connection.execute('SELECT * FROM projection_sets ORDER BY generated_at DESC LIMIT 1').fetchone()
        return self._projection_set(row) if row else None

    def projection_values(self, projection_set_id: str) -> Dict[tuple, float]:
        with _connection(self.database_path) as connection:
            rows = connection.execute("SELECT fpl_player_id, gameweek, expected_points FROM player_projections WHERE projection_set_id = ?", (projection_set_id,)).fetchall()
        return {(row['fpl_player_id'], row['gameweek']): row['expected_points'] for row in rows}

    def used_chips(self, fpl_team_id: int) -> Optional[List[Dict[str, Any]]]:
        with _connection(self.database_path) as connection:
            team = connection.execute('SELECT id FROM tracked_teams WHERE fpl_team_id = ?', (fpl_team_id,)).fetchone()
            if not team:
                return None
            rows = connection.execute('SELECT chip_name, gameweek FROM chip_usage WHERE tracked_team_id = ? ORDER BY gameweek', (team['id'],)).fetchall()
        return [dict(row) for row in rows]

    def mark_refresh_failed(self, fpl_team_id: int, season: str, message: str) -> None:
        now = utcnow()
        with _connection(self.database_path) as connection:
            connection.execute("""
                INSERT INTO tracked_teams (fpl_team_id, season, created_at, last_refresh_at, refresh_status, refresh_error)
                VALUES (?, ?, ?, ?, 'failed', ?)
                ON CONFLICT(fpl_team_id) DO UPDATE SET last_refresh_at = excluded.last_refresh_at,
                    refresh_status = 'failed', refresh_error = excluded.refresh_error
            """, (fpl_team_id, season, now, now, message))

    def import_team(
        self, fpl_team_id: int, season: str, team: Mapping[str, Any], current_gameweek: int,
        picks_payload: Mapping[str, Any], history: Mapping[str, Any],
    ) -> Dict[str, Any]:
        now = utcnow()
        first, last = team.get('player_first_name'), team.get('player_last_name')
        manager = ' '.join(part for part in (first, last) if part) or None
        with _connection(self.database_path) as connection:
            connection.execute("""
                INSERT INTO tracked_teams (fpl_team_id, team_name, manager_name, season, created_at, last_refresh_at,
                    last_successful_refresh_at, refresh_status, refresh_error)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'current', NULL)
                ON CONFLICT(fpl_team_id) DO UPDATE SET team_name = excluded.team_name, manager_name = excluded.manager_name,
                    season = excluded.season, last_refresh_at = excluded.last_refresh_at,
                    last_successful_refresh_at = excluded.last_successful_refresh_at, refresh_status = 'current', refresh_error = NULL
            """, (fpl_team_id, team.get('name'), manager, season, now, now, now))
            tracked_id = connection.execute("SELECT id FROM tracked_teams WHERE fpl_team_id = ?", (fpl_team_id,)).fetchone()['id']
            for record in history.get('current', []):
                gameweek = record.get('event')
                if isinstance(gameweek, int) and gameweek != current_gameweek:
                    self._upsert_snapshot(connection, tracked_id, season, gameweek, record, now, 'partial', ['Historical picks were not imported.'])
            for chip in history.get('chips', []):
                name, gameweek = chip.get('name'), chip.get('event')
                if isinstance(name, str) and isinstance(gameweek, int):
                    connection.execute('INSERT OR REPLACE INTO chip_usage (tracked_team_id, chip_name, gameweek) VALUES (?, ?, ?)',
                                       (tracked_id, name, gameweek))
            current_record = dict(picks_payload.get('entry_history') or {})
            current_record.update({
                'overall_points': team.get('summary_overall_points'),
                'overall_rank': team.get('summary_overall_rank'),
                'transfers_available': team.get('transfers_available'),
            })
            snapshot_id = self._upsert_snapshot(connection, tracked_id, season, current_gameweek, current_record, now, 'complete', [])
            connection.execute("DELETE FROM squad_picks WHERE snapshot_id = ?", (snapshot_id,))
            for pick in picks_payload.get('picks', []):
                if isinstance(pick.get('element'), int) and isinstance(pick.get('position'), int):
                    connection.execute("""
                        INSERT INTO squad_picks (snapshot_id, fpl_player_id, squad_position, multiplier, is_captain, is_vice_captain,
                            purchase_price_tenths, selling_price_tenths)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (snapshot_id, pick['element'], pick['position'], pick.get('multiplier'), int(bool(pick.get('is_captain'))),
                          int(bool(pick.get('is_vice_captain'))), pick.get('purchase_price'), pick.get('selling_price')))
        return self.get_team(fpl_team_id)

    def _upsert_snapshot(self, connection, team_id, season, gameweek, record, observed_at, status, warnings):
        payload_hash = _payload_hash(record)
        values = (team_id, season, gameweek, observed_at, record.get('total_points', record.get('overall_points')),
                  record.get('overall_rank'), record.get('points'), record.get('bank'), record.get('value'),
                  record.get('transfers_available'), record.get('event_transfers'), record.get('event_transfers_cost'),
                  record.get('active_chip'), payload_hash, status, json.dumps(warnings), observed_at, observed_at)
        connection.execute("""
            INSERT INTO team_snapshots (tracked_team_id, season, gameweek, as_of, overall_points, overall_rank, gameweek_points,
                bank_tenths, team_value_tenths, free_transfers, gameweek_transfer_count, gameweek_transfer_cost, active_chip,
                source_payload_hash, import_status, warnings_json, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(tracked_team_id, season, gameweek) DO UPDATE SET as_of=excluded.as_of,
                overall_points=excluded.overall_points, overall_rank=excluded.overall_rank, gameweek_points=excluded.gameweek_points,
                bank_tenths=excluded.bank_tenths, team_value_tenths=excluded.team_value_tenths, free_transfers=excluded.free_transfers,
                gameweek_transfer_count=excluded.gameweek_transfer_count, gameweek_transfer_cost=excluded.gameweek_transfer_cost,
                active_chip=excluded.active_chip, source_payload_hash=excluded.source_payload_hash,
                import_status=excluded.import_status, warnings_json=excluded.warnings_json, updated_at=excluded.updated_at
        """, values)
        return connection.execute("SELECT id FROM team_snapshots WHERE tracked_team_id = ? AND season = ? AND gameweek = ?", (team_id, season, gameweek)).fetchone()['id']

    @staticmethod
    def _team(row):
        return dict(row)

    @staticmethod
    def _pick_ids(connection, snapshot_id: int):
        return {row['fpl_player_id'] for row in connection.execute(
            'SELECT fpl_player_id FROM squad_picks WHERE snapshot_id = ?', (snapshot_id,)
        )}

    @staticmethod
    def _snapshot(row):
        snapshot = dict(row)
        snapshot['warnings'] = json.loads(snapshot.pop('warnings_json'))
        return snapshot

    @staticmethod
    def _projection_set(row):
        value = dict(row)
        value['gameweeks'] = json.loads(value.pop('gameweeks_json'))
        value['warnings'] = json.loads(value.pop('warnings_json'))
        return value
