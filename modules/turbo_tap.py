import os
import sys
import  asyncio

# Определяем корневую директорию проекта
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Добавляем корневую директорию в sys.path
sys.path.append(ROOT_DIR)

from browser_functions.functions import launch_profile_async
from db.db_api import get_profile
from db.models import Profile
from db import config
from file_functions.utils import get_file_names


async def turbo_tap(profiles: list[Profile]):
    for profile in profiles:
        context = await launch_profile_async(profile,
                                             extensions=get_file_names(config.EXTENSIONS_DIR, files=False),
                                             keep_open=False)
        turbo_page = await context.new_page()
        # 181 profile


def main():
    if len(sys.argv) != 2:
        print("Usage: python install_extensions.py <extension_url>")
        sys.exit(1)
    profiles_list_str = sys.argv[1]

    profiles = []
    for profile_name in profiles_list_str.split(','):
        profiles.append(get_profile(profile_name))

    asyncio.run(turbo_tap(profiles))


if __name__ == "__main__":
    main()
