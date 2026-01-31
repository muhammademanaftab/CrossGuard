"""
Repository classes for Cross Guard database operations.

Provides CRUD (Create, Read, Update, Delete) operations for
analysis data with proper transaction handling.
"""

import sqlite3
import json
from typing import List, Optional, Dict, Any
from datetime import datetime

from .models import Analysis, AnalysisFeature, BrowserResult
from .connection import get_connection
from src.utils.config import get_logger

logger = get_logger('database.repositories')


class AnalysisRepository:
    """Repository for Analysis CRUD operations.

    Provides methods to save, retrieve, and delete analysis records
    along with their related features and browser results.
    """

    def __init__(self, conn: Optional[sqlite3.Connection] = None):
        """Initialize the repository.

        Args:
            conn: Optional database connection. If not provided,
                  uses the shared connection.
        """
        self._conn = conn

    @property
    def conn(self) -> sqlite3.Connection:
        """Get the database connection."""
        if self._conn is None:
            return get_connection()
        return self._conn

    def save_analysis(self, analysis: Analysis) -> int:
        """Save an analysis with all its features and browser results.

        Uses a transaction to ensure data integrity.

        Args:
            analysis: Analysis object to save

        Returns:
            The ID of the saved analysis

        Raises:
            sqlite3.Error: If database operation fails
        """
        conn = self.conn
        cursor = conn.cursor()

        try:
            # Start transaction
            cursor.execute("BEGIN TRANSACTION")

            # Insert main analysis record
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

            # Insert features
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

                # Insert browser results for this feature
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

            # Commit transaction
            cursor.execute("COMMIT")

            logger.info(f"Saved analysis #{analysis_id} for {analysis.file_name}")
            return analysis_id

        except Exception as e:
            # Rollback on error
            cursor.execute("ROLLBACK")
            logger.error(f"Error saving analysis: {e}")
            raise

    def get_all_analyses(
        self,
        limit: int = 50,
        offset: int = 0,
        file_type: Optional[str] = None
    ) -> List[Analysis]:
        """Get all analyses with pagination.

        Args:
            limit: Maximum number of records to return
            offset: Number of records to skip
            file_type: Optional filter by file type

        Returns:
            List of Analysis objects (without features loaded)
        """
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
        """Get a single analysis by ID.

        Args:
            analysis_id: The analysis ID
            include_features: Whether to load features and browser results

        Returns:
            Analysis object or None if not found
        """
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
        """Load features for an analysis.

        Args:
            analysis_id: The analysis ID

        Returns:
            List of AnalysisFeature objects with browser results
        """
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
        """Load browser results for a feature.

        Args:
            feature_id: The analysis feature ID

        Returns:
            List of BrowserResult objects
        """
        conn = self.conn

        cursor = conn.execute("""
            SELECT * FROM browser_results
            WHERE analysis_feature_id = ?
        """, (feature_id,))

        return [BrowserResult.from_row(row) for row in cursor.fetchall()]

    def get_analyses_for_file(
        self,
        file_name: str,
        limit: int = 10
    ) -> List[Analysis]:
        """Get analysis history for a specific file.

        Args:
            file_name: The file name to search for
            limit: Maximum number of records to return

        Returns:
            List of Analysis objects for the file
        """
        conn = self.conn

        cursor = conn.execute("""
            SELECT * FROM analyses
            WHERE file_name = ?
            ORDER BY analyzed_at DESC
            LIMIT ?
        """, (file_name, limit))

        return [Analysis.from_row(row) for row in cursor.fetchall()]

    def delete_analysis(self, analysis_id: int) -> bool:
        """Delete an analysis and all related data.

        Cascading delete will automatically remove features and browser results.

        Args:
            analysis_id: The analysis ID to delete

        Returns:
            True if deleted, False if not found
        """
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
        """Delete all analysis history.

        Returns:
            Number of records deleted
        """
        conn = self.conn

        # Count before deletion
        cursor = conn.execute("SELECT COUNT(*) FROM analyses")
        count = cursor.fetchone()[0]

        # Delete all (cascading delete handles related tables)
        conn.execute("DELETE FROM analyses")

        logger.info(f"Cleared all {count} analyses from history")
        return count

    def get_count(self, file_type: Optional[str] = None) -> int:
        """Get total count of analyses.

        Args:
            file_type: Optional filter by file type

        Returns:
            Number of analyses in the database
        """
        conn = self.conn

        if file_type:
            cursor = conn.execute(
                "SELECT COUNT(*) FROM analyses WHERE file_type = ?",
                (file_type,)
            )
        else:
            cursor = conn.execute("SELECT COUNT(*) FROM analyses")

        return cursor.fetchone()[0]

    def search_analyses(
        self,
        query: str,
        limit: int = 20
    ) -> List[Analysis]:
        """Search analyses by file name.

        Args:
            query: Search query (partial file name)
            limit: Maximum results to return

        Returns:
            List of matching Analysis objects
        """
        conn = self.conn

        cursor = conn.execute("""
            SELECT * FROM analyses
            WHERE file_name LIKE ?
            ORDER BY analyzed_at DESC
            LIMIT ?
        """, (f'%{query}%', limit))

        return [Analysis.from_row(row) for row in cursor.fetchall()]


def save_analysis_from_result(result: Dict[str, Any], file_info: Dict[str, str]) -> int:
    """Helper function to save an analysis result from the analyzer.

    Args:
        result: Analysis result dictionary from the analyzer
        file_info: Dictionary with 'file_name', 'file_path', 'file_type'

    Returns:
        The ID of the saved analysis
    """
    from src.utils.feature_names import get_feature_name

    # Create Analysis object
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

    # Set browsers
    target_browsers = {}
    for browser_name, browser_data in browsers.items():
        target_browsers[browser_name] = browser_data.get('version', '')
    analysis.browsers = target_browsers

    # Build features list
    features = []
    all_feature_ids = set()

    # Collect all feature IDs from all categories
    for category in ['html', 'css', 'js']:
        for feature_id in features_dict.get(category, []):
            all_feature_ids.add((feature_id, category))

    # Create AnalysisFeature objects
    for feature_id, category in all_feature_ids:
        feature = AnalysisFeature(
            feature_id=feature_id,
            feature_name=get_feature_name(feature_id),
            category=category,
        )

        # Add browser results for this feature
        for browser_name, browser_data in browsers.items():
            # Determine support status
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
                status = 'u'  # Unknown

            browser_result = BrowserResult(
                browser=browser_name,
                version=browser_data.get('version', ''),
                support_status=status,
            )
            feature.browser_results.append(browser_result)

        features.append(feature)

    analysis.features = features

    # Save to database
    repo = AnalysisRepository()
    return repo.save_analysis(analysis)
