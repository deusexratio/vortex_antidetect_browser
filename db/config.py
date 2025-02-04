import os
import sys
from pathlib import Path

if getattr(sys, 'frozen', False):
    ROOT_DIR = Path(sys.executable).parent.absolute()
else:
    ROOT_DIR = Path(__file__).parent.parent.absolute()

DB_FOLDER_DIR = os.path.join(ROOT_DIR, 'db')
DB_DIR = os.path.join(DB_FOLDER_DIR, 'profiles.db')
USER_DATA_DIR = os.path.join(DB_FOLDER_DIR, 'user_data')
USER_FILES_DIR = os.path.join(ROOT_DIR, 'user_files')
IMPORT_TABLE = os.path.join(USER_FILES_DIR, 'profiles.xlsx')
EXTENSIONS_DIR = os.path.join(USER_FILES_DIR, 'extensions')
