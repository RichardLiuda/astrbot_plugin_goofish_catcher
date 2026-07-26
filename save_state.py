from __future__ import annotations

import argparse
import asyncio

try:
    from .app.auth_session import (
        _resolve_platform_profile,
        resolve_local_storage_state_path,
        save_login_session_state,
    )
    from .app.login_session import (
        GoofishLoginSession,
        resolve_save_state_executable_path,
    )
    from .app.platforms.registry import PLATFORM_GOOFISH, PLATFORM_TAOBAO
except ImportError:
    from app.auth_session import (
        _resolve_platform_profile,
        resolve_local_storage_state_path,
        save_login_session_state,
    )
    from app.login_session import GoofishLoginSession, resolve_save_state_executable_path
    from app.platforms.registry import PLATFORM_GOOFISH, PLATFORM_TAOBAO


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="手动登录并保存登录态（storage_state）到插件数据目录",
    )
    parser.add_argument(
        "--platform",
        choices=[PLATFORM_GOOFISH, PLATFORM_TAOBAO],
        default=PLATFORM_GOOFISH,
        help="登录平台（默认 goofish；taobao 保存到 storage_state.taobao.json）",
    )
    return parser.parse_args()


async def main():
    args = parse_args()
    executable_path = resolve_save_state_executable_path()
    stable_state_path = resolve_local_storage_state_path(args.platform)
    profile = _resolve_platform_profile(args.platform)
    session = GoofishLoginSession(executable_path=executable_path, profile=profile)
    try:
        print(f"登录平台: {profile.display_name} ({args.platform})")
        if executable_path is not None:
            print(f"使用自定义浏览器: {executable_path}")
        else:
            print("使用 Playwright 自带 Chromium")

        await session.start_login_session()
        print("请在浏览器完成登录，回到终端按 Enter 保存登录态...")
        await asyncio.get_running_loop().run_in_executor(None, input)
        result = await save_login_session_state(
            session,
            stable_path=stable_state_path,
        )
        print(f"已保存: {result['saved_path']}")
    finally:
        await session.close()


if __name__ == "__main__":
    asyncio.run(main())
