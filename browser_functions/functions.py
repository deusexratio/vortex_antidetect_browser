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

# playwright = sync_playwright().start()
#
#
# def launch_profile(profile: Profile, extensions: list[str], active_sessions: dict):
#     browser = playwright.chromium.launch_persistent_context(
#         user_data_dir=profile.user_data_dir,
#         headless=False,
#         args=[f"--load-extension={extension_path}" for extension_path in extensions]
#     )
#     active_sessions[profile.id] = browser
#     print(f"Profile {profile.id} {profile.name} launched!")

async def close_page_with_delay(page: Page, delay: float) -> None:
    await asyncio.sleep(delay)
    try:
        await page.close()
    except Exception:
        pass

async def launch_profile_async(profile: Profile, extensions: list[str]): # , active_sessions: dict
    logger.debug(f"Starting profile {profile.name}...")  # Отладка: начало выполнения
    try:
        async with async_playwright() as p:
            fingerprint = json.loads(profile.fingerprint)

            context = await p.chromium.launch_persistent_context(
                user_data_dir=profile.user_data_dir,
                headless=False,
                args=[f"--load-extension={extension_path}" for extension_path in extensions],
                channel='chrome',
                user_agent=fingerprint["navigator"]["userAgent"], # profile.fingerprint.navigator.userAgent,
                proxy=Proxy.from_str(profile.proxy).as_playwright_proxy,
                color_scheme='dark',
                viewport={
                    'width': fingerprint["screen"]["width"], #profile.fingerprint.screen.width,
                    'height': fingerprint["screen"]["height"], #profile.fingerprint.screen.height
                },
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

            await context.add_init_script(
                InjectFunction(fingerprint),
            )

            # Закрываем стартовую about:blank
            for page in context.pages:
                if page.url == 'about:blank':
                    _ = asyncio.create_task(
                        close_page_with_delay(page, delay=0.25),
                    )

            # Открываем страницы
            for page_url in profile.page_urls or ['https://amiunique.org/fingerprint']:
                page: Page = await context.new_page()
                _ = asyncio.create_task(page.goto(page_url))

            try:
                while True:
                    await asyncio.sleep(0.25)

                    pages = context.pages
                    if not pages:
                        break

                    profile.page_urls = [
                        page.url
                        for page in pages
                        if page.url != 'about:blank'
                    ]
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
            # active_sessions[profile.id] = browser
            logger.success(f"Profile {profile.id} {profile.name} launched!")

            await asyncio.sleep(999999999)
    except Exception as e:
        logger.exception(f'Profile {profile.name} error: {e}')
    finally:
        db.commit()
        # _ = self.running_tasks.pop(profile_name, None)
        # self.save_profiles()


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
