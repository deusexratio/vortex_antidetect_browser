import re
import site
import sys
from pathlib import Path
from random import randrange
import json

from browserforge.injectors.utils import utils_js
from loguru import logger

CONTEXT_RE_PATTERN = re.compile(
    r'.*\s_context?\s*\(world\)\s*\{(?:[^}{]+|\{(?:[^}{]+|\{[^}{]*\})*\})*\}'
)
ON_CLEAR_PATTERN = re.compile(r'.\s_onClearLifecycle?\s*\(\)\s*\{')

CONTEXT_REPLACEMENT_CODE = """ async _context(world) {
    if (this._isolatedContext === undefined) {
        const worldName = 'utility';
        const result = await this._page._delegate._mainFrameSession._client.send(
            'Page.createIsolatedWorld',
            {
                frameId: this._id,
                grantUniveralAccess: true,
                worldName
            }
        );
        const crModule = require('./chromium/crExecutionContext');
        const domModule = require('./dom');
        const crContext = new crModule.CRExecutionContext(
            this._page._delegate._mainFrameSession._client,
            { id: result.executionContextId }
        );
        this._isolatedContext = new domModule.FrameExecutionContext(
            crContext,
            this,
            worldName
        );
    }
    return this._isolatedContext;
} """

ON_CLEAR_REPLACEMENT_CODE = """ _onClearLifecycle() {
    this._isolatedContext = undefined;
"""


class StealthPlaywrightPatcher:
    """
    A class for stealth modification of certain Playwright files.
    It updates JavaScript logic to disable excessive Runtime.enable calls
    and configures isolated contexts.
    """

    def __init__(self):
        """
        Initializes the logger and determines the path to the site-packages directory.
        """
        self.site_packages_path = self._find_site_packages()

    def _find_site_packages(self) -> Path:
        """
        Returns the path to the site-packages directory, taking into account the operating system.
        """
        packages = site.getsitepackages()
        if not packages:
            raise RuntimeError("Unable to determine the site-packages path.")
        return Path(packages[0] if sys.platform != "win32" else packages[1])

    def _generate_path(self, filename: str, subfolder: str | None = "chromium") -> Path:
        """
        Constructs the full path to Playwright files (driver/package/lib/server).
        Subfolder can be specified if needed.
        """
        base_path = self.site_packages_path / "playwright" / "driver" / "package" / "lib" / "server"
        return base_path / subfolder / filename if subfolder else base_path / filename

    def _safe_replace(self, target: Path, old: str, new: str) -> None:
        """
        Replaces 'old' with 'new' only if 'new' is not already present in the file.
        """
        with open(target, encoding="utf-8") as f:
            content = f.read()
        if new not in content:
            updated_content = content.replace(old, new)
            with open(target, "w", encoding="utf-8") as fw:
                fw.write(updated_content)
            logger.info(f"Replaced '{old}' with '{new}' in {target}")
        else:
            logger.info(f"Skipping: '{new}' is already present in {target}")

    def _patch_runtime_methods(self) -> None:
        """
        Finds and comments out Runtime.enable calls in the Chromium-related source files.
        """
        self._safe_replace(
            target=self._generate_path("crDevTools.js"),
            old="session.send('Runtime.enable')",
            new="/*session.send('Runtime.enable')*/"
        )
        cr_page_path = self._generate_path("crPage.js")
        self._safe_replace(
            target=cr_page_path,
            old="this._client.send('Runtime.enable', {}),",
            new="/*this._client.send('Runtime.enable', {}),*/"
        )
        self._safe_replace(
            target=cr_page_path,
            old="session._sendMayFail('Runtime.enable');",
            new="/*session._sendMayFail('Runtime.enable');*/"
        )
        self._safe_replace(
            target=self._generate_path("crServiceWorker.js"),
            old="session.send('Runtime.enable', {}).catch(e => {});",
            new="/*session.send('Runtime.enable', {}).catch(e => {});*/"
        )

    def _patch_context(self) -> None:
        """
        Modifies frames.js:
        1) Overrides the _context method to create isolated contexts.
        2) Updates _onClearLifecycle to reset the isolated context.
        """
        frames_path = self._generate_path("frames.js", subfolder=None)
        with open(frames_path, encoding="utf-8") as f:
            frames_code = f.read()
        if "_isolatedContext = undefined" not in frames_code:
            frames_code = CONTEXT_RE_PATTERN.sub(CONTEXT_REPLACEMENT_CODE, frames_code, count=1)
            frames_code = ON_CLEAR_PATTERN.sub(ON_CLEAR_REPLACEMENT_CODE, frames_code, count=1)
            with open(frames_path, "w", encoding="utf-8") as fw:
                fw.write(frames_code)
            logger.info(f"File {frames_path} was successfully patched.")
        else:
            logger.info(
                f"File {frames_path} already contains the necessary modifications. Skipping...",
            )

    def apply_patches(self) -> None:
        """
        The main method to apply all patches:
        1) Comments out Runtime.enable calls.
        2) Configures the isolated context in frames.js.
        """
        logger.info("[PATCH] Starting stealth modification of the Playwright driver...")
        self._patch_runtime_methods()
        self._patch_context()
        logger.info("[PATCH] All necessary changes have been applied.")


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
