import asyncio
import sys
from asyncio import Semaphore

from loguru import logger
from playwright.async_api import async_playwright, expect

from db import config
from db.db_api import load_profiles, get_extension_id, get_wallets_by_name
from db.models import Profile
from file_functions.utils import get_file_names


backpack_extension_id = get_extension_id('Backpack')
url = f"chrome-extension://{backpack_extension_id}/options.html?onboarding=true"
logger.debug(f"url: {url}")
args = []
extension_paths = get_file_names(config.EXTENSIONS_DIR, files=False)
if extension_paths:
    extension_paths = ",".join(extension_paths)  # Объединяем все пути через запятую
    extension_arg = f"--load-extension={extension_paths}"
    args.append(extension_arg)
    args.append(f"--disable-extensions-except={extension_paths}", )
    logger.debug(f"Loading extensions: {extension_arg}")
logger.debug(f'args: {args}')

async def install_extension_for_profile(profile: Profile, password: str, semaphore: Semaphore, seed_or_pk: str):
    try:
        async with (semaphore):
            wallets_for_profile = get_wallets_by_name(profile.name)
            seed = wallets_for_profile.solana_seed_phrase
            pk = wallets_for_profile.solana_private_key

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
                    slow_mo=150,
                    # channel='chrome',
                    args=args
                )
                backpack_page = await context.new_page()
                await backpack_page.bring_to_front()
                await backpack_page.goto(url)

                if await backpack_page.get_by_text('Already setup').is_visible(timeout=3000):
                    logger.info(f"Backpack already set up for profile {profile.name}")
                    return

                # Wait for browser loading
                await asyncio.sleep(3)
                # Import Wallet
                await backpack_page.locator("//button").last.click(timeout=5000)

                # Solana
                await backpack_page.locator("//button").first.click(timeout=5000)

                if seed_or_pk == 'seed':
                    # Import Seed Phrase
                    await backpack_page.locator("//button").first.click(timeout=5000)

                    seeds = seed.split(' ')
                    for i, seed in enumerate(seeds):
                        await backpack_page.locator("//input").nth(i).fill(seed, timeout=5000)

                    await backpack_page.locator("//button").nth(1).click(timeout=5000)
                    await asyncio.sleep(5)

                    # Check funded wallet
                    await backpack_page.get_by_role('checkbox').first.click(timeout=5000)
                    # Import
                    await backpack_page.locator("//button").last.click(timeout=5000)

                if seed_or_pk == 'pk':
                    await backpack_page.locator("//button").nth(2).click(timeout=5000)
                    await backpack_page.locator("//textarea").first.fill(pk, timeout=5000)

                    # Import
                    await backpack_page.locator("//button").first.click(timeout=5000)

                # Password
                await backpack_page.locator("//input").nth(0).fill(password, timeout=5000)
                await backpack_page.locator("//input").nth(1).fill(password, timeout=5000)

                await backpack_page.locator("//input").nth(2).click(timeout=5000)
                await backpack_page.locator("//button").nth(1).click(timeout=5000)

                await expect(backpack_page.locator('//*[@id="options"]'
                                                   '/span/span/div/div/div/div/div/div[1]/div/div[2]/div/span/button')
                             ).to_be_visible(timeout=5000)

                logger.success(f"Successfully imported Backpack Wallet for profile {profile.name}")

    except Exception as e:
        logger.error(f"Failed to install extension for profile {profile.name}: {e}")


async def backpack():
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
    asyncio.run(backpack())
