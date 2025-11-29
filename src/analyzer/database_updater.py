"""Database Updater for Cross Guard
Downloads and updates the Can I Use database using Git.
"""

import subprocess
import os
from pathlib import Path
from typing import Callable, Optional
import json


class DatabaseUpdater:
    """Handles updating the Can I Use database via Git."""
    
    def __init__(self, caniuse_dir: Path):
        """Initialize the database updater.
        
        Args:
            caniuse_dir: Path to the caniuse directory
        """
        self.caniuse_dir = Path(caniuse_dir)
        self.data_json_path = self.caniuse_dir / "data.json"
    
    def check_git_available(self) -> bool:
        """Check if Git is installed and available.
        
        Returns:
            bool: True if Git is available
        """
        try:
            result = subprocess.run(
                ['git', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def check_is_git_repo(self) -> bool:
        """Check if caniuse directory is a Git repository.
        
        Returns:
            bool: True if it's a Git repo
        """
        git_dir = self.caniuse_dir / ".git"
        return git_dir.exists() and git_dir.is_dir()
    
    def get_database_info(self) -> dict:
        """Get information about the current database.
        
        Returns:
            dict with database statistics
        """
        try:
            info = {
                'exists': self.data_json_path.exists(),
                'features_count': 0,
                'last_updated': None,
                'is_git_repo': self.check_is_git_repo()
            }
            
            if self.data_json_path.exists():
                with open(self.data_json_path, 'r') as f:
                    data = json.load(f)
                    info['last_updated'] = data.get('updated', 'Unknown')
                    info['features_count'] = len(data.get('data', {}))
            
            return info
            
        except Exception as e:
            return {'error': str(e)}
    
    def update_database(self, progress_callback: Optional[Callable[[str, int], None]] = None) -> dict:
        """Update the database using Git pull.
        
        Args:
            progress_callback: Optional callback function(message, percentage)
            
        Returns:
            dict with 'success', 'message', and optional 'error'
        """
        try:
            # Check if Git is available
            if not self.check_git_available():
                return {
                    'success': False,
                    'message': 'Git is not installed',
                    'error': 'Please install Git to update the database'
                }
            
            # Check if it's a Git repo
            if not self.check_is_git_repo():
                return {
                    'success': False,
                    'message': 'Not a Git repository',
                    'error': 'The caniuse directory is not a Git repository'
                }
            
            if progress_callback:
                progress_callback("Checking for updates...", 10)
            
            # Fetch latest changes
            result = subprocess.run(
                ['git', 'fetch', 'origin', 'main'],
                cwd=self.caniuse_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return {
                    'success': False,
                    'message': 'Failed to fetch updates',
                    'error': result.stderr
                }
            
            if progress_callback:
                progress_callback("Downloading updates...", 40)
            
            # Pull changes
            result = subprocess.run(
                ['git', 'pull', 'origin', 'main'],
                cwd=self.caniuse_dir,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                return {
                    'success': False,
                    'message': 'Failed to pull updates',
                    'error': result.stderr
                }
            
            if progress_callback:
                progress_callback("Update complete!", 100)
            
            # Check if anything was updated
            output = result.stdout
            if "Already up to date" in output or "Already up-to-date" in output:
                return {
                    'success': True,
                    'message': 'Database is already up to date',
                    'no_changes': True
                }
            
            # Get updated info
            info = self.get_database_info()
            
            return {
                'success': True,
                'message': f"Database updated successfully! {info.get('features_count', 0)} features available",
                'features_count': info.get('features_count', 0),
                'last_updated': info.get('last_updated', 'Unknown')
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'message': 'Update timed out',
                'error': 'The update process took too long'
            }
        except Exception as e:
            return {
                'success': False,
                'message': 'Error updating database',
                'error': str(e)
            }
