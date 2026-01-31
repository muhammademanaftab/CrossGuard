"""
Statistics service for Cross Guard database.

Provides aggregated insights from analysis history using SQL queries.
"""

import sqlite3
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta

from .connection import get_connection
from src.utils.config import get_logger

logger = get_logger('database.statistics')


class StatisticsService:
    """Service for computing statistics from analysis history.

    Provides various aggregation methods using SQL queries including:
    - Total counts
    - Average scores
    - Trends over time
    - Top problematic features
    - Most analyzed files
    """

    def __init__(self, conn: Optional[sqlite3.Connection] = None):
        """Initialize the statistics service.

        Args:
            conn: Optional database connection.
        """
        self._conn = conn

    @property
    def conn(self) -> sqlite3.Connection:
        """Get the database connection."""
        if self._conn is None:
            return get_connection()
        return self._conn

    def get_total_analyses(self) -> int:
        """Get the total number of analyses performed.

        SQL: SELECT COUNT(*) FROM analyses;

        Returns:
            Total count of analyses
        """
        cursor = self.conn.execute("SELECT COUNT(*) FROM analyses")
        return cursor.fetchone()[0]

    def get_average_score(self) -> float:
        """Get the average compatibility score across all analyses.

        SQL: SELECT AVG(overall_score) FROM analyses;

        Returns:
            Average score (0-100), or 0 if no analyses
        """
        cursor = self.conn.execute("SELECT AVG(overall_score) FROM analyses")
        result = cursor.fetchone()[0]
        return round(result, 1) if result else 0.0

    def get_best_score(self) -> float:
        """Get the highest compatibility score.

        SQL: SELECT MAX(overall_score) FROM analyses;

        Returns:
            Best score (0-100), or 0 if no analyses
        """
        cursor = self.conn.execute("SELECT MAX(overall_score) FROM analyses")
        result = cursor.fetchone()[0]
        return round(result, 1) if result else 0.0

    def get_worst_score(self) -> float:
        """Get the lowest compatibility score.

        SQL: SELECT MIN(overall_score) FROM analyses;

        Returns:
            Worst score (0-100), or 0 if no analyses
        """
        cursor = self.conn.execute("SELECT MIN(overall_score) FROM analyses")
        result = cursor.fetchone()[0]
        return round(result, 1) if result else 0.0

    def get_score_trend(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get average score trend over time.

        SQL: SELECT DATE(analyzed_at) as date, AVG(overall_score) as avg_score
             FROM analyses
             WHERE analyzed_at >= date('now', '-N days')
             GROUP BY DATE(analyzed_at)
             ORDER BY date DESC;

        Args:
            days: Number of days to look back

        Returns:
            List of dicts with 'date' and 'avg_score' keys
        """
        cursor = self.conn.execute("""
            SELECT DATE(analyzed_at) as date,
                   AVG(overall_score) as avg_score,
                   COUNT(*) as count
            FROM analyses
            WHERE analyzed_at >= date('now', ? || ' days')
            GROUP BY DATE(analyzed_at)
            ORDER BY date DESC
        """, (f'-{days}',))

        return [
            {
                'date': row['date'],
                'avg_score': round(row['avg_score'], 1),
                'count': row['count'],
            }
            for row in cursor.fetchall()
        ]

    def get_top_problematic_features(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get the most frequently failing features.

        Uses a JOIN with browser_results to count unsupported instances.

        SQL: SELECT af.feature_name, af.feature_id, COUNT(*) as fail_count
             FROM analysis_features af
             JOIN browser_results br ON af.id = br.analysis_feature_id
             WHERE br.support_status = 'n'
             GROUP BY af.feature_id
             ORDER BY fail_count DESC
             LIMIT ?;

        Args:
            limit: Maximum number of features to return

        Returns:
            List of dicts with feature info and fail counts
        """
        cursor = self.conn.execute("""
            SELECT af.feature_name,
                   af.feature_id,
                   af.category,
                   COUNT(*) as fail_count
            FROM analysis_features af
            JOIN browser_results br ON af.id = br.analysis_feature_id
            WHERE br.support_status = 'n'
            GROUP BY af.feature_id
            ORDER BY fail_count DESC
            LIMIT ?
        """, (limit,))

        return [
            {
                'feature_name': row['feature_name'] or row['feature_id'],
                'feature_id': row['feature_id'],
                'category': row['category'],
                'fail_count': row['fail_count'],
            }
            for row in cursor.fetchall()
        ]

    def get_most_analyzed_files(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get the most frequently analyzed files.

        SQL: SELECT file_name, COUNT(*) as analysis_count,
                    MAX(overall_score) as best_score,
                    AVG(overall_score) as avg_score
             FROM analyses
             GROUP BY file_name
             ORDER BY analysis_count DESC
             LIMIT ?;

        Args:
            limit: Maximum number of files to return

        Returns:
            List of dicts with file info and analysis counts
        """
        cursor = self.conn.execute("""
            SELECT file_name,
                   file_type,
                   COUNT(*) as analysis_count,
                   MAX(overall_score) as best_score,
                   AVG(overall_score) as avg_score
            FROM analyses
            GROUP BY file_name
            ORDER BY analysis_count DESC
            LIMIT ?
        """, (limit,))

        return [
            {
                'file_name': row['file_name'],
                'file_type': row['file_type'],
                'analysis_count': row['analysis_count'],
                'best_score': round(row['best_score'], 1),
                'avg_score': round(row['avg_score'], 1),
            }
            for row in cursor.fetchall()
        ]

    def get_browser_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Get aggregated statistics per browser.

        Returns:
            Dict mapping browser name to stats (support counts, percentages)
        """
        # Get all distinct browsers from browser_results
        cursor = self.conn.execute("""
            SELECT browser,
                   SUM(CASE WHEN support_status = 'y' THEN 1 ELSE 0 END) as supported,
                   SUM(CASE WHEN support_status = 'a' THEN 1 ELSE 0 END) as partial,
                   SUM(CASE WHEN support_status = 'n' THEN 1 ELSE 0 END) as unsupported,
                   COUNT(*) as total
            FROM browser_results
            GROUP BY browser
        """)

        stats = {}
        for row in cursor.fetchall():
            total = row['total'] or 1
            stats[row['browser']] = {
                'supported': row['supported'],
                'partial': row['partial'],
                'unsupported': row['unsupported'],
                'total': total,
                'support_percentage': round(
                    (row['supported'] + row['partial'] * 0.5) / total * 100, 1
                ),
            }

        return stats

    def get_grade_distribution(self) -> Dict[str, int]:
        """Get distribution of grades across all analyses.

        SQL: SELECT grade, COUNT(*) as count
             FROM analyses
             GROUP BY grade
             ORDER BY grade;

        Returns:
            Dict mapping grade letters to counts
        """
        cursor = self.conn.execute("""
            SELECT grade, COUNT(*) as count
            FROM analyses
            GROUP BY grade
            ORDER BY grade
        """)

        return {row['grade']: row['count'] for row in cursor.fetchall()}

    def get_file_type_distribution(self) -> Dict[str, int]:
        """Get distribution of file types analyzed.

        SQL: SELECT file_type, COUNT(*) as count
             FROM analyses
             GROUP BY file_type;

        Returns:
            Dict mapping file type to count
        """
        cursor = self.conn.execute("""
            SELECT file_type, COUNT(*) as count
            FROM analyses
            GROUP BY file_type
        """)

        return {row['file_type']: row['count'] for row in cursor.fetchall()}

    def get_recent_activity(self, days: int = 30) -> Dict[str, int]:
        """Get analysis activity counts per day for recent period.

        Args:
            days: Number of days to look back

        Returns:
            Dict mapping date strings to counts
        """
        cursor = self.conn.execute("""
            SELECT DATE(analyzed_at) as date, COUNT(*) as count
            FROM analyses
            WHERE analyzed_at >= date('now', ? || ' days')
            GROUP BY DATE(analyzed_at)
            ORDER BY date
        """, (f'-{days}',))

        return {row['date']: row['count'] for row in cursor.fetchall()}

    def get_summary_statistics(self) -> Dict[str, Any]:
        """Get a comprehensive summary of all statistics.

        Returns:
            Dict with all key statistics combined
        """
        total = self.get_total_analyses()

        if total == 0:
            return {
                'total_analyses': 0,
                'average_score': 0,
                'best_score': 0,
                'worst_score': 0,
                'grade_distribution': {},
                'file_type_distribution': {},
                'top_problematic_features': [],
                'most_analyzed_files': [],
            }

        return {
            'total_analyses': total,
            'average_score': self.get_average_score(),
            'best_score': self.get_best_score(),
            'worst_score': self.get_worst_score(),
            'grade_distribution': self.get_grade_distribution(),
            'file_type_distribution': self.get_file_type_distribution(),
            'top_problematic_features': self.get_top_problematic_features(),
            'most_analyzed_files': self.get_most_analyzed_files(),
            'browser_statistics': self.get_browser_statistics(),
        }


# Singleton instance for convenience
_stats_service: Optional[StatisticsService] = None


def get_statistics_service() -> StatisticsService:
    """Get the singleton statistics service instance.

    Returns:
        StatisticsService instance
    """
    global _stats_service
    if _stats_service is None:
        _stats_service = StatisticsService()
    return _stats_service
