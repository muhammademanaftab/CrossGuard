"""Updates the local Can I Use database via npm registry (with git fallback)."""

import subprocess
import os
import shutil
import tarfile
import tempfile
from pathlib import Path
from typing import Callable, Optional
from urllib.request import urlopen, Request
from urllib.error import URLError
import json


class DatabaseUpdater:
    """Pulls the latest caniuse data from npm (preferred) or git (fallback)."""

    def __init__(self, caniuse_dir: Path):
        self.caniuse_dir = Path(caniuse_dir)
        self.data_json_path = self.caniuse_dir / "data.json"
        self.package_json_path = self.caniuse_dir / "package.json"

    # --- npm methods ---

    def get_local_npm_version(self) -> Optional[str]:
        """Read the version from the local package.json (if it exists)."""
        try:
            if self.package_json_path.exists():
                with open(self.package_json_path, 'r') as f:
                    return json.load(f).get('version')
        except Exception:
            pass
        return None

    def check_npm_update(self) -> dict:
        """Check npm registry for a newer caniuse-db version."""
        from src.utils.config import NPM_REGISTRY_URL
        try:
            req = Request(NPM_REGISTRY_URL, headers={'Accept': 'application/json'})
            with urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())

            latest = data.get('version')
            local = self.get_local_npm_version()

            return {
                'success': True,
                'local_version': local,
                'latest_version': latest,
                'update_available': latest != local if (latest and local) else latest is not None,
                'tarball_url': data.get('dist', {}).get('tarball'),
            }
        except (URLError, OSError, json.JSONDecodeError) as e:
            return {'success': False, 'error': str(e)}

    def download_npm_update(self, progress_callback: Optional[Callable[[str, int], None]] = None) -> dict:
        """Download and extract the latest caniuse-db from npm."""
        if progress_callback:
            progress_callback("Checking npm registry...", 5)

        check = self.check_npm_update()
        if not check.get('success'):
            return {'success': False, 'message': 'Cannot reach npm registry', 'error': check.get('error')}

        if not check.get('update_available'):
            return {'success': True, 'message': 'Database is already up to date', 'no_changes': True}

        tarball_url = check.get('tarball_url')
        if not tarball_url:
            return {'success': False, 'message': 'No tarball URL in npm response', 'error': 'Missing dist.tarball'}

        if progress_callback:
            progress_callback("Downloading from npm...", 20)

        try:
            tmp_dir = tempfile.mkdtemp(prefix='crossguard_')
            tmp_tar = os.path.join(tmp_dir, 'caniuse-db.tgz')

            req = Request(tarball_url)
            with urlopen(req, timeout=60) as resp:
                with open(tmp_tar, 'wb') as f:
                    f.write(resp.read())

            if progress_callback:
                progress_callback("Extracting...", 60)

            with tarfile.open(tmp_tar, 'r:gz') as tar:
                tar.extractall(path=tmp_dir)

            package_dir = os.path.join(tmp_dir, 'package')
            if not os.path.isdir(package_dir):
                return {'success': False, 'message': 'Unexpected tarball structure', 'error': 'No package/ directory'}

            if progress_callback:
                progress_callback("Installing...", 80)

            self.caniuse_dir.mkdir(parents=True, exist_ok=True)

            # Copy data.json
            src_data = os.path.join(package_dir, 'data.json')
            if os.path.exists(src_data):
                shutil.copy2(src_data, str(self.data_json_path))

            # Copy features-json/
            src_features = os.path.join(package_dir, 'features-json')
            dst_features = self.caniuse_dir / 'features-json'
            if os.path.isdir(src_features):
                if dst_features.exists():
                    shutil.rmtree(str(dst_features))
                shutil.copytree(src_features, str(dst_features))

            # Copy package.json for version tracking
            src_pkg = os.path.join(package_dir, 'package.json')
            if os.path.exists(src_pkg):
                shutil.copy2(src_pkg, str(self.package_json_path))

            # Cleanup temp
            shutil.rmtree(tmp_dir, ignore_errors=True)

            if progress_callback:
                progress_callback("Update complete!", 100)

            info = self.get_database_info()
            return {
                'success': True,
                'message': f"Database updated to v{check['latest_version']}! "
                           f"{info.get('features_count', 0)} features available",
                'features_count': info.get('features_count', 0),
                'npm_version': check['latest_version'],
            }

        except Exception as e:
            # Cleanup on failure
            if 'tmp_dir' in locals():
                shutil.rmtree(tmp_dir, ignore_errors=True)
            return {'success': False, 'message': 'npm download failed', 'error': str(e)}

    # --- git methods (fallback) ---

    def check_git_available(self) -> bool:
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
        git_dir = self.caniuse_dir / ".git"
        return git_dir.exists() and git_dir.is_dir()

    def update_via_git(self, progress_callback: Optional[Callable[[str, int], None]] = None) -> dict:
        """Fetch + pull from origin/main. Returns success/failure dict."""
        try:
            if not self.check_git_available():
                return {
                    'success': False,
                    'message': 'Git is not installed',
                    'error': 'Please install Git to update the database'
                }

            if not self.check_is_git_repo():
                return {
                    'success': False,
                    'message': 'Not a Git repository',
                    'error': 'The caniuse directory is not a Git repository'
                }

            if progress_callback:
                progress_callback("Checking for updates (git)...", 10)

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
                progress_callback("Downloading updates (git)...", 40)

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

            output = result.stdout
            if "Already up to date" in output or "Already up-to-date" in output:
                return {
                    'success': True,
                    'message': 'Database is already up to date',
                    'no_changes': True
                }

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

    # --- Main entry points ---

    def get_database_info(self) -> dict:
        try:
            info = {
                'exists': self.data_json_path.exists(),
                'features_count': 0,
                'last_updated': None,
                'is_git_repo': self.check_is_git_repo(),
                'npm_version': self.get_local_npm_version(),
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
        """Try npm first, fall back to git if npm fails."""
        # Try npm first
        result = self.download_npm_update(progress_callback)
        if result.get('success'):
            return result

        # Fall back to git
        if progress_callback:
            progress_callback("npm failed, trying git...", 10)

        return self.update_via_git(progress_callback)
