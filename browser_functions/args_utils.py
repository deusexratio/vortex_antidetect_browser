import json
import sys

from better_proxy import Proxy
from browserforge.injectors.utils import only_injectable_headers
from loguru import logger

from db.models import Profile
from db import config
from gui_functions.utils import is_dark_mode_win, is_dark_mode_mac


def get_context_launch_args(profile: Profile, extensions: list[str] | None) -> dict:
    fingerprint = json.loads(profile.fingerprint)
    str_args =  [
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
        extension_paths = ",".join(extensions)
        str_args.extend([
            f"--load-extension={extension_paths}",
            f"--disable-extensions-except={extension_paths}"
        ])
        logger.debug(f"Loading extensions: {extension_paths}")

    if config.OS_TYPE == 'win':
        if is_dark_mode_win():
            color_scheme = 'dark'
        else:
            color_scheme = 'light'

    elif config.OS_TYPE == 'mac':
        if is_dark_mode_mac():
            color_scheme = 'dark'
        else:
            color_scheme = 'light'

    else:
        color_scheme = 'light'

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
        'permissions': ['geolocation', 'notifications', 'camera', 'microphone'],
        'timezone_id': None,
        'locale': 'en-US',
        # **fingerprint # разворачиваем параметры фингерпринта
    }

    return pw_args
