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


rabby_extension_id = get_extension_id('Rabby')
url = f"chrome-extension://{rabby_extension_id}/index.html#/new-user/guide"
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
        async with semaphore:
            wallets_for_profile = get_wallets_by_name(profile.name)
            seed = wallets_for_profile.evm_seed_phrase
            pk = wallets_for_profile.evm_private_key

            if not seed and seed_or_pk == 'seed':
                logger.info(f'Not specified EVM seed phrase for profile {profile.name}')
                return
            if not pk and seed_or_pk == 'pk':
                logger.info(f'Not specified EVM private key for profile {profile.name}')
                return

            async with async_playwright() as p:
                context = await p.chromium.launch_persistent_context(
                    user_data_dir=profile.user_data_dir,
                    headless=False,
                    # channel='chrome',
                    args=args
                )
                rabby_page = await context.new_page()
                await rabby_page.bring_to_front()
                # try:
                await rabby_page.goto(url)
                # except Exception as e:
                #     logger.error(f"Failed importing for profile {profile.name}: {e}")

                # Wait for browser loading
                await asyncio.sleep(3)
                await rabby_page.get_by_text('I already have an address').click(timeout=15000)

                if seed_or_pk == 'seed':
                    await rabby_page.get_by_text('Seed Phrase').click(timeout=3000)

                    await rabby_page.locator('//input').first.fill(seed)
                    await asyncio.sleep(1)
                    confirm_button = rabby_page.locator('//button').last
                    await confirm_button.click(timeout=3000)

                if seed_or_pk == 'pk':
                    await rabby_page.get_by_text('Private Key').click(timeout=3000)
                    await rabby_page.get_by_placeholder('Input private key').fill(pk)
                    confirm_button = rabby_page.locator('//button').last
                    await confirm_button.click(timeout=3000)

                try:
                    await rabby_page.get_by_placeholder("8 characters min").fill(password, timeout=5000)
                    await rabby_page.get_by_placeholder("Password").fill(password, timeout=5000)
                except:
                    logger.info(f"Profile {profile.name} {seed_or_pk} was already added")

                await asyncio.sleep(1)
                try:
                    await confirm_button.click(timeout=3000)
                except TargetClosedError:
                    logger.info(f"Wallet for profile {profile.name} was already recovered")
                    return

                await rabby_page.get_by_text("Get Started").click(timeout=3000)

                await expect(rabby_page.get_by_text('Rabby Wallet is Ready to Use')).to_be_visible(timeout=5000)

                logger.success(f"Successfully imported Rabby Wallet for profile {profile.name}")

    except Exception as e:
        logger.error(f"Failed to import extension for profile {profile.name}: {e}")


async def rabby():
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
    asyncio.run(rabby())
