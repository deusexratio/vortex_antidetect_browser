import os
import sys
import asyncio
import random

from playwright.async_api import async_playwright, BrowserContext
from loguru import logger

from file_functions.utils import get_file_names

# Определяем корневую директорию проекта
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Добавляем корневую директорию в sys.path
sys.path.append(ROOT_DIR)

from browser_functions.functions import launch_profile_async
from db.db_api import get_profile, get_extension_id
from db.models import Profile
from db import config


class TurboTap:
    backpack_extension_id = get_extension_id('Backpack')
    turbo_url = 'https://tap.eclipse.xyz/'

    def __init__(self, context: BrowserContext, profile: Profile, range_from: int, range_to: int, password: str):
        self.context = context
        self.profile = profile
        self.range_from = range_from
        self.range_to = range_to
        self.password = password

    async def tap(self):
        taps_amount = random.randint(self.range_from, self.range_to)

        try:
            backpack_page = await self.unlock_backpack()
        except Exception as e:
            logger.warning(f"Error unlocking Backpack: {e}. Unlock it by hand or stop.")

            turbo_page = await self.context.new_page()
            await turbo_page.goto(self.turbo_url)

            await self.connect_backpack(turbo_page, backpack_page)
            await self.log_in(turbo_page, backpack_page)

            while True:
                bull = turbo_page.locator('//canvas').first
                await bull.click()
                await asyncio.sleep(.3)


    async def unlock_backpack(self):
        url = f"chrome-extension://{self.backpack_extension_id}/popup.html"

        backpack_page = await self.context.new_page()
        await backpack_page.goto(url)

        while True:
            try:
                if await backpack_page.locator('//*[@id="root"]/span[1]/span/div/div/div[7]/div/div/div[2]/div[1]/div/'
                                               'div[2]/div[2]/div/div/div/div[2]/div/div[1]/div/div/div/div/div/div/'
                                               'div[1]/div/div[2]/div[2]/div/div/div/div[2]/div/div[1]/div/div[2]/'
                                               'div[1]/div/div/div[1]/div/div[1]/div/div[1]/div[1]/div[1]/span').is_visible():
                    return backpack_page

                await backpack_page.locator('//input').fill(self.password)

                await backpack_page.locator('//*[@id="root"]/span[1]/'
                                        'span/div/div/div[2]/div[2]/div[1]/div/div[2]/form/div[2]').click(timeout=3000)
                return backpack_page
            except Exception as e:
                logger.warning(f"Error unlocking Backpack: {e}. Unlock it by hand or stop. You have 20 seconds until next try")
                await asyncio.sleep(20)

    async def connect_backpack(self, turbo_page, backpack_page):
        pass

    async def log_in(self, turbo_page, backpack_page):
        await turbo_page.get_by_text('I have').click(timeout=1000)
        await turbo_page.get_by_text('Backpack').click(timeout=1000)
        await turbo_page.get_by_test_id('select-hardware-wallet-connect-button').click(timeout=1000)

        ### add connecting wallet from scratch

        await turbo_page.goto("https://tap.eclipse.xyz/")
        await turbo_page.get_by_text('I have').click(timeout=1000)
        await turbo_page.get_by_text('Backpack').click(timeout=1000)
        await turbo_page.get_by_test_id('select-hardware-wallet-connect-button').click(timeout=1000)

        login_button = turbo_page.get_by_text('Log in', exact=True)
        if await login_button.is_visible(timeout=10000):
            await login_button.dblclick(timeout=1000)
            approve_button = backpack_page.get_by_text('Approve', exact=True)
            if approve_button.is_visible(timeout=1000):
                await approve_button.click(timeout=3000)


async def turbo_tap_launcher(semaphore, profile, range_from, range_to, password):
    async with semaphore:
        async with async_playwright() as playwright_instance:
            while True:
                try:
                    context = await launch_profile_async(profile=profile, playwright_instance=playwright_instance,
                                                         extensions=extensions,
                                                         keep_open=False, restore_pages=False)

                    taps = TurboTap(context, profile, range_from, range_to, password)

                    await taps.tap()
                    logger.success(f"Profile {profile.name} finished all taps!")
                    break

                except Exception as e:
                    logger.error(f"Profile {profile.name} {e}")
                    continue


extensions = get_file_names(config.EXTENSIONS_DIR, files=False)


async def main():
    if len(sys.argv) != 5:
        print("Usage: python turbo_tap.py")
        sys.exit(1)

    profiles_list_str = sys.argv[1]
    taps_range = sys.argv[2]
    password = sys.argv[3]
    threads = sys.argv[4]

    semaphore = asyncio.Semaphore(int(threads))

    taps_range = taps_range.split('-')
    range_from, range_to = int(taps_range[0]), int(taps_range[1])

    profiles = []
    for profile_name in profiles_list_str.split(','):
        profiles.append(get_profile(profile_name))

    tasks = [asyncio.create_task(turbo_tap_launcher(semaphore, profile, range_from, range_to, password)) for profile in profiles]
    logger.debug(f"Launching {len(tasks)} tasks")
    await asyncio.wait(tasks)

if __name__ == "__main__":
    asyncio.run(main())
