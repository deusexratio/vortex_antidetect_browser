import asyncio
import os.path
import traceback

from playwright.async_api import async_playwright
from loguru import logger

from db import config
from db.db_api import load_profiles
from db.models import Profile
from file_functions.utils import read_json


def convert_cookies_to_playwright_format(cookies_json: dict) -> list[dict]:
    """Конвертирует JSON с cookies в формат, понятный Playwright"""
    playwright_cookies = []

    for cookie in cookies_json:
        # Обязательные поля для Playwright
        playwright_cookie = {
            'name': cookie.get('name'),
            'value': cookie.get('value'),
            'domain': cookie.get('domain'),
            'path': cookie.get('path', '/'),
        }

        # Опциональные поля
        if 'expires' in cookie:
            playwright_cookie['expires'] = cookie.get('expires')
        if 'httpOnly' in cookie:
            playwright_cookie['httpOnly'] = cookie.get('httpOnly')
        if 'secure' in cookie:
            playwright_cookie['secure'] = cookie.get('secure')
        if 'sameSite' in cookie:
            playwright_cookie['sameSite'] = cookie.get('sameSite')

        playwright_cookies.append(playwright_cookie)

    return playwright_cookies


def get_cookies_for_profile(profile: Profile):
    cookie_path = os.path.join(config.COOKIES_DIR, f'{profile.name}.json')
    try:
        return read_json(cookie_path)
    except FileNotFoundError:
        logger.info(f"Not found cookies json file for profile {profile.name}")


async def import_cookies():
    async with async_playwright() as playwright:
        for profile in load_profiles():
            try:
                # if profile.proxy:
                #     proxy = Proxy.from_str(profile.proxy).as_playwright_proxy
                # else:
                #     proxy = None
                logger.debug(f"Starting to import cookies for profile {profile.name}")
                context = await playwright.chromium.launch_persistent_context(
                    profile.user_data_dir,
                    headless=True,
                    # proxy=proxy
                )

                cookies = get_cookies_for_profile(profile)
                if cookies:
                    await context.add_cookies(cookies)
                    logger.success(f"Imported cookies for profile {profile.name}")
                    # await asyncio.sleep(1000)

                else:
                    logger.info(f"Empty cookies json for profile {profile.name}")

                await context.close()

            except Exception as e:
                traceback.print_exc()
                logger.error(f"Failed importing cookies for {profile.name} because of {e}")
                continue


def main():
    # if len(sys.argv) != 2:
    #     print("Usage: python install_extensions.py <extension_url>")
    #     sys.exit(1)
    # extension_paths = sys.argv[1]
    asyncio.run(import_cookies())


if __name__ == "__main__":
    main()


# def sanitize_cookie_value(value: str) -> str:
#     """Очищает значение cookie от вложенных JSON структур"""
#     try:
#         # Пытаемся найти вложенные JSON структуры
#         pattern = r'"value":\s*({[^}]+})'
#
#         def replace_json(match):
#             # Экранируем внутренний JSON
#             inner_json = match.group(1)
#             escaped_json = inner_json.replace('"', '\\"')
#             return f'"value": "{escaped_json}"'
#
#         # Заменяем все вложенные JSON
#         sanitized = re.sub(pattern, replace_json, value)
#         print(sanitized)
#
#         # Проверяем, что результат валидный JSON
#         json.loads(sanitized)
#         return sanitized
#
#     except Exception as e:
#         # Если что-то пошло не так, можно попробовать более агрессивную очистку
#         try:
#             # Удаляем все проблемные значения
#             pattern = r'"value":\s*{[^}]+}'
#             sanitized = re.sub(pattern, '"value": "removed"', value)
#             json.loads(sanitized)
#             return sanitized
#         except:
#             # Если и это не помогло, возвращаем пустую строку или None
#             return '""'
#
#
# def get_cookies_for_profile(profile: Profile) -> list[dict]:
#     workbook = load_workbook(config.ADS_PROFILES_TABLE)
#     sheet = workbook.active
#     rows = sheet.iter_rows(min_row=2, max_row=sheet.max_row, min_col=1, max_col=3, values_only=True)
#     for row in rows:
#         print(row)
#         if str(row[0]).strip() == str(profile.name):
#             try:
#                 print(profile.name)
#                 print(row[2])
#                 cookie_string = rf"""{row[2].replace("'", '"').replace('""', '"')
#                 .replace('True', "true").replace('False', "false")}"""
#
#                 sanitized_cookie = sanitize_cookie_value(cookie_string)
#                 print(sanitized_cookie)
#
#                 parsed_cookies = json.loads(cookie_string)
#                 print(parsed_cookies)
#
#                 cookies_array = convert_cookies_to_playwright_format(parsed_cookies)
#                 print(cookies_array)
#                 return cookies_array
#             except Exception as e:
#                 print()
