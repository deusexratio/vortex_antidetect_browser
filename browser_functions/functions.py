import asyncio
from datetime import datetime
import json

from playwright.async_api import Playwright
from loguru import logger

from browser_functions.args_utils import get_context_launch_args
from browser_functions.patch import InjectFunction
from db.models import Profile, db
from browser_functions.cookie_utils import sanitize_cookie_value, convert_cookies_to_playwright_format


async def launch_profile_async(playwright_instance: Playwright,
                               profile: Profile,
                               extensions: list[str] | None,
                               keep_open: bool = True,
                               restore_pages: bool = True):
    """
    Launches browser for profile
    Args:
        profile:
        playwright_instance:
        extensions:
        keep_open:
        restore_pages:

    Returns:
        context: BrowserContext
    """
    logger.debug(f"Starting profile {profile.name}...")
    try:
        args = get_context_launch_args(profile, extensions)

        context = await playwright_instance.chromium.launch_persistent_context(**args)

        profile.last_opening_time = datetime.now().replace(microsecond=0)
        db.commit()

        try:
            fingerprint = json.loads(profile.fingerprint)
            # await context.add_init_script(InjectFunction(fingerprint))
            await context.add_init_script("""
            const getParameter = WebGLRenderingContext.prototype.getParameter;
                   WebGLRenderingContext.prototype.getParameter = function(parameter) {
                   if (parameter === 37445) return "NVIDIA GeForce RTX 3060"; // Подмена GPU
                        return getParameter.apply(this, arguments);
                };

                HTMLCanvasElement.prototype.toDataURL = function() {
                    return "data:image/png;base64,blocked";
                };

                if (window.RTCPeerConnection) {
                    window.RTCPeerConnection = function() {
                        return null;
                    };
                }
                
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => false
                });
                Object.defineProperty(navigator, 'automationControlled', {
                    get: () => null
                });
            //    window.chrome = {
            //        runtime: {}
            //    };
            """)

            if restore_pages:
                logger.debug(f"Restoring previously opened tabs {profile.page_urls}")
                # Открываем страницы и держим браузер открытым
                for page_url in profile.page_urls or ['https://www.browserscan.net/']:
                    page = await context.new_page()
                    try:
                        await page.goto(page_url)
                    except Exception as e:
                        # logger.error(f"Profile {profile.name} error {e}, waiting for 60 seconds until closing")
                        # await asyncio.sleep(60)
                        if 'ERR_TIMED_OUT' in str(e):
                            logger.error(f"Profile {profile.name} proxy doesn't work")
                            break
                        # await page.goto('http://eth0.me/')
            else:
                page = await context.new_page()

            # Закрываем стартовую about:blank
            for page in context.pages:
                if page.url == 'about:blank':
                    await page.close()

            if keep_open:
                while True:
                    await asyncio.sleep(0.25)
                    pages = context.pages
                    if not pages:
                        db.commit()
                        break
                    profile.page_urls = [
                        page.url
                        for page in pages
                        if (page.url != 'about:blank' and
                            "chrome-extension://" not in page.url and
                            "chrome-error://" not in page.url)
                    ]
            else:
                return context

        except Exception as e:
            logger.error(f"Error in profile {profile.name}: {e}")
            # if context:
            #     await context.close()


    except Exception as e:
        logger.exception(f'Profile {profile.name} error: {e}')
        return None



def close_profile(profile: Profile, active_sessions: dict):
    if profile.id in active_sessions:
        active_sessions[profile.id].close()
        del active_sessions[profile.id]
        print(f"Profile {profile.id} {profile.name} closed!")


async def import_cookies(context, cookies_data):
    """Импортирует cookies в контекст браузера"""
    try:
        # Очищаем и конвертируем cookies
        cookies = sanitize_cookie_value(cookies_data)
        playwright_cookies = convert_cookies_to_playwright_format(cookies)
        
        if playwright_cookies:
            # Добавляем cookies в контекст
            await context.add_cookies(playwright_cookies)
            logger.success(f"Successfully imported {len(playwright_cookies)} cookies")
        else:
            logger.warning("No valid cookies to import")
            
    except Exception as e:
        logger.error(f"Error importing cookies: {e}")


# async def launch_synced_profiles(main_profile: Profile, follower_profiles: list[Profile], extensions: list[str]):
#     """Запускает профили в синхронизированном режиме"""
#     try:
#         async with async_playwright() as p:
#             main_profile_args = get_context_launch_args(main_profile, extensions)
#
#             # Запускаем главный профиль
#             main_context = await p.chromium.launch_persistent_context(**main_profile_args)
#
#             # Запускаем профили-последователи
#             follower_contexts = []
#             for profile in follower_profiles:
#                 follower_profile_args = get_context_launch_args(profile, extensions)
#
#                 context = await p.chromium.launch_persistent_context(**follower_profile_args)
#                 follower_contexts.append(context)
#
#             # Создаем начальные страницы
#             await main_context.new_page()
#             for context in follower_contexts:
#                 await context.new_page()
#
#             # Инициализируем синхронизатор
#             # from browser_functions.sync_actions import ActionSynchronizer
#             # synchronizer = ActionSynchronizer(main_context, follower_contexts)
#
#             from browser_functions.sync_actions_win import ActionSynchronizerWin
#             synchronizer = ActionSynchronizerWin(main_context, follower_contexts)
#             synchronizer.start()
#
#             # Держим браузеры открытыми
#             try:
#                 while main_context.pages:  # Пока есть хотя бы одна страница в главном контексте
#                     await asyncio.sleep(0.25)
#                     # Обновляем URL'ы страниц
#                     main_profile.page_urls = [
#                         page.url for page in main_context.pages
#                         if page.url != 'about:blank' and 'chrome-extension://' not in page.url
#                     ]
#                     for profile, context in zip(follower_profiles, follower_contexts):
#                         profile.page_urls = [
#                             page.url for page in context.pages
#                             if page.url != 'about:blank' and 'chrome-extension://' not in page.url
#                         ]
#                     db.commit()
#             finally:
#                 synchronizer.stop()
#                 # Закрываем все контексты
#                 await main_context.close()
#                 for context in follower_contexts:
#                     await context.close()
#
#     except Exception as e:
#         logger.error(f"Error in synced profiles: {e}")
