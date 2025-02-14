import os
import sys
import asyncio
import random

from playwright.async_api import async_playwright, BrowserContext, expect, Page
from loguru import logger

# Определяем корневую директорию проекта
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Добавляем корневую директорию в sys.path
sys.path.append(ROOT_DIR)

from browser_functions.functions import launch_profile_async
from db.db_api import get_profile, get_extension_id
from db.models import Profile
from db import config
from file_functions.utils import get_file_names


class AbstractPizza:
    rabby_extension_id = get_extension_id('Rabby')
    pizza_url = 'https://abstract.pizza/app'
    rabby_ext_url = f'chrome-extension://{rabby_extension_id}/index.html'

    def __init__(self, context: BrowserContext, profile: Profile, password: str, rabby_or_abstract: str):
        self.context = context
        self.profile = profile
        self.password = password
        self.rabby_or_abstract = rabby_or_abstract

    async def cook(self):
        pizza_page = await self.context.new_page()
        await pizza_page.goto(self.pizza_url)

        connect_button = pizza_page.get_by_text('Connect Wallet', exact=True)
        try:
            await connect_button.click(timeout=5000)
            await self.all_connections(pizza_page)
        except:
            logger.debug(f'Profile {self.profile.name} passed connection')
            pass

        start_button = pizza_page.get_by_text('Start Making Pizza!')

        your_points_element = pizza_page.get_by_text("Your Points")
        points_count_selector = your_points_element.locator('xpath=following-sibling::*[1]')

        sleep = random.randint(5, 30)
        logger.info(f"Profile {self.profile.name} sleeping for {sleep} seconds")
        await asyncio.sleep(sleep)

        while True:
            try:
                points = await points_count_selector.text_content(timeout=5000)
                logger.info(f"Profile: {self.profile.name} starting to cook, current points: {points.strip()}")
                await start_button.click(timeout=3000)
                await asyncio.sleep(3)
                abs_page = await self.switch_to_url_page('privy', timeout_=15000)
                approve_button = abs_page.get_by_text('Approve', exact=True)
                approve_visible = await approve_button.is_visible(timeout=10000)
                while not approve_visible:
                    logger.warning(f"Profile: {self.profile.name} waiting for approve button")
                    await asyncio.sleep(3)
                    approve_visible = await approve_button.is_visible(timeout=10000)

                try:
                    await expect(approve_button).to_be_enabled()
                except:
                    pass
                await approve_button.click(timeout=3000)

                all_done = abs_page.get_by_text('All Done')
                retry_button = abs_page.get_by_text("Retry transaction")
                # await expect(abs_page.locator('//button').last).to_be_enabled()

                await asyncio.sleep(5)
                loading = await abs_page.get_by_text('Loading...').is_visible(timeout=10000)
                while loading:
                    logger.warning(f"Profile: {self.profile.name} waiting for All Done button")
                    await asyncio.sleep(3)
                    loading = await abs_page.get_by_text('Loading...').is_visible(timeout=10000)

                for i in range(1, 4):
                    try:
                        await expect(abs_page.locator('//button').last).to_have_text('Retry')
                    except:
                        pass
                    if await retry_button.is_visible(timeout=3000):
                        logger.warning(f"Profile: {self.profile.name} error, retrying {i} attempt")
                        await retry_button.click(timeout=3000)
                        await approve_button.click(timeout=3000)
                    else:
                        break
                else:
                    logger.warning(f"Attempting relogin")
                    await abs_page.close()

                    # Wallet button
                    await pizza_page.locator('//html/body/div/div[1]/header/nav/div/div/div[2]/div/div/button').click(timeout=3000)
                    await pizza_page.get_by_test_id('rk-disconnect-button').click(timeout=3000)
                    # Connect button

                    await pizza_page.locator('//html/body/div/div[1]/header/nav/div/div/div[2]/div/button').click(timeout=3000)
                    await self.all_connections(pizza_page)

                if await all_done.is_visible(timeout=10000):
                    await all_done.click()
                    logger.success(f"Profile: {self.profile.name} cooking pizza! Sleeping for 60 seconds")
                    await asyncio.sleep(55)
                    continue

            except Exception as e:
                logger.error(f"Profile: {self.profile.name} error {e}")

    async def all_connections(self, pizza_page: Page):
        if self.rabby_or_abstract == 'Rabby':
            await pizza_page.get_by_test_id('rk-wallet-option-io.rabby').click(timeout=3000)
            await self.unlock_rabby(self.password)
            await self.connect_rabby()
        if self.rabby_or_abstract == 'Abstract':
            await pizza_page.get_by_test_id("rk-wallet-option-abstract").click(timeout=3000)
            await asyncio.sleep(3)
            abs_page = await self.switch_to_url_page('privy', timeout_=15000)
            if abs_page:
                approve_button = abs_page.get_by_text('Approve', exact=True)
                try:
                    await expect(approve_button).to_be_enabled()
                except:
                    pass
                await approve_button.click(timeout=10000)

    async def switch_to_url_page(self, url, timeout_ = 60000):
        url_page = next((p for p in self.context.pages if url in p.url), None)

        if not url_page:
            try:
                url_page = await self.context.wait_for_event('page', timeout=timeout_)
            except TimeoutError:
                logger.error(f"Error: {url} page hasn't opened in {timeout_} ms.")
                return None

        if url in url_page.url:
            # await url_page.bring_to_front()
            logger.info(f"{self.profile.name} Switched to {url} page")
            return url_page
        else:
            logger.error(f"Error: found page {url_page.url} doesn't match input url {url}.")
            return None

    async def connect_rabby(self):
        rabby_page = await self.switch_to_url_page(self.rabby_extension_id)
        ignore_all = rabby_page.get_by_text('Ignore All')
        if await ignore_all.is_visible(timeout=3000):
            await ignore_all.click()

        await rabby_page.locator('//button').first.click()


    async def unlock_rabby(self, password: str):
        for i in range(5):
            try:
                logger.debug(f'Name: {self.profile.name} | Starting to unlock Rabby')
                # 'chrome-extension://acmacodkjbdgmoleebolmdjonilkdbch/index.html#/unlock'
                rabby_page = await self.context.new_page()
                await rabby_page.bring_to_front()
                await rabby_page.goto(self.rabby_ext_url)
                await asyncio.sleep(.5)

                try:
                    if await rabby_page.get_by_text("What's new").is_visible(timeout=3000):
                        await rabby_page.locator('/html/body/div[2]/div/div[2]/div/div[2]/button/span').click(
                            timeout=3000)
                except:
                    logger.warning(f"Name: {self.profile.name} | Can't close what's new")

                try:
                    await expect(rabby_page.get_by_text('No Dapp found')).not_to_be_visible()
                    # if RABBY_VERSION == 'OLD':
                    #     await expect(rabby_page.locator('//*[@id="root"]/div[1]/div[2]/div[1]')).not_to_be_visible()
                    # else:
                    #     await expect(rabby_page.locator('//*[@id="root"]/div/div[1]/div[1]/div[1]/span')).not_to_be_visible()
                except:
                    logger.success(f'Name: {self.profile.name} | Already unlocked Rabby')
                    await rabby_page.close()
                    return

                password_field = rabby_page.get_by_placeholder('Enter the Password to Unlock')
                await expect(password_field).to_be_visible()
                await password_field.fill(password)

                unlock_button = rabby_page.get_by_text('Unlock')
                await expect(unlock_button).to_be_enabled()
                await unlock_button.click()
                logger.success(f'Name: {self.profile.name} | Unlocked Rabby')

                # clean up rabby pages
                await rabby_page.close()

                titles = [await p.title() for p in self.context.pages]
                for rabby_page_index, title in enumerate(titles):
                    if 'Rabby' in title:
                        page = self.context.pages[rabby_page_index]
                        await page.close()

                break

            except Exception as e:
                logger.error(f'Name: {self.profile.name} | {e}')
                continue



async def abstract_pizza_launcher(semaphore, profile, password, rabby_or_abstract):
    async with semaphore:
        async with async_playwright() as playwright_instance:
            while True:
                try:
                    context = await launch_profile_async(profile=profile, playwright_instance=playwright_instance,
                                                         extensions=extensions,
                                                         keep_open=False, restore_pages=False)

                    pizza = AbstractPizza(context, profile, password, rabby_or_abstract)

                    await pizza.cook()
                    break

                except Exception as e:
                    logger.error(f"Profile {profile.name} {e}")
                    continue


extensions = get_file_names(config.EXTENSIONS_DIR, files=False)

async def main():
    if len(sys.argv) != 5:
        print("Usage: python abstract_pizza.py")
        sys.exit(1)
    profiles_list_str = sys.argv[1]
    password = sys.argv[2]
    threads = sys.argv[3]
    rabby_or_abstract = sys.argv[4]

    semaphore = asyncio.Semaphore(int(threads))

    profiles = []
    for profile_name in profiles_list_str.split(','):
        profiles.append(get_profile(profile_name))

    tasks = [asyncio.create_task(abstract_pizza_launcher(semaphore, profile, password, rabby_or_abstract)) for profile in profiles]
    logger.debug(f"Launching {len(tasks)} tasks")
    await asyncio.wait(tasks)


if __name__ == "__main__":
    asyncio.run(main())
