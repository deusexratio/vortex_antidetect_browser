import asyncio
import sys
from typing import Any

from playwright.async_api import async_playwright, Playwright, BrowserContext
from loguru import logger

from db import config
from db.db_api import load_profiles
from db.models import Extension, db
from file_functions.utils import get_file_names


async def get_extension_ids(context: BrowserContext) -> dict[str, Any | None] | None:
    """
    Gets the extension id from the installed applications page chrome://extensions/
    :param context: BrowserContext
    :param extension_name: str
    :return: Extension ID: str
    """
    # logger.debug(f'GETTING "" EXTENSION ID')
    page = await context.new_page()
    try:
        await page.goto('chrome://extensions/')
        session = await context.new_cdp_session(page)

        response = await session.send('Runtime.evaluate', {
            'expression': """
        new Promise((resolve) => {
            chrome.management.getAll((items) => {
                resolve(items);
            });
        });
    """,
            'awaitPromise': True
        })


        object_id = response['result']['objectId']

        # Get the properties of the extension array
        properties_response = await session.send('Runtime.getProperties', {
            'objectId': object_id,
            'ownProperties': True  # Получаем только собственные свойства
        })
        # logger.debug(properties_response)
        # Extracting extension data
        extensions = []
        for prop in properties_response['result']:
            if 'value' in prop and prop['value']['type'] == 'object':
                extension = prop['value']
                # Extracting the properties of the extension
                extension_properties = await session.send('Runtime.getProperties', {
                    'objectId': extension['objectId'],
                    'ownProperties': True
                })

                # logger.debug(extension_properties)

                # Save the extension data
                extension_data = {}
                for ext_prop in extension_properties['result']:
                    if 'value' in ext_prop:
                        extension_data[ext_prop['name']] = ext_prop['value'].get('value', None)
                extensions.append(extension_data)

        ext_ids = {}
        # Search for the required extension and return its ID
        for extension in extensions:
            ext_name = extension.get("name")
            ext_id = extension.get("id")
            ext_ids[ext_name] = ext_id
            logger.success(f'{ext_name} EXTENSION ID: {ext_id}')
            # if extension_name.lower() in extension.get("name").lower():
            #     app_id = extension.get("id")
            #     logger.success(f'{extension_name} EXTENSION ID: {app_id}')
            #     return app_id
        return ext_ids

    except Exception as ex:
        logger.error(f' EXTENSION ID NOT FOUND')
        return None


async def run(playwright: Playwright, extension_paths: list[str]):
    profile = load_profiles()[0]

    args = []
    if extension_paths:
        extension_paths = ",".join(extension_paths)  # Объединяем все пути через запятую
        extension_arg = f"--load-extension={extension_paths}"
        args.append(extension_arg)
        args.append(f"--disable-extensions-except={extension_paths}", )
        logger.debug(f"Loading extensions: {extension_arg}")

    context = await playwright.chromium.launch_persistent_context(
        profile.user_data_dir,
        headless=False,
        args=args,
        # channel='chrome'
    )

    ext_ids = await get_extension_ids(context=context)

    await context.close()
    return ext_ids


async def get_ext_ids(extension_paths):
    async with async_playwright() as playwright:
        ext_ids = await run(playwright, extension_paths)

        return ext_ids


def main():
    # if len(sys.argv) != 2:
    #     print("Usage: python install_extensions.py <extension_url>")
    #     sys.exit(1)
    # extension_paths = sys.argv[1]
    extension_paths = get_file_names(config.EXTENSIONS_DIR, files=False)
    ext_ids = asyncio.run(get_ext_ids(extension_paths))

    for name, id_ in ext_ids.items():
        extension_instance = Extension(name=name, extension_id=id_)
        db.insert(extension_instance)

if __name__ == "__main__":
    main()


