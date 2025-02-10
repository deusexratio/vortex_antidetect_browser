import asyncio
import json
from datetime import datetime
from random import randrange

from better_proxy import Proxy
from browserforge.injectors.utils import utils_js, only_injectable_headers
from playwright.async_api import async_playwright, Page
from loguru import logger

from browser_functions.patch import StealthPlaywrightPatcher
from db.models import Profile, db
from browser_functions.cookie_utils import sanitize_cookie_value, convert_cookies_to_playwright_format


StealthPlaywrightPatcher().apply_patches()

async def close_page_with_delay(page: Page, delay: float) -> None:
    await asyncio.sleep(delay)
    try:
        await page.close()
    except Exception:
        pass

async def launch_profile_async(profile: Profile, extensions: list[str] | None, keep_open: bool = True):
    logger.debug(f"Starting profile {profile.name}...")
    try:
        async with async_playwright() as p:
            fingerprint = json.loads(profile.fingerprint)

            args = [
                # '--disable-blink-features=AutomationControlled',
                # '--start-maximized',
                # '--no-sandbox',
                # '--disable-setuid-sandbox',
                # '--disable-infobars',
                # '--disable-dev-shm-usage',
                # '--disable-blink-features',
                '--disable-blink-features=AutomationControlled',
                # '--disable-features=IsolateOrigins,site-per-process',
                # '--ignore-certificate-errors',
                # '--enable-features=NetworkService,NetworkServiceInProcess',
                # '--force-color-profile=srgb',
                # '--disable-web-security',
                # '--allow-running-insecure-content',
                # '--disable-site-isolation-trials',
                # f'--window-size={fingerprint["screen"]["width"]},{fingerprint["screen"]["height"]}',
                # '--app-name="Vortex Browser"',
                f'--window-name={profile.name}',
                f'--lang=en-US' # todo: add to settings
            ]

            if extensions:
                extension_paths = ",".join(extensions)  # Объединяем все пути через запятую
                extension_arg = f"--load-extension={extension_paths}"
                args.append(extension_arg)
                logger.debug(f"Loading extensions: {extension_arg}")
                args.append(f"--disable-extensions-except={extension_paths}",)

            if profile.proxy:
                proxy = Proxy.from_str(profile.proxy).as_playwright_proxy
            else:
                proxy = None

            context = await p.chromium.launch_persistent_context(
                user_data_dir=profile.user_data_dir,
                headless=False,
                args=args,
                # channel='chrome',
                user_agent=fingerprint["navigator"]["userAgent"],
                proxy=proxy,
                color_scheme='dark',
                no_viewport=True,
                extra_http_headers=only_injectable_headers(headers={
                    'Accept-Language': fingerprint['headers'].get('Accept-Language', 'en-US,en;q=0.9'),
                    **fingerprint['headers']
                }, browser_name='chrome'
                ),
                ignore_default_args=[
                    '--enable-automation',
                    '--no-sandbox',
                    # '--disable-blink-features=AutomationControlled',
                ],
                bypass_csp=True,
                ignore_https_errors=True,
                permissions=['geolocation', 'notifications', 'camera', 'microphone'],
                timezone_id=None, # todo: add timezone to settings
                locale='en-US', # todo: add to settings
            )

            profile.last_opening_time = datetime.now().replace(microsecond=0)
            db.commit()

            try:
                # await context.add_init_script("""
                #                                 Object.defineProperty(navigator, 'webdriver', {
                #                                     get: () => undefined
                #                                 });
                #                                 Object.defineProperty(navigator, 'automationControlled', {
                #                                     get: () => false
                #                                 });
                #                                 window.chrome = {
                #                                     runtime: {}
                #                                 };
                #                             """)
                # await context.add_init_script(InjectFunction(fingerprint))

                if keep_open:
                    logger.debug(f"Restoring previously opened tabs {profile.page_urls}")
                    # Открываем страницы и держим браузер открытым
                    for page_url in profile.page_urls or ['https://amiunique.org/fingerprint']:
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
                            if (page.url != 'about:blank' and
                                "chrome-extension://" not in page.url and
                                "chrome-error://" not in page.url)
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

