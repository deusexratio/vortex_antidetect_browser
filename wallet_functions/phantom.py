import asyncio
import sys
from asyncio import Semaphore

from loguru import logger
from playwright._impl._errors import TargetClosedError
from playwright.async_api import async_playwright, expect

from db import config
from db.db_api import load_profiles, get_extension_id, get_wallets_by_name
from db.models import Profile
from file_functions.utils import get_file_names


phantom_extension_id = get_extension_id('Phantom')
url = f"chrome-extension://{phantom_extension_id}/onboarding.html"
logger.debug(f"url: {url}")
args = []
extension_paths = get_file_names(config.EXTENSIONS_DIR, files=False)
if extension_paths:
    extension_paths = ",".join(extension_paths)  # Объединяем все пути через запятую
    extension_arg = f"--load-extension={extension_paths}"
    args.append(extension_arg)
    args.append(f"--disable-extensions-except={extension_paths}", )
    logger.debug(f"Loading extensions: {extension_arg}")
# logger.debug(f'args: {args}')


async def install_extension_for_profile(profile: Profile, password: str, semaphore: Semaphore, seed_or_pk: str):
    try:
        async with semaphore:
            wallets_for_profile = get_wallets_by_name(profile.name)
            seed: str = wallets_for_profile.solana_seed_phrase
            pk: str = wallets_for_profile.solana_seed_phrase
            # print('seed', seed)
            # print('pk', pk)
            if not seed and seed_or_pk == 'seed':
                logger.info(f'Not specified Solana seed phrase for profile {profile.name}')
                return
            if not pk and seed_or_pk == 'pk':
                logger.info(f'Not specified Solana private key for profile {profile.name}')
                return

            async with async_playwright() as p:
                context = await p.chromium.launch_persistent_context(
                    user_data_dir=profile.user_data_dir,
                    headless=False,
                    # channel='chrome',
                    args=args
                )
                phantom_page = await context.new_page()
                await phantom_page.bring_to_front()
                await phantom_page.goto(url)

                # Wait for browser loading
                await asyncio.sleep(3)

                # I already have a wallet button
                await phantom_page.locator('//button').last.click(timeout=15000)
                await asyncio.sleep(1)

                if seed_or_pk == 'seed':
                    # Import seed button
                    await phantom_page.locator('//button').nth(2).click(timeout=10000)

                    seed_list = seed.split()
                    for i in range(0, 12):
                        await phantom_page.locator('//input').nth(i).fill(seed_list[i])

                    await asyncio.sleep(1)
                    confirm_button = phantom_page.locator('//button').nth(1)
                    await confirm_button.click(timeout=3000)

                    await asyncio.sleep(3)
                    # Found account
                    await phantom_page.locator('//button').nth(2).click(timeout=10000)

                if seed_or_pk == 'pk':
                    # Import pk button
                    await phantom_page.locator('//button').nth(3).click(timeout=3000)
                    # Fill name
                    await phantom_page.locator('//input').first.fill(str(profile.name))
                    # Fill private key
                    await phantom_page.locator('//textarea').first.fill(pk)
                    # Import button
                    await phantom_page.locator('//button').nth(1).click(timeout=10000)

                # passwords
                await phantom_page.locator('//input').nth(0).fill(password)
                await phantom_page.locator('//input').nth(1).fill(password)
                await asyncio.sleep(.5)
                # checkbox
                await phantom_page.locator('//input').nth(2).click(timeout=3000)

                # Import
                await phantom_page.locator('//button').nth(1).click(timeout=10000)

                # Get started
                await asyncio.sleep(3)
                await phantom_page.locator('//button').nth(1).click(timeout=10000)
                # finish

                logger.success(f"Successfully imported Phantom Wallet for profile {profile.name}")

    except Exception as e:
        logger.error(f"Failed to import Phantom extension for profile {profile.name}: {e}")


async def phantom():
    if len(sys.argv) != 4:
        print("Usage: python install_extensions.py <extension_url>")
        sys.exit(1)

    seed_or_pk = sys.argv[1]
    password = sys.argv[2]
    threads = sys.argv[3]

    semaphore = asyncio.Semaphore(int(threads))

    tasks = [asyncio.create_task(install_extension_for_profile(profile, password, semaphore, seed_or_pk)) for profile in load_profiles()]
    logger.debug(f"Starting {len(tasks)} tasks")
    await asyncio.wait(tasks)


if __name__ == "__main__":
    asyncio.run(phantom())
