from __future__ import annotations

import asyncio
import unittest
from unittest.mock import AsyncMock, Mock, patch

from app import browser_agent


class BrowserAgentCleanupTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self._saved_count = browser_agent._active_agents

    def tearDown(self) -> None:
        browser_agent._active_agents = self._saved_count

    def _agent_with_mocks(self, *, page_close_effect=None):
        agent = browser_agent.GofishBrowserAgent(llm_call=None)
        page = Mock(close=AsyncMock(side_effect=page_close_effect))
        context = Mock(close=AsyncMock())
        browser = Mock(close=AsyncMock())
        pw = Mock(stop=AsyncMock())
        agent._page, agent._context = page, context
        agent._browser, agent._playwright = browser, pw
        return agent, page, context, browser, pw

    async def test_aexit_swallows_close_errors_and_decrements(self) -> None:
        browser_agent._active_agents = 3
        agent, page, context, browser, pw = self._agent_with_mocks(
            page_close_effect=RuntimeError("already closed")
        )

        await agent.__aexit__(None, None, None)

        context.close.assert_awaited_once()
        browser.close.assert_awaited_once()
        pw.stop.assert_awaited_once()
        self.assertIsNone(agent._page)
        self.assertIsNone(agent._playwright)
        self.assertEqual(browser_agent._active_agents, 2)

    async def test_aexit_stays_consistent_when_cancelled_mid_close(self) -> None:
        """清理途中被 cancel（如 SSE 断连触发 bg_task.cancel()）：剩余
        close/stop 仍要执行、字段重置、计数递减，最后重抛取消信号。"""
        browser_agent._active_agents = 3
        agent, page, context, browser, pw = self._agent_with_mocks(
            page_close_effect=asyncio.CancelledError()
        )

        with self.assertRaises(asyncio.CancelledError):
            await agent.__aexit__(None, None, None)

        context.close.assert_awaited_once()
        browser.close.assert_awaited_once()
        pw.stop.assert_awaited_once()
        self.assertIsNone(agent._page)
        self.assertIsNone(agent._playwright)
        self.assertEqual(browser_agent._active_agents, 2)

    async def test_aenter_cleans_up_when_launch_fails(self) -> None:
        """__aenter__ 中途失败时 async with 不会调用 __aexit__，必须自行清理：
        已启动的 playwright driver 要 stop，活跃计数要减回去。"""
        browser_agent._active_agents = 0
        pw = Mock(
            chromium=Mock(launch=AsyncMock(side_effect=RuntimeError("boom"))),
            stop=AsyncMock(),
        )
        ap_factory = Mock(return_value=Mock(start=AsyncMock(return_value=pw)))
        agent = browser_agent.GofishBrowserAgent(llm_call=None, headless=True)

        with patch("playwright.async_api.async_playwright", ap_factory):
            with self.assertRaisesRegex(RuntimeError, "boom"):
                await agent.__aenter__()

        pw.stop.assert_awaited_once()
        self.assertIsNone(agent._playwright)
        self.assertEqual(browser_agent._active_agents, 0)


if __name__ == "__main__":
    unittest.main()
