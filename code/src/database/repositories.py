"""CRUD repositories for analyses, settings, bookmarks, and tags."""

import sqlite3
from typing import List, Optional, Dict, Any
from datetime import datetime

from .models import Analysis, AnalysisFeature, BrowserResult
from .connection import get_connection
from src.utils.config import get_logger

logger = get_logger('database.repositories')


class _BaseRepository:

    def __init__(self, conn: Optional[sqlite3.Connection] = None):
        self._conn = conn

    @property
    def conn(self) -> sqlite3.Connection:
        if self._conn is None:
            return get_connection()
        return self._conn


class AnalysisRepository(_BaseRepository):

    def save_analysis(self, analysis: Analysis) -> int:
        conn = self.conn
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO analyses
                (file_name, file_path, file_type, overall_score, grade,
                 total_features, analyzed_at, browsers_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                analysis.file_name,
                analysis.file_path,
                analysis.file_type,
                analysis.overall_score,
                analysis.grade,
                analysis.total_features,
                analysis.analyzed_at.isoformat() if analysis.analyzed_at else datetime.now().isoformat(),
                analysis.browsers_json,
            ))

            analysis_id = cursor.lastrowid
            analysis.id = analysis_id

            for feature in analysis.features:
                cursor.execute("""
                    INSERT INTO analysis_features
                    (analysis_id, feature_id, feature_name, category)
                    VALUES (?, ?, ?, ?)
                """, (
                    analysis_id,
                    feature.feature_id,
                    feature.feature_name,
                    feature.category,
                ))

                feature_id = cursor.lastrowid
                feature.id = feature_id
                feature.analysis_id = analysis_id

                for browser_result in feature.browser_results:
                    cursor.execute("""
                        INSERT INTO browser_results
                        (analysis_feature_id, browser, version, support_status)
                        VALUES (?, ?, ?, ?)
                    """, (
                        feature_id,
                        browser_result.browser,
                        browser_result.version,
                        browser_result.support_status,
                    ))

                    browser_result.id = cursor.lastrowid
                    browser_result.analysis_feature_id = feature_id

            conn.commit()

            logger.info(f"Saved analysis #{analysis_id} for {analysis.file_name}")
            return analysis_id

        except Exception as e:
            conn.rollback()
            logger.error(f"Error saving analysis: {e}")
            raise

    def get_all_analyses(
        self,
        limit: int = 50,
        offset: int = 0,
        file_type: Optional[str] = None
    ) -> List[Analysis]:
        """Newest first, paginated. Features are not eager-loaded."""
        conn = self.conn

        if file_type:
            cursor = conn.execute("""
                SELECT * FROM analyses
                WHERE file_type = ?
                ORDER BY analyzed_at DESC
                LIMIT ? OFFSET ?
            """, (file_type, limit, offset))
        else:
            cursor = conn.execute("""
                SELECT * FROM analyses
                ORDER BY analyzed_at DESC
                LIMIT ? OFFSET ?
            """, (limit, offset))

        rows = cursor.fetchall()
        return [Analysis.from_row(row) for row in rows]

    def get_analysis_by_id(
        self,
        analysis_id: int,
        include_features: bool = True
    ) -> Optional[Analysis]:
        conn = self.conn

        cursor = conn.execute(
            "SELECT * FROM analyses WHERE id = ?",
            (analysis_id,)
        )
        row = cursor.fetchone()

        if not row:
            return None

        analysis = Analysis.from_row(row)

        if include_features:
            analysis.features = self._load_features(analysis_id)

        return analysis

    def _load_features(self, analysis_id: int) -> List[AnalysisFeature]:
        conn = self.conn

        cursor = conn.execute("""
            SELECT * FROM analysis_features
            WHERE analysis_id = ?
        """, (analysis_id,))

        features = []
        for row in cursor.fetchall():
            feature = AnalysisFeature.from_row(row)
            feature.browser_results = self._load_browser_results(feature.id)
            features.append(feature)

        return features

    def _load_browser_results(self, feature_id: int) -> List[BrowserResult]:
        conn = self.conn

        cursor = conn.execute("""
            SELECT * FROM browser_results
            WHERE analysis_feature_id = ?
        """, (feature_id,))

        return [BrowserResult.from_row(row) for row in cursor.fetchall()]

    def delete_analysis(self, analysis_id: int) -> bool:
        """Cascade deletes nested features and browser results automatically"""
        conn = self.conn

        cursor = conn.execute(
            "DELETE FROM analyses WHERE id = ?",
            (analysis_id,)
        )

        deleted = cursor.rowcount > 0

        if deleted:
            logger.info(f"Deleted analysis #{analysis_id}")
        else:
            logger.warning(f"Analysis #{analysis_id} not found for deletion")

        return deleted

    def clear_all(self) -> int:
        """Returns count of deleted records"""
        conn = self.conn

        cursor = conn.execute("SELECT COUNT(*) FROM analyses")
        count = cursor.fetchone()[0]

        conn.execute("DELETE FROM analyses")

        logger.info(f"Cleared all {count} analyses from history")
        return count

    def get_count(self, file_type: Optional[str] = None) -> int:
        conn = self.conn

        if file_type:
            cursor = conn.execute(
                "SELECT COUNT(*) FROM analyses WHERE file_type = ?",
                (file_type,)
            )
        else:
            cursor = conn.execute("SELECT COUNT(*) FROM analyses")

        return cursor.fetchone()[0]


def save_analysis_from_result(result: Dict[str, Any], file_info: Dict[str, str]) -> int:
    """Convert an analyzer result dict into model objects and save to DB."""
    from src.utils.feature_names import get_feature_name

    scores = result.get('scores', {})
    summary = result.get('summary', {})
    browsers = result.get('browsers', {})
    features_dict = result.get('features', {})

    analysis = Analysis(
        file_name=file_info.get('file_name', 'unknown'),
        file_path=file_info.get('file_path', ''),
        file_type=file_info.get('file_type', 'unknown'),
        overall_score=scores.get('weighted_score', 0.0),
        grade=scores.get('grade', 'N/A'),
        total_features=summary.get('total_features', 0),
    )

    target_browsers = {}
    for browser_name, browser_data in browsers.items():
        target_browsers[browser_name] = browser_data.get('version', '')
    analysis.browsers = target_browsers

    features = []
    all_feature_ids = set()

    for category in ['html', 'css', 'js']:
        for feature_id in features_dict.get(category, []):
            all_feature_ids.add((feature_id, category))

    for feature_id, category in all_feature_ids:
        feature = AnalysisFeature(
            feature_id=feature_id,
            feature_name=get_feature_name(feature_id),
            category=category,
        )

        for browser_name, browser_data in browsers.items():
            unsupported = browser_data.get('unsupported_features', [])
            partial = browser_data.get('partial_features', [])
            supported = browser_data.get('supported_features', [])

            if feature_id in unsupported:
                status = 'n'
            elif feature_id in partial:
                status = 'a'
            elif feature_id in supported:
                status = 'y'
            else:
                status = 'u'

            browser_result = BrowserResult(
                browser=browser_name,
                version=browser_data.get('version', ''),
                support_status=status,
            )
            feature.browser_results.append(browser_result)

        features.append(feature)

    analysis.features = features

    repo = AnalysisRepository()
    return repo.save_analysis(analysis)


class SettingsRepository(_BaseRepository):

    def get(self, key: str, default: str = '') -> str:
        cursor = self.conn.execute(
            "SELECT value FROM settings WHERE key = ?",
            (key,)
        )
        row = cursor.fetchone()
        return row['value'] if row else default

    def set(self, key: str, value: str):
        self.conn.execute("""
            INSERT OR REPLACE INTO settings (key, value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """, (key, value))
        logger.debug(f"Setting '{key}' = '{value}'")

    def get_as_bool(self, key: str, default: bool = False) -> bool:
        value = self.get(key, str(default).lower())
        return value.lower() in ('true', '1', 'yes', 'on')

    def get_as_list(self, key: str, default: List[str] = None) -> List[str]:
        value = self.get(key, '')
        if not value:
            return default or []
        return [v.strip() for v in value.split(',') if v.strip()]


class BookmarksRepository(_BaseRepository):

    def add_bookmark(self, analysis_id: int, note: str = '') -> int:
        from .models import Bookmark

        cursor = self.conn.execute("""
            INSERT OR REPLACE INTO bookmarks (analysis_id, note, created_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """, (analysis_id, note))

        logger.info(f"Bookmarked analysis #{analysis_id}")
        return cursor.lastrowid

    def remove_bookmark(self, analysis_id: int) -> bool:
        cursor = self.conn.execute(
            "DELETE FROM bookmarks WHERE analysis_id = ?",
            (analysis_id,)
        )
        removed = cursor.rowcount > 0
        if removed:
            logger.info(f"Removed bookmark from analysis #{analysis_id}")
        return removed

    def is_bookmarked(self, analysis_id: int) -> bool:
        cursor = self.conn.execute(
            "SELECT 1 FROM bookmarks WHERE analysis_id = ?",
            (analysis_id,)
        )
        return cursor.fetchone() is not None

    def get_all_bookmarks(self, limit: int = 50) -> List[Dict[str, Any]]:
        from .models import Bookmark, Analysis

        cursor = self.conn.execute("""
            SELECT b.*, a.file_name, a.file_type, a.overall_score, a.grade,
                   a.total_features, a.analyzed_at
            FROM bookmarks b
            JOIN analyses a ON b.analysis_id = a.id
            ORDER BY b.created_at DESC
            LIMIT ?
        """, (limit,))

        results = []
        for row in cursor.fetchall():
            bookmark = {
                'id': row['id'],
                'analysis_id': row['analysis_id'],
                'note': row['note'] or '',
                'created_at': row['created_at'],
                'analysis': {
                    'file_name': row['file_name'],
                    'file_type': row['file_type'],
                    'overall_score': row['overall_score'],
                    'grade': row['grade'],
                    'total_features': row['total_features'],
                    'analyzed_at': row['analyzed_at'],
                }
            }
            results.append(bookmark)

        return results

    def get_count(self) -> int:
        cursor = self.conn.execute("SELECT COUNT(*) FROM bookmarks")
        return cursor.fetchone()[0]


