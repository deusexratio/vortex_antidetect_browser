import os
import sys
from pathlib import Path


if getattr(sys, 'frozen', False):
    ROOT_DIR = Path(sys.executable).parent.absolute()
else:
    ROOT_DIR = Path(__file__).parent.parent.absolute()

DB_FOLDER_DIR = os.path.join(ROOT_DIR, 'db')
LOG_FILE = os.path.join(ROOT_DIR, 'log.txt')
DB_DIR = os.path.join(DB_FOLDER_DIR, 'profiles.db')
USER_DATA_DIR = os.path.join(DB_FOLDER_DIR, 'browser_data')
ASSETS_DIR = os.path.join(DB_FOLDER_DIR, 'assets')
USER_FILES_DIR = os.path.join(ROOT_DIR, 'user_files')
IMPORT_TABLE = os.path.join(USER_FILES_DIR, 'profiles.xlsx')
EXTENSIONS_DIR = os.path.join(USER_FILES_DIR, 'extensions')
ADS_PROFILES_TABLE = os.path.join(USER_FILES_DIR, 'profiles_ads.xlsx')
COOKIES_DIR = os.path.join(USER_FILES_DIR, 'cookies')
X_USERNAMES_TXT = os.path.join(USER_FILES_DIR, 'x_usernames_for_following.txt')
FANTASY_BACKUP = os.path.join(USER_FILES_DIR, 'fantasy_private_keys.xlsx')
DOWNLOADS_DIR = os.path.join(USER_FILES_DIR, 'downloads')

OS_TYPE = 'win' if sys.platform.startswith('win') else 'mac' if sys.platform.startswith(
    'darwin') else 'linux' if sys.platform.startswith('linux') else 'unknown'

# no traceback in logs
sys.tracebacklimit = 0
