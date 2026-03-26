from __future__ import annotations

import asyncio

try:
    from .app.auth_session import (
        resolve_local_storage_state_path,
        save_login_session_state,
    )
    from .app.login_session import (
        GoofishLoginSession,
        resolve_save_state_executable_path,
    )
except ImportError:
    from app.auth_session import (
        resolve_local_storage_state_path,
        save_login_session_state,
    )
    from app.login_session import GoofishLoginSession, resolve_save_state_executable_path


async def main():
    executable_path = resolve_save_state_executable_path()
    stable_state_path = resolve_local_storage_state_path()
    session = GoofishLoginSession(executable_path=executable_path)
    try:
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
