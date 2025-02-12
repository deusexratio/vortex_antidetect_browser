import sys
import traceback
import asyncio

from better_proxy import Proxy
from playwright.async_api import async_playwright
from loguru import logger

from db.db_api import get_profile
from file_functions.Import import get_profiles_from_excel
from db import config


async def import_cookies(x_or_discord: str):
    async with async_playwright() as playwright:
        for profile_xlsx in get_profiles_from_excel(config.IMPORT_TABLE):
            try:
                if ((x_or_discord == 'X' and not profile_xlsx.x_cookie)
                        or (x_or_discord == 'Discord' and not profile_xlsx.discord_cookie)):
                    logger.info(f"Empty {x_or_discord} token for profile {profile_xlsx.name}")
                    continue

                profile = get_profile(profile_xlsx.name)

                logger.debug(f"Starting to import {x_or_discord} cookies for profile {profile.name}")
                context = await playwright.chromium.launch_persistent_context(
                    profile.user_data_dir,
                    headless=True,
                    proxy=Proxy.from_str(profile.proxy).as_playwright_proxy
                )

                if x_or_discord == 'X':
                    cookies = profile_xlsx.x_cookie

                else: # Discord only now
                    cookies = profile_xlsx.discord_cookie
                    token = cookies[0]['value']
                    # Открываем Discord
                    page = await context.new_page()
                    await page.goto("https://discord.com/app")

                    # Устанавливаем токен в localStorage
                    await page.evaluate(f"""
                        () => {{
                            window.localStorage.setItem('token', '"{token}"');
                        }}
                    """)

                    # Перезагружаем страницу, чтобы Discord подхватил токен
                    await page.reload()

                await context.add_cookies(cookies)
                logger.success(f"Imported {x_or_discord} cookies for profile {profile.name}")

                await context.close()

            except Exception as e:
                traceback.print_exc()
                logger.error(f"Failed importing cookies for {profile.name} because of {e}")
                continue


def main():
    if len(sys.argv) != 2:
        print("Usage: python install_extensions.py <extension_url>")
        sys.exit(1)
    x_or_discord = sys.argv[1]

    asyncio.run(import_cookies(x_or_discord))


if __name__ == "__main__":
    main()
