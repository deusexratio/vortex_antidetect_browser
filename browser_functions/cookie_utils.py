import re
import json
from loguru import logger

def sanitize_cookie_value(cookie_data: str | list) -> list:
    """Очищает значение cookie от вложенных JSON структур"""
    try:
        # Если получили список, возвращаем как есть
        if isinstance(cookie_data, list):
            return cookie_data
            
        # Если получили строку, обрабатываем
        if isinstance(cookie_data, str):
            # Заменяем проблемные значения в JSON
            pattern = r'("value":\s*)({[^}]+})'
            
            def escape_json_value(match):
                value = match.group(2)
                # Экранируем кавычки и обрамляем в кавычки все значение
                escaped = value.replace('"', '\\"')
                return f'{match.group(1)}"{escaped}"'
            
            # Пытаемся найти и заменить все проблемные значения
            sanitized = re.sub(pattern, escape_json_value, cookie_data)
            
            try:
                # Пробуем распарсить результат
                return json.loads(sanitized)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse sanitized JSON: {e}")
                # Если не получилось, пробуем более агрессивную очистку
                sanitized = re.sub(r'("value":\s*){[^}]+}', r'\1""', cookie_data)
                return json.loads(sanitized)
                
        logger.error(f"Unexpected cookie data type: {type(cookie_data)}")
        return []
        
    except Exception as e:
        logger.error(f"Error processing cookies: {e}")
        logger.debug(f"Problematic data: {cookie_data[:200]}...")  # Показываем начало данных для отладки
        return []

def convert_cookies_to_playwright_format(cookies_data: list) -> list[dict]:
    """Конвертирует cookies в формат для Playwright"""
    try:
        playwright_cookies = []
        
        for cookie in cookies_data:
            # Пропускаем невалидные cookie
            if not isinstance(cookie, dict):
                continue
                
            # Обязательные поля
            playwright_cookie = {
                'name': str(cookie.get('name', '')),
                'value': str(cookie.get('value', '')),
                'domain': str(cookie.get('domain', '')),
                'path': str(cookie.get('path', '/')),
            }
            
            # Опциональные поля
            if 'expires' in cookie:
                try:
                    playwright_cookie['expires'] = float(cookie['expires'])
                except (ValueError, TypeError):
                    pass
                    
            if 'httpOnly' in cookie:
                playwright_cookie['httpOnly'] = bool(cookie['httpOnly'])
            if 'secure' in cookie:
                playwright_cookie['secure'] = bool(cookie['secure'])
            if 'sameSite' in cookie:
                playwright_cookie['sameSite'] = str(cookie['sameSite'])
                
            playwright_cookies.append(playwright_cookie)
            
        logger.debug(f"Converted {len(playwright_cookies)} cookies to Playwright format")
        return playwright_cookies
    except Exception as e:
        logger.error(f"Error converting cookies to Playwright format: {e}")
        return []
