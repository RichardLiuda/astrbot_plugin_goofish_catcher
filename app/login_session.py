from __future__ import annotations

import asyncio
import base64
import json
import logging
import os
import selectors
import shutil
import socket
import subprocess
import sys
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from uuid import uuid4

try:
    from astrbot.api import logger
except ModuleNotFoundError:
    logger = logging.getLogger("astrbot_plugin_goofish_catcher")

PLUGIN_NAME = "astrbot_plugin_goofish_catcher"
PROVIDER_MODE_PLAYWRIGHT_LOCAL = "playwright_local"
DEFAULT_LOGIN_URL = "https://www.goofish.com/search?q=%E9%97%B2%E9%B1%BC"
DEFAULT_VIEWPORT = {"width": 1280, "height": 960}
_LOGIN_STATUS_API_MARKERS = (
    "mtop.taobao.idlemessage.pc.loginuser.get",
    "mtop.idle.web.user.page.nav",
)
_EMBEDDED_LOGIN_MARKERS = (
    "passport.goofish.com/mini_login.htm",
    "alibaba-login-box",
)

# Button texts that indicate a one-click / quick login option is available.
# Clicking one of these should log the user in without QR scanning.
_QUICK_LOGIN_TEXTS = (
    "快速进入",
    "快速登录",
    "一键登录",
    "快捷登录",
)


def get_astrbot_root() -> Path:
    if root := os.getenv("ASTRBOT_ROOT"):
        return Path(root).expanduser().resolve()
    return Path(__file__).resolve().parents[4]


def load_local_plugin_config() -> dict[str, Any]:
    config_path = (
        get_astrbot_root()
        / "data"
        / "config"
        / f"{PLUGIN_NAME}_config.json"
    )
    if not config_path.exists():
        return {}
    raw = json.loads(config_path.read_text(encoding="utf-8-sig"))
    if not isinstance(raw, dict):
        raise RuntimeError("local plugin config root must be a JSON object")
    return raw


def load_worker_config() -> dict[str, Any]:
    config_path = Path(
        os.getenv("GOOFISH_WORKER_CONFIG", "worker_config.json")
    ).expanduser()
    if not config_path.exists():
        return {}
    raw = json.loads(config_path.read_text(encoding="utf-8-sig"))
    if not isinstance(raw, dict):
        raise RuntimeError("worker config root must be a JSON object")
    return raw


def normalize_executable_path(executable_path: Path | str | None) -> Path | None:
    if executable_path is None:
        return None

    candidate = Path(executable_path).expanduser()
    if not candidate.exists():
        raise RuntimeError(f"configured browser executable does not exist: {candidate}")
    if not candidate.is_file():
        raise RuntimeError(f"configured browser executable is not a file: {candidate}")
    return candidate


def resolve_save_state_executable_path() -> Path | None:
    env_value = os.getenv("GOOFISH_WORKER_EXECUTABLE_PATH")
    if env_value is not None:
        raw_path = env_value.strip()
    else:
        local_config = load_local_plugin_config()
        if (
            local_config.get("provider_mode") == PROVIDER_MODE_PLAYWRIGHT_LOCAL
            and str(local_config.get("playwright_executable_path", "")).strip()
        ):
            raw_path = str(local_config.get("playwright_executable_path", "")).strip()
        else:
            raw_path = str(load_worker_config().get("executable_path", "")).strip()

    if not raw_path:
        return None
    return normalize_executable_path(raw_path)


# Shared Chromium launch args for every browser this plugin starts (login,
# scraping provider, LLM browser-use agent) — keep them in one place so the
# Docker/Xvfb workarounds below apply consistently:
# --disable-dev-shm-usage: Docker's default /dev/shm is 64MB, too small for
#   Chromium's shared memory usage; this makes it fall back to /tmp instead of
#   crashing (e.g. on page.screenshot()) —
#   see https://github.com/GoogleChrome/lighthouse-ci/issues/193
# --disable-gpu: under Xvfb (no real GPU) Chromium's GPU compositing path is
#   unreliable and intermittently fails page.screenshot() with "Unable to
#   capture screenshot"; forcing software rendering fixes this consistently.
BASE_LAUNCH_ARGS: tuple[str, ...] = (
    "--disable-blink-features=AutomationControlled",
    "--disable-dev-shm-usage",
    "--disable-gpu",
)


def build_login_launch_args(*, force_direct: bool = False) -> list[str]:
    args = list(BASE_LAUNCH_ARGS)
    if force_direct:
        args.extend(
            [
                "--no-proxy-server",
                "--proxy-server=direct://",
                "--proxy-bypass-list=*",
            ]
        )
    return args


_VIRTUAL_DISPLAY_START_TIMEOUT_SEC = 10
_virtual_display_lock = threading.Lock()
_virtual_display_proc: subprocess.Popen | None = None
_external_display_logged = False
# 记录自启 Xvfb 的 DISPLAY 值。放在 os.environ 而非模块全局：AstrBot 热重载插件
# 会重新 import 本模块（模块全局全部重置），但 os.environ 和自启的 Xvfb 子进程
# 随宿主进程存续——靠这个标记在重载后仍能识别"这个 DISPLAY 是我们自己起的"，
# 从而在它死亡后重启，而不是误判为外部显示、永久失效。
_XVFB_MARKER_ENV = "GOOFISH_XVFB_DISPLAY"


def _reap_xvfb(proc: subprocess.Popen) -> None:
    """Terminate a half-started Xvfb and reap it so it doesn't linger as a
    zombie until the interpreter's next Popen cleanup pass."""
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            pass


def _wait_display_ready(read_fd: int, timeout_sec: float) -> bool:
    """Wait for Xvfb to write its display number to the -displayfd pipe.

    用 selectors（Linux 上是 epoll）而非 select.select：后者受 FD_SETSIZE=1024
    限制，长驻进程 fd 号超过 1024 时会直接抛 ValueError。
    """
    sel = selectors.DefaultSelector()
    try:
        sel.register(read_fd, selectors.EVENT_READ)
        return bool(sel.select(timeout_sec))
    finally:
        sel.close()


def _xvfb_display_alive(display: str) -> bool:
    """Probe whether the X server behind ``display`` (e.g. ":99") still accepts
    connections on its unix socket. Used after a plugin hot-reload, when the
    Popen handle for our own Xvfb has been lost with the old module instance."""
    name = display.lstrip(":").split(".", 1)[0]
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.settimeout(1)
    try:
        sock.connect(f"/tmp/.X11-unix/X{name}")
        return True
    except OSError:
        return False
    finally:
        sock.close()


def ensure_virtual_display() -> None:
    """Lazily start a process-wide throwaway Xvfb display so headed Playwright
    browsers can launch on a Linux box with no X server (typical for AstrBot
    deployed via Docker with no desktop environment).

    Every headed browser this plugin launches (login, the adopted long-lived
    scraping browser, the LLM browser-use agent) must run headed rather than
    headless=True, since goofish's passport page detects and blocks headless
    Chromium. The display is started once per process and left running for
    the process lifetime — it is cheap, and the adopted login browser keeps
    using it long after the login step itself finishes. If the Xvfb we started
    dies (e.g. OOM killer inside a memory-tight container), the next call
    detects it via poll() and starts a fresh one instead of failing forever.
    """
    global _virtual_display_proc, _external_display_logged

    if sys.platform != "linux":
        return

    with _virtual_display_lock:
        proc = _virtual_display_proc
        if proc is not None:
            if proc.poll() is None:
                return
            # 我们启动的 Xvfb 已退出（例如容器内存紧张被 OOM killer 杀掉）。
            # 丢掉失效的 DISPLAY 并重新启动，否则后续所有 headed 启动会永远失败。
            logger.warning(
                "[goofish_catcher][login_session] previously started Xvfb "
                "(DISPLAY=%s) exited with code %s; restarting",
                os.environ.get("DISPLAY"),
                proc.returncode,
            )
            _virtual_display_proc = None
            os.environ.pop("DISPLAY", None)
            os.environ.pop(_XVFB_MARKER_ENV, None)

        display = os.environ.get("DISPLAY")
        if display:
            if display == os.environ.get(_XVFB_MARKER_ENV):
                # 这是我们之前自启的 Xvfb，但 Popen 句柄已随插件热重载丢失，
                # 只能通过 unix socket 探活。活着就直接沿用。
                if _xvfb_display_alive(display):
                    return
                logger.warning(
                    "[goofish_catcher][login_session] previously auto-started "
                    "Xvfb (DISPLAY=%s) is no longer alive after plugin reload; "
                    "restarting",
                    display,
                )
                os.environ.pop("DISPLAY", None)
                os.environ.pop(_XVFB_MARKER_ENV, None)
            else:
                # 外部已有 DISPLAY（宿主 X server 或镜像预置的环境变量），跳过自启。
                # 注意：部分镜像会预置 DISPLAY=:0 却没有真实 X server，这种情况
                # 浏览器仍会启动失败——log 一句方便排查时定位到这里。
                if not _external_display_logged:
                    _external_display_logged = True
                    logger.info(
                        "[goofish_catcher][login_session] existing DISPLAY=%s "
                        "detected, skip auto-starting Xvfb",
                        display,
                    )
                return

        xvfb_path = shutil.which("Xvfb")
        if xvfb_path is None:
            raise RuntimeError(
                "未检测到 DISPLAY 环境变量，且系统未安装 Xvfb（无桌面环境下运行闲鱼登录/抓取浏览器"
                "需要一个虚拟显示）。请安装后重试，例如 Debian/Ubuntu: "
                "apt-get install -y xvfb；CentOS/RHEL: yum install -y xorg-x11-server-Xvfb。"
            )

        read_fd, write_fd = os.pipe()
        try:
            try:
                proc = subprocess.Popen(
                    [xvfb_path, "-displayfd", str(write_fd), "-screen", "0", "1280x960x24", "-nolisten", "tcp"],
                    pass_fds=(write_fd,),
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            finally:
                # 无论 Popen 成败都要关父进程侧的写端：成功时让子进程持有唯一
                # 写端（子进程退出 → read 端立刻 EOF），失败时避免泄漏。
                os.close(write_fd)

            if not _wait_display_ready(read_fd, _VIRTUAL_DISPLAY_START_TIMEOUT_SEC):
                _reap_xvfb(proc)
                raise RuntimeError(
                    f"启动 Xvfb 虚拟显示超时（{_VIRTUAL_DISPLAY_START_TIMEOUT_SEC}s 内未就绪），"
                    "请检查系统是否正确安装了 Xvfb"
                )
            display_number = os.read(read_fd, 32).decode().strip()
        finally:
            # read_fd 的关闭放在最外层 finally：Popen 本身抛异常（如容器内存
            # 紧张时 fork 报 ENOMEM）时也不泄漏。
            os.close(read_fd)

        if not display_number:
            _reap_xvfb(proc)
            raise RuntimeError("启动 Xvfb 虚拟显示失败，未能获取 display 编号")

        os.environ["DISPLAY"] = f":{display_number}"
        os.environ[_XVFB_MARKER_ENV] = f":{display_number}"
        _virtual_display_proc = proc
        logger.info(
            "[goofish_catcher][login_session] auto-started Xvfb on display :%s",
            display_number,
        )


@dataclass(slots=True)
class LoginSessionSnapshot:
    page_url: str
    screenshot_base64: str


class GoofishLoginSession:
    def __init__(
        self,
        *,
        executable_path: Path | str | None = None,
        user_data_dir: Path | str | None = None,
        force_direct: bool = False,
        proxy: str | None = None,
        login_url: str = DEFAULT_LOGIN_URL,
    ) -> None:
        self.executable_path = normalize_executable_path(executable_path)
        self.user_data_dir = (
            Path(user_data_dir).expanduser()
            if user_data_dir is not None
            else None
        )
        self.force_direct = force_direct
        self.proxy = proxy
        self.login_url = login_url
        self._playwright: Any | None = None
        self._browser: Any | None = None
        self._context: Any | None = None
        self._page: Any | None = None

    @property
    def page_url(self) -> str:
        if self._page is None:
            return ""
        return str(getattr(self._page, "url", "") or "")

    async def start_login_session(self) -> LoginSessionSnapshot:
        if self._page is not None:
            return await self.capture_snapshot()

        try:
            from playwright.async_api import async_playwright
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "playwright is not installed. "
                "Run: uv pip install -r requirements.txt && "
                "uv run python -m playwright install chromium chromium-headless-shell"
            ) from exc

        try:
            # to_thread：Xvfb 启动失败路径最长可阻塞 ~20s（等待超时 + reap），
            # 不能在事件循环线程上同步执行。
            await asyncio.to_thread(ensure_virtual_display)
            self._playwright = await async_playwright().start()
            launch_kwargs: dict[str, Any] = {
                "headless": False,
                "args": build_login_launch_args(force_direct=self.force_direct),
            }
            if self.executable_path is not None:
                launch_kwargs["executable_path"] = str(self.executable_path)
            if self.proxy:
                # Route the login browser through the configured upstream proxy so
                # the session cookie is bound to the same egress IP the worker uses.
                launch_kwargs["proxy"] = {"server": self.proxy}

            if self.user_data_dir is not None:
                self.user_data_dir.mkdir(parents=True, exist_ok=True)
                self._context = await self._playwright.chromium.launch_persistent_context(
                    str(self.user_data_dir),
                    viewport=DEFAULT_VIEWPORT,
                    **launch_kwargs,
                )
                self._browser = self._context.browser
                self._page = (
                    self._context.pages[0]
                    if getattr(self._context, "pages", None)
                    else None
                )
                if self._page is None:
                    self._page = await self._context.new_page()
            else:
                self._browser = await self._playwright.chromium.launch(**launch_kwargs)
                self._context = await self._browser.new_context(
                    viewport=DEFAULT_VIEWPORT
                )
                self._page = await self._context.new_page()
            await self._page.goto(
                self.login_url,
                wait_until="domcontentloaded",
                timeout=30_000,
            )
            await self._settle_page()
            return await self.capture_snapshot()
        except Exception:
            await self.close()
            raise

    async def capture_snapshot(self) -> LoginSessionSnapshot:
        screenshot_base64 = await self.capture_screenshot_base64()
        return LoginSessionSnapshot(
            page_url=self.page_url,
            screenshot_base64=screenshot_base64,
        )

    async def capture_screenshot_base64(self) -> str:
        if self._page is None:
            raise RuntimeError("login session has not been started")
        await self._settle_page()
        image_bytes = await self._page.screenshot(
            type="jpeg",
            quality=70,
            full_page=False,
        )
        return base64.b64encode(image_bytes).decode("ascii")

    async def save_storage_state(self, target_path: Path | str) -> Path:
        if self._context is None:
            raise RuntimeError("login session has not been started")

        target = Path(target_path).expanduser()
        target.parent.mkdir(parents=True, exist_ok=True)
        temp_path = target.parent / f".{target.name}.{uuid4().hex}.tmp"
        try:
            await self._context.storage_state(path=str(temp_path))
            os.replace(temp_path, target)
            return target
        except Exception:
            if temp_path.exists():
                temp_path.unlink(missing_ok=True)
            raise

    async def validate_login(self) -> dict[str, Any]:
        if self._context is None:
            raise RuntimeError("login session has not been started")

        page = self._page
        if page is None:
            page = await self._context.new_page()
            self._page = page

        auth_flags: set[str] = set()
        captcha_flags: set[str] = set()
        payload_rets: dict[str, str] = {}
        payload_hits: set[str] = set()

        def _on_frame_navigated(frame) -> None:
            frame_url = str(getattr(frame, "url", "") or "")
            if _is_auth_url(frame_url):
                auth_flags.add(frame_url)
            if _is_captcha_url(frame_url):
                captcha_flags.add(frame_url)

        async def _on_response(response) -> None:
            url = str(getattr(response, "url", "") or "")
            if _is_auth_url(url):
                auth_flags.add(url)
            if _is_captcha_url(url):
                captcha_flags.add(url)

            lowered = url.lower()
            if not any(marker in lowered for marker in _LOGIN_STATUS_API_MARKERS):
                return

            try:
                payload = await response.json()
            except Exception:
                return
            if not isinstance(payload, dict):
                return
            payload_rets[url] = _payload_ret_summary(payload)
            matched_marker = _match_login_status_api(url)
            if matched_marker is not None:
                payload_hits.add(matched_marker)
            if _payload_requires_login(payload):
                auth_flags.add(f"payload:{payload_rets[url]}")
            if _payload_indicates_captcha(payload):
                captcha_flags.add(f"payload:{payload_rets[url]}")

        on = getattr(page, "on", None)
        if callable(on):
            on("framenavigated", _on_frame_navigated)
            on("response", _on_response)

        await page.goto(
            self.login_url,
            wait_until="domcontentloaded",
            timeout=30_000,
        )
        await self._settle_page()

        current_url = str(getattr(page, "url", "") or "")
        frame_urls = _collect_frame_urls(page)
        try:
            html = await page.content()
        except Exception:
            html = ""
        lowered_html = html.lower()
        reason_text = "; ".join(payload_rets.values()) if payload_rets else "-"
        logger.info(
            "[goofish_catcher] validate_login result probe: page_url=%s hits=%s auth_flags=%s captcha_flags=%s frame_urls=%s payloads=%s",
            current_url,
            sorted(payload_hits),
            sorted(auth_flags),
            sorted(captcha_flags),
            frame_urls,
            payload_rets,
        )

        if auth_flags or _is_auth_url(current_url) or any(
            _is_auth_url(frame_url) for frame_url in frame_urls
        ) or any(marker in lowered_html for marker in _EMBEDDED_LOGIN_MARKERS):
            return {
                "ok": False,
                "code": "AUTH_REQUIRED",
                "reason": reason_text if payload_rets else "登录态尚未生效，页面仍出现登录提示",
                "page_url": current_url,
                "frame_urls": frame_urls,
                "payload_rets": payload_rets,
            }

        if captcha_flags or _is_captcha_url(current_url) or (
            "验证码" in html or "滑块" in html or "captcha" in lowered_html
        ):
            return {
                "ok": False,
                "code": "CAPTCHA",
                "reason": reason_text if payload_rets else "登录校验期间触发验证码或风控",
                "page_url": current_url,
                "frame_urls": frame_urls,
                "payload_rets": payload_rets,
            }

        missing_hits = [
            marker for marker in _LOGIN_STATUS_API_MARKERS if marker not in payload_hits
        ]
        if missing_hits:
            return {
                "ok": False,
                "code": "AUTH_REQUIRED",
                "reason": "登录校验缺少关键接口成功响应："
                + ", ".join(missing_hits),
                "page_url": current_url,
                "frame_urls": frame_urls,
                "payload_rets": payload_rets,
            }

        if payload_rets:
            return {
                "ok": True,
                "code": "OK",
                "reason": reason_text,
                "page_url": current_url,
                "frame_urls": frame_urls,
                "payload_rets": payload_rets,
            }

        return {
            "ok": False,
            "code": "AUTH_REQUIRED",
            "reason": "未观察到登录态成功响应，请确认扫码后页面已完成登录",
            "page_url": current_url,
            "frame_urls": frame_urls,
            "payload_rets": payload_rets,
        }

    async def close(self) -> None:
        if self._context is not None:
            await self._context.close()
            self._context = None
        elif self._browser is not None:
            await self._browser.close()
        self._browser = None
        self._page = None
        if self._playwright is not None:
            await self._playwright.stop()
            self._playwright = None

    def detach_runtime(self) -> dict[str, Any]:
        runtime = {
            "playwright": self._playwright,
            "browser": self._browser,
            "context": self._context,
            "page": self._page,
        }
        self._playwright = None
        self._browser = None
        self._context = None
        self._page = None
        return runtime

    async def _settle_page(self) -> None:
        if self._page is None:
            return
        await self._page.wait_for_timeout(1200)
        try:
            await self._page.wait_for_load_state("networkidle", timeout=3000)
        except Exception:
            await self._page.wait_for_timeout(600)

    async def try_quick_login(self) -> bool:
        """Click a quick-login button if one is visible on the current page.

        Returns True if a button was found and clicked (page may have changed).
        Should be called after start_login_session(); if it returns True the
        caller must re-validate with validate_login() to confirm success.
        """
        if self._page is None:
            return False
        for text in _QUICK_LOGIN_TEXTS:
            try:
                locator = self._page.get_by_text(text, exact=True).first
                if await locator.count() > 0:
                    logger.info(
                        "[goofish_catcher] quick login option found: %r, clicking", text
                    )
                    await locator.click(timeout=3_000)
                    await self._settle_page()
                    return True
            except Exception as exc:
                logger.debug(
                    "[goofish_catcher] quick login click failed for %r: %s", text, exc
                )
        return False


def _payload_ret_summary(payload: dict[str, Any]) -> str:
    ret = payload.get("ret")
    if isinstance(ret, list):
        return " | ".join(str(item) for item in ret[:3]) or "-"
    text = str(ret or "").strip()
    return text or "-"


def _payload_requires_login(payload: dict[str, Any]) -> bool:
    ret_text = _payload_ret_summary(payload).lower()
    return any(
        marker in ret_text
        for marker in (
            "fail_sys_session_expired",
            "fail_sys_illegal_access",
            "session过期",
            "请登录",
            "need_login",
        )
    )


def _payload_indicates_captcha(payload: dict[str, Any]) -> bool:
    ret_text = _payload_ret_summary(payload).lower()
    return any(marker in ret_text for marker in ("captcha", "验证码", "滑块"))


def _is_auth_url(url: str) -> bool:
    lowered = str(url or "").lower()
    if not lowered:
        return False
    parsed = urlparse(lowered)
    host = parsed.netloc
    path = parsed.path or ""
    if "passport.goofish.com" in host and (
        "mini_login.htm" in path or path == "/login" or path.startswith("/login/")
    ):
        return True
    if "goofish.com" in host and "mini_login.htm" in path:
        return True
    if "goofish.com" in host and "member/login" in path:
        return True
    return False


def _is_captcha_url(url: str) -> bool:
    lowered = str(url or "").lower()
    if not lowered:
        return False
    parsed = urlparse(lowered)
    host = parsed.netloc
    path = parsed.path or ""
    return bool(
        ("cf.aliyun.com" in host and "nocaptcha" in path)
        or "captcha" in path
    )


def _collect_frame_urls(page) -> list[str]:
    try:
        frames = list(getattr(page, "frames", []) or [])
    except Exception:
        return []
    urls: list[str] = []
    for frame in frames:
        try:
            url = str(getattr(frame, "url", "") or "").strip()
        except Exception:
            url = ""
        if url:
            urls.append(url)
    return urls


def _match_login_status_api(url: str) -> str | None:
    lowered = str(url or "").lower()
    for marker in _LOGIN_STATUS_API_MARKERS:
        if marker in lowered:
            return marker
    return None
