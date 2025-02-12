import os
import sys
import traceback
import asyncio
import random

from loguru import logger
from playwright.async_api import async_playwright

# Определяем корневую директорию проекта
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Добавляем корневую директорию в sys.path
sys.path.append(ROOT_DIR)

from browser_functions.functions import launch_profile_async
from db.db_api import get_profile
from db.models import Profile
from db import config
from file_functions.utils import open_txt_with_line_control, randfloat


async def mutual_following(profiles: list[Profile], x_usernames_list: list[str]):
    for profile in profiles:
        async with async_playwright() as playwright_instance:
            context = await launch_profile_async(playwright_instance, profile, extensions=None, keep_open=False)

            x_page = await context.new_page()
            await x_page.goto('https://x.com')

            await asyncio.sleep(randfloat(1, 3))
            for _ in range(random.randint(3, 7)):
                await x_page.mouse.wheel(delta_x=0, delta_y=randfloat(200, 500, 0.001))
                await asyncio.sleep(randfloat(2, 5))

            self_profile_button = x_page.get_by_test_id("AppTabBar_Profile_Link")
            await self_profile_button.click()
            await x_page.wait_for_load_state()
            profile_username = x_page.url.split('https://x.com/')[0]

            for username in x_usernames_list:
                await x_page.goto(f"https://x.com/{username}")

                await asyncio.sleep(random.randint(1, 5))

                follow_button = x_page.get_by_test_id('placementTracking').first

                try:
                    await follow_button.click(timeout=3000)
                    alert = x_page.get_by_test_id('toast')
                    if await alert.is_visible(timeout=5000):
                        logger.critical(f"Profile {profile.name}, X username {profile_username}: {await alert.text_content()}")
                    else:
                        logger.success(f'Profile {profile.name}, X username {profile_username}: Subscribed for {username}')

                except Exception as e:
                    print(e)
                    await asyncio.sleep(60)

                await asyncio.sleep(random.randint(10, 30))


def main():
    if len(sys.argv) != 2:
        print("Usage: python install_extensions.py <extension_url>")
        sys.exit(1)

    profiles_names = sys.argv[1]
    profiles_names_list = profiles_names.split(",")

    profiles = list(get_profile(profile_name) for profile_name in profiles_names_list)

    x_usernames_list = open_txt_with_line_control(config.X_USERNAMES_TXT)
    random.shuffle(x_usernames_list)
    print(x_usernames_list)
    print(profiles)

    asyncio.run(mutual_following(profiles, x_usernames_list))


if __name__ == "__main__":
    main()
