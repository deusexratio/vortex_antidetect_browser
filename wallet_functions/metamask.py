import asyncio
import sys
from asyncio import Semaphore

from better_proxy import Proxy
from loguru import logger
from playwright.async_api import async_playwright, expect

from db import config
from db.db_api import load_profiles, get_extension_id, get_wallets_by_name
from db.models import Profile
from file_functions.utils import get_file_names


metamask_extension_id = get_extension_id('MetaMask')
url = f"chrome-extension://{metamask_extension_id}/home.html#onboarding/welcome"
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
                    args=args,
                    # proxy=Proxy.from_str(profile.proxy).as_playwright_proxy,
                    slow_mo=300,
                    # viewport={"width": 1000, "height": 800}
                )
                metamask_page = await context.new_page()
                await metamask_page.bring_to_front()
                await metamask_page.goto(url)

                # Wait for browser loading
                await asyncio.sleep(5)

                if not await metamask_page.locator('//*[@id="app-content"]'
                                                   '/div/div[2]/div/div/div/div/div/div/ul/li[1]/div/div'
                                                   ).is_visible(timeout=10000):
                    logger.info(f"MetaMask already set up for profile {profile.name}")
                    return


                # First checkbox
                await metamask_page.locator("//input").first.click(timeout=5000)

                if seed_or_pk == 'seed':
                    # Import Existing Wallet
                    await metamask_page.locator("//button").nth(4).click(timeout=5000)

                    # No Thanks
                    await metamask_page.locator("//button").nth(1).click(timeout=5000)

                    seeds = seed.split(' ')
                    for i, seed in enumerate(seeds):
                        await metamask_page.locator("//input").nth(i * 2).fill(seed, timeout=5000)

                    # await metamask_page.locator("//input").nth(0).fill(seeds[0], timeout=5000)
                    # await metamask_page.locator("//input").nth(2).fill(seeds[1], timeout=5000)
                    # await metamask_page.locator("//input").nth(4).fill(seeds[2], timeout=5000)
                    # await metamask_page.locator("//input").nth(6).fill(seeds[3], timeout=5000)
                    # await metamask_page.locator("//input").nth(8).fill(seeds[4], timeout=5000)
                    # await metamask_page.locator("//input").nth(10).fill(seeds[5], timeout=5000)
                    # await metamask_page.locator("//input").nth(12).fill(seeds[6], timeout=5000)
                    # await metamask_page.locator("//input").nth(14).fill(seeds[7], timeout=5000)
                    # await metamask_page.locator("//input").nth(16).fill(seeds[8], timeout=5000)
                    # await metamask_page.locator("//input").nth(18).fill(seeds[9], timeout=5000)
                    # await metamask_page.locator("//input").nth(20).fill(seeds[10], timeout=5000)
                    # await metamask_page.locator("//input").nth(22).fill(seeds[11], timeout=5000)

                    # Import
                    await metamask_page.locator("//button").last.click(timeout=5000)

                    # Password
                    await metamask_page.locator("//input").nth(0).fill(password, timeout=5000)
                    await metamask_page.locator("//input").nth(1).fill(password, timeout=5000)

                    await metamask_page.locator("//input").nth(2).click(timeout=5000)
                    await metamask_page.locator("//button").last.click(timeout=5000)

                    await expect(metamask_page.get_by_test_id("onboarding-complete-done")).to_be_visible(timeout=5000)

                    await metamask_page.get_by_test_id("onboarding-complete-done").click(timeout=5000)
                    await metamask_page.get_by_test_id("pin-extension-next").click(timeout=5000)
                    await metamask_page.get_by_test_id("pin-extension-done").click(timeout=5000)

                    await metamask_page.locator("//button").last.click(timeout=5000)

                if seed_or_pk == 'pk':
                    # Create New Wallet
                    await metamask_page.locator("//button").nth(3).click(timeout=5000)

                    # No Thanks
                    await metamask_page.locator("//button").nth(1).click(timeout=5000)

                    # Password
                    await metamask_page.locator("//input").nth(0).fill(password, timeout=5000)
                    await metamask_page.locator("//input").nth(1).fill(password, timeout=5000)

                    await metamask_page.locator("//input").nth(2).click(timeout=5000)
                    await metamask_page.locator("//button").last.click(timeout=5000)

                    # Protect later
                    await metamask_page.locator("//button").nth(1).click(timeout=5000)
                    await metamask_page.locator("//input").first.click(timeout=5000)
                    await metamask_page.locator("//button").last.click(timeout=5000)

                    # Done
                    await metamask_page.get_by_test_id("onboarding-complete-done").click(timeout=5000)
                    await metamask_page.get_by_test_id("pin-extension-next").click(timeout=5000)
                    await metamask_page.get_by_test_id("pin-extension-done").click(timeout=5000)

                    await metamask_page.locator("//button").last.click(timeout=5000)

                    # await metamask_page.goto(f'chrome-extension://{metamask_extension_id}/home.html#')
                    #
                    # # Confirm
                    # await metamask_page.locator("//button").last.click(timeout=5000)

                    # Account
                    await metamask_page.locator("//button").nth(2).click(timeout=5000)

                    # Add Account
                    await metamask_page.locator("//button").last.click(timeout=5000)

                    # Import account
                    await metamask_page.locator("//button").nth(27).click(timeout=5000)

                    await metamask_page.locator("//input").first.fill(pk, timeout=5000)

                    # Import
                    await metamask_page.locator("//button").last.click(timeout=5000)

                    # await expect(metamask_page.get_by_text('Account 2')).to_be_visible(timeout=5000)

                logger.success(f"Successfully imported MetaMask Wallet for profile {profile.name}")
                await asyncio.sleep(3)

    except Exception as e:
        logger.error(f"Failed to install extension for profile {profile.name}: {e}")
        await asyncio.sleep(10000)


async def metamask():
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
    asyncio.run(metamask())
