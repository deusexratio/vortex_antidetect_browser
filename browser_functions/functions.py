import asyncio
import json
import threading
from random import randrange

from better_proxy import Proxy
from browserforge.injectors.utils import utils_js
# from playwright.sync_api import sync_playwright
from patchright.async_api import async_playwright, Page
from loguru import logger


from db.models import Profile, db
from db.db_api import load_profiles


async def close_page_with_delay(page: Page, delay: float) -> None:
    await asyncio.sleep(delay)
    try:
        await page.close()
    except Exception:
        pass

async def launch_profile_async(profile: Profile, extensions: list[str], keep_open: bool = True): 
    logger.debug(f"Starting profile {profile.name}...")
    try:
        async with async_playwright() as p:
            fingerprint = json.loads(profile.fingerprint)

            context = await p.chromium.launch_persistent_context(
                user_data_dir=profile.user_data_dir,
                headless=False,
                args=[f"--load-extension={extension_path}" for extension_path in extensions],
                channel='chrome',
                user_agent=fingerprint["navigator"]["userAgent"],
                proxy=Proxy.from_str(profile.proxy).as_playwright_proxy,
                color_scheme='dark',
                no_viewport=True,
                # viewport={
                #     'width': fingerprint["screen"]["width"],
                #     'height': fingerprint["screen"]["height"]
                # },
                extra_http_headers={
                    'Accept-Language': fingerprint['headers'].get(
                        'Accept-Language',
                        'en-US,en;q=0.9'
                    ),
                    **fingerprint['headers']
                },
                ignore_default_args=[
                    '--enable-automation',
                    '--no-sandbox',
                    '--disable-blink-features=AutomationControlled',
                ],
            )

            try:
                await context.add_init_script(InjectFunction(fingerprint))

                if keep_open:
                    logger.debug(f"Restoring previously opened tabs {profile.page_urls}")
                    # Открываем страницы и держим браузер открытым
                    for page_url in profile.page_urls or ['https://amiunique.org/fingerprint']:
                        page = await context.new_page()
                        await page.goto(page_url)

                    # Закрываем стартовую about:blank
                    for page in context.pages:
                        if page.url == 'about:blank':
                            await page.close()


                    while True:
                        await asyncio.sleep(0.25)
                        pages = context.pages
                        if not pages:
                            db.commit()
                            break
                        profile.page_urls = [
                            page.url
                            for page in pages
                            if page.url != 'about:blank'
                        ]
                else:
                    return context

            except Exception as e:
                logger.error(f"Error in profile {profile.name}: {e}")
                if context:
                    await context.close()
                raise

    except Exception as e:
        logger.exception(f'Profile {profile.name} error: {e}')
        return None


# def launch_profile_in_executor(profile_name, extensions: list[str]):
#     asyncio.run_coroutine_threadsafe(
#         launch_profile_async(profile_name, extensions),
#         asyncio.get_event_loop()
#     )


def close_profile(profile: Profile, active_sessions: dict):
    if profile.id in active_sessions:
        active_sessions[profile.id].close()
        del active_sessions[profile.id]
        print(f"Profile {profile.id} {profile.name} closed!")


def InjectFunction(fingerprint: dict) -> str:
    return f"""
    (()=>{{
        {utils_js()}

        const fp = {json.dumps(fingerprint)};
        const {{
            battery,
            navigator: {{
                userAgentData,
                webdriver,
                ...navigatorProps
            }},
            screen: allScreenProps,
            videoCard,
            audioCodecs,
            videoCodecs,
            mockWebRTC,
        }} = fp;

        slim = fp.slim;

        const historyLength = {randrange(1, 6)};

        const {{
            outerHeight,
            outerWidth,
            devicePixelRatio,
            innerWidth,
            innerHeight,
            screenX,
            pageXOffset,
            pageYOffset,
            clientWidth,
            clientHeight,
            hasHDR,
            ...newScreen
        }} = allScreenProps;

        const windowScreenProps = {{
            innerHeight,
            outerHeight,
            outerWidth,
            innerWidth,
            screenX,
            pageXOffset,
            pageYOffset,
            devicePixelRatio,
        }};

        const documentScreenProps = {{
            clientHeight,
            clientWidth,
        }};

        runHeadlessFixes();
        if (mockWebRTC) blockWebRTC();
        if (slim) {{
            window['slim'] = true;
        }}
        overrideIntlAPI(navigatorProps.language);
        overrideStatic();
        if (userAgentData) {{
            overrideUserAgentData(userAgentData);
        }}
        if (window.navigator.webdriver) {{
            navigatorProps.webdriver = false;
        }}
        overrideInstancePrototype(window.navigator, navigatorProps);
        overrideInstancePrototype(window.screen, newScreen);
        overrideWindowDimensionsProps(windowScreenProps);
        overrideDocumentDimensionsProps(documentScreenProps);
        overrideInstancePrototype(window.history, {{ length: historyLength }});
        overrideWebGl(videoCard);
        overrideCodecs(audioCodecs, videoCodecs);
        overrideBattery(battery);
    }})()
    """

#
# def start_profiles(selected_profiles, extensions: list[str], active_sessions: dict):
#     for profile in selected_profiles:
#         profile = next((p for p in load_profiles() if p.name == profile), None)
#         if profile.id not in active_sessions:
#             threading.Thread(
#                 target=launch_profile,
#                 args=(profile, extensions, active_sessions),
#                 daemon=True
#             ).start()
#         else:
#             print(f"Profile {profile.id} {profile.name} is already running or not found!")

async def install_extension(context, extension_url: str):
    """Устанавливает расширение из Chrome Web Store"""
    try:
        # Ждем полной инициализации браузера
        await asyncio.sleep(3)
        
        # Проверяем, что контекст все еще активен
        if not context.browser:
            logger.error("Browser context is not active")
            return
            
        # Открываем новую страницу с ожиданием готовности
        page = await context.new_page()
        await page.wait_for_load_state('domcontentloaded')
        
        # Переходим на страницу расширения
        await page.goto(extension_url, wait_until='networkidle')
        await asyncio.sleep(3)
        
        # Пробуем найти кнопку установки разными способами
        install_button = None
        selectors = [
            'div[role="button"][aria-label*="Add to Chrome"]',
            'div[role="button"][aria-label*="Add extension"]',
            'div[role="button"]:has-text("Add to Chrome")',
            'div[role="button"]:has-text("Add extension")'
        ]
        
        for selector in selectors:
            try:
                install_button = await page.wait_for_selector(selector, timeout=5000)
                if install_button:
                    break
            except:
                continue
                
        if install_button:
            await install_button.click()
            await asyncio.sleep(2)
            
            # Ищем диалог подтверждения
            confirm_dialog = await page.wait_for_selector('div[role="dialog"]', timeout=5000)
            if confirm_dialog:
                # Ищем кнопку подтверждения разными способами
                add_selectors = [
                    'div[role="button"][aria-label*="Add"]',
                    'div[role="button"]:has-text("Add")',
                    'div[role="button"]:has-text("Add extension")'
                ]
                
                add_button = None
                for selector in add_selectors:
                    try:
                        add_button = await confirm_dialog.wait_for_selector(selector, timeout=5000)
                        if add_button:
                            break
                    except:
                        continue
                
                if add_button:
                    await add_button.click()
                    await asyncio.sleep(3)
                    
                    # Ждем завершения установки
                    await page.wait_for_load_state('networkidle')
                    logger.success(f"Extension {extension_url} installed successfully")
                else:
                    logger.error("Add button not found in confirmation dialog")
            else:
                logger.error("Confirmation dialog not found")
        else:
            logger.error("Install button not found")
            
    except Exception as e:
        logger.error(f"Failed to install extension {extension_url}: {e}")
        # Делаем скриншот для отладки
        try:
            await page.screenshot(path=f"error_screenshot_{profile.name}.png")
        except:
            pass
    finally:
        try:
            if page:
                await page.close()
        except:
            pass


def install_extension_sync(context, extension_url: str):
    """Устанавливает расширение из Chrome Web Store"""
    try:
        # Ждем полной инициализации браузера
        # await asyncio.sleep(3)

        # Проверяем, что контекст все еще активен
        if not context.browser:
            logger.error("Browser context is not active")
            return

        # Открываем новую страницу с ожиданием готовности
        page = context.new_page()
        page.wait_for_load_state('domcontentloaded')

        # Переходим на страницу расширения
        page.goto(extension_url, wait_until='networkidle')
        # await asyncio.sleep(3)

        # Пробуем найти кнопку установки разными способами
        install_button = None
        selectors = [
            'div[role="button"][aria-label*="Add to Chrome"]',
            'div[role="button"][aria-label*="Add extension"]',
            'div[role="button"]:has-text("Add to Chrome")',
            'div[role="button"]:has-text("Add extension")'
        ]

        for selector in selectors:
            try:
                install_button = page.wait_for_selector(selector, timeout=5000)
                if install_button:
                    break
            except:
                continue

        if install_button:
            install_button.click()
            # await asyncio.sleep(2)

            # Ищем диалог подтверждения
            confirm_dialog = page.wait_for_selector('div[role="dialog"]', timeout=5000)
            if confirm_dialog:
                # Ищем кнопку подтверждения разными способами
                add_selectors = [
                    'div[role="button"][aria-label*="Add"]',
                    'div[role="button"]:has-text("Add")',
                    'div[role="button"]:has-text("Add extension")'
                ]

                add_button = None
                for selector in add_selectors:
                    try:
                        add_button = confirm_dialog.wait_for_selector(selector, timeout=5000)
                        if add_button:
                            break
                    except:
                        continue

                if add_button:
                    add_button.click()
                    # await asyncio.sleep(3)

                    # Ждем завершения установки
                    page.wait_for_load_state('networkidle')
                    logger.success(f"Extension {extension_url} installed successfully")
                else:
                    logger.error("Add button not found in confirmation dialog")
            else:
                logger.error("Confirmation dialog not found")
        else:
            logger.error("Install button not found")

    except Exception as e:
        logger.error(f"Failed to install extension {extension_url}: {e}")
        # Делаем скриншот для отладки
        # try:
        #     await page.screenshot(path=f"error_screenshot_{profile.name}.png")
        # except:
        #     pass
    finally:
        try:
            if page:
                page.close()
        except:
            pass

