import json
import requests
from better_proxy import Proxy
from browserforge.injectors.utils import only_injectable_headers
from loguru import logger

from db.models import Profile
from db import config
from gui_functions.utils import is_dark_mode_win, is_dark_mode_mac


def get_proxy_country_timezone(proxy_str: str | None) -> str | None:
    if not proxy_str:
        return None
    
    try:
        proxy_obj = Proxy.from_str(proxy_str)
        response = requests.get(f'http://ip-api.com/json/{proxy_obj.host}')
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                timezone = data.get('timezone')
                if timezone:
                    return timezone
    except Exception as e:
        logger.warning(f"Failed to get timezone for proxy {proxy_str}: {e}")
    return None


def get_context_launch_args(profile: Profile, extensions: list[str] | None) -> dict:
    fingerprint = json.loads(profile.fingerprint)
    str_args =  [
                # '--start-maximized',
                # '--no-sandbox',
                # '--disable-setuid-sandbox',
                # '--disable-infobars',
                # '--disable-dev-shm-usage',
                # '--disable-blink-features',
                # '--disable-features=IsolateOrigins,site-per-process',
                # '--ignore-certificate-errors',
                # '--enable-features=NetworkService,NetworkServiceInProcess',
                # '--force-color-profile=srgb',
                # '--disable-web-security',
                # '--allow-running-insecure-content',
                # '--disable-site-isolation-trials',
                # f'--window-size={fingerprint["screen"]["width"]},{fingerprint["screen"]["height"]}',
                # '--app-name="Vortex Browser"',
                # f"--disable-reading-from-canvas",
                # f"--disable-webgl",
                '--disable-blink-features=AutomationControlled',
                # "--use-mock-keychain",
                f'--window-name={profile.name}',
                f'--lang=en-US' # todo: add to settings
            ]

    if extensions:
        extension_paths = ",".join(extensions)
        str_args.extend([
            f"--load-extension={extension_paths}",
            f"--disable-extensions-except={extension_paths}"
        ])
        logger.debug(f"Loading extensions: {extension_paths}")

    if config.OS_TYPE == 'win':
        color_scheme = 'dark' if is_dark_mode_win() else 'light'
    elif config.OS_TYPE == 'mac':
        color_scheme = 'dark' if is_dark_mode_mac() else 'light'
    else:
        color_scheme = 'light'

    # Get timezone from proxy if available

    pw_args = {
        'user_data_dir': profile.user_data_dir,
        'headless': False,
        'args': str_args,
        'proxy': Proxy.from_str(profile.proxy).as_playwright_proxy if profile.proxy else None,
        'user_agent': fingerprint["navigator"]["userAgent"],
        'color_scheme': color_scheme,
        'no_viewport': True,
        'extra_http_headers': only_injectable_headers(headers={
                    'Accept-Language': fingerprint['headers'].get('Accept-Language', 'en-US,en;q=0.9'),
                    **fingerprint['headers']
                }, browser_name='chrome'
                ),
        'ignore_default_args': [
                    '--enable-automation',
                    '--no-sandbox',
                    # '--disable-blink-features=AutomationControlled',
                ],
        'bypass_csp': True,
        'ignore_https_errors': True,
        'permissions': ['geolocation', 'notifications', 'camera', 'microphone', "clipboard-read", "clipboard-write"], #
        'timezone_id': get_proxy_country_timezone(profile.proxy),
        'locale': 'en-US',
        # 'channel': 'chrome',
        'accept_downloads': True,
        'downloads_path': config.DOWNLOADS_DIR,
        # **fingerprint # разворачиваем параметры фингерпринта
    }

    return pw_args
