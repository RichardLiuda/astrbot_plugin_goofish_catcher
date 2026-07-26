from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from app import login_session


def _fake_popen(display_text: bytes, procs: list | None = None):
    """Build a subprocess.Popen stand-in that writes straight to the real pipe fd
    the code hands it via pass_fds, without spawning any real process.

    poll() returns None (still running) so the singleton/liveness check treats
    the fake as alive; pass `procs` to capture created procs for assertions.
    """

    def _popen(cmd, pass_fds=(), **kwargs):
        os.write(pass_fds[0], display_text)
        proc = unittest.mock.Mock()
        proc.poll = unittest.mock.Mock(return_value=None)
        proc.returncode = None
        proc.terminate = unittest.mock.Mock()
        proc.wait = unittest.mock.Mock(return_value=0)
        proc.kill = unittest.mock.Mock()
        if procs is not None:
            procs.append(proc)
        return proc

    return _popen


class EnsureVirtualDisplayTest(unittest.TestCase):
    _ENV_KEYS = ("DISPLAY", login_session._XVFB_MARKER_ENV)

    def setUp(self) -> None:
        login_session._virtual_display_proc = None
        login_session._external_display_logged = False
        self._saved_env = {key: os.environ.pop(key, None) for key in self._ENV_KEYS}

    def tearDown(self) -> None:
        login_session._virtual_display_proc = None
        login_session._external_display_logged = False
        for key in self._ENV_KEYS:
            os.environ.pop(key, None)
            if self._saved_env[key] is not None:
                os.environ[key] = self._saved_env[key]

    def test_noop_on_non_linux(self) -> None:
        with patch.object(login_session.sys, "platform", "darwin"), patch(
            "subprocess.Popen"
        ) as popen:
            login_session.ensure_virtual_display()
        popen.assert_not_called()
        self.assertNotIn("DISPLAY", os.environ)

    def test_noop_when_display_already_set(self) -> None:
        os.environ["DISPLAY"] = ":7"
        with patch.object(login_session.sys, "platform", "linux"), patch(
            "subprocess.Popen"
        ) as popen:
            login_session.ensure_virtual_display()
        popen.assert_not_called()
        # 外部预置的 DISPLAY 不能被清掉
        self.assertEqual(os.environ["DISPLAY"], ":7")

    def test_raises_clear_error_when_xvfb_missing(self) -> None:
        with patch.object(login_session.sys, "platform", "linux"), patch(
            "shutil.which", return_value=None
        ):
            with self.assertRaisesRegex(RuntimeError, "Xvfb"):
                login_session.ensure_virtual_display()
        self.assertNotIn("DISPLAY", os.environ)

    def test_starts_xvfb_and_sets_display(self) -> None:
        with patch.object(login_session.sys, "platform", "linux"), patch(
            "shutil.which", return_value="/usr/bin/Xvfb"
        ), patch("subprocess.Popen", side_effect=_fake_popen(b"99\n")) as popen:
            login_session.ensure_virtual_display()
        self.assertEqual(os.environ["DISPLAY"], ":99")
        self.assertEqual(os.environ[login_session._XVFB_MARKER_ENV], ":99")
        self.assertIsNotNone(login_session._virtual_display_proc)
        popen.assert_called_once()

    def test_second_call_is_noop_singleton(self) -> None:
        with patch.object(login_session.sys, "platform", "linux"), patch(
            "shutil.which", return_value="/usr/bin/Xvfb"
        ), patch("subprocess.Popen", side_effect=_fake_popen(b"55\n")) as popen:
            login_session.ensure_virtual_display()
            login_session.ensure_virtual_display()
        popen.assert_called_once()
        self.assertEqual(os.environ["DISPLAY"], ":55")

    def test_restarts_when_started_xvfb_died(self) -> None:
        """我们启动的 Xvfb 被杀（如 OOM killer）后，下一次调用应清掉失效的
        DISPLAY 并重新拉起，而不是永远沿用死掉的显示。"""
        with patch.object(login_session.sys, "platform", "linux"), patch(
            "shutil.which", return_value="/usr/bin/Xvfb"
        ), patch("subprocess.Popen", side_effect=_fake_popen(b"42\n")) as popen:
            login_session.ensure_virtual_display()
            first_proc = login_session._virtual_display_proc
            # 模拟 Xvfb 进程退出
            first_proc.poll.return_value = 137
            first_proc.returncode = 137
            login_session.ensure_virtual_display()
        self.assertEqual(popen.call_count, 2)
        self.assertEqual(os.environ["DISPLAY"], ":42")
        self.assertEqual(os.environ[login_session._XVFB_MARKER_ENV], ":42")
        self.assertIsNot(login_session._virtual_display_proc, first_proc)

    def test_reload_adopts_own_alive_display(self) -> None:
        """热重载后模块全局重置（Popen 句柄丢失），但 marker env 表明 DISPLAY
        是我们自己起的 Xvfb 且探活成功——直接沿用，不重复拉起。"""
        os.environ["DISPLAY"] = ":88"
        os.environ[login_session._XVFB_MARKER_ENV] = ":88"
        with patch.object(login_session.sys, "platform", "linux"), patch.object(
            login_session, "_xvfb_display_alive", return_value=True
        ), patch("subprocess.Popen") as popen:
            login_session.ensure_virtual_display()
        popen.assert_not_called()
        self.assertEqual(os.environ["DISPLAY"], ":88")

    def test_reload_restarts_own_dead_display(self) -> None:
        """热重载后 marker 命中但探活失败（Xvfb 在重载后死亡）——清掉失效的
        DISPLAY/marker 并重新拉起，而不是误判为外部显示永久失效。"""
        os.environ["DISPLAY"] = ":88"
        os.environ[login_session._XVFB_MARKER_ENV] = ":88"
        with patch.object(login_session.sys, "platform", "linux"), patch.object(
            login_session, "_xvfb_display_alive", return_value=False
        ), patch("shutil.which", return_value="/usr/bin/Xvfb"), patch(
            "subprocess.Popen", side_effect=_fake_popen(b"91\n")
        ) as popen:
            login_session.ensure_virtual_display()
        popen.assert_called_once()
        self.assertEqual(os.environ["DISPLAY"], ":91")
        self.assertEqual(os.environ[login_session._XVFB_MARKER_ENV], ":91")
        self.assertIsNotNone(login_session._virtual_display_proc)

    def test_raises_on_timeout_and_leaves_display_unset(self) -> None:
        procs: list = []
        with patch.object(login_session.sys, "platform", "linux"), patch(
            "shutil.which", return_value="/usr/bin/Xvfb"
        ), patch(
            "subprocess.Popen", side_effect=_fake_popen(b"", procs)
        ), patch.object(
            login_session, "_wait_display_ready", return_value=False
        ):
            with self.assertRaisesRegex(RuntimeError, "超时"):
                login_session.ensure_virtual_display()
        self.assertNotIn("DISPLAY", os.environ)
        self.assertIsNone(login_session._virtual_display_proc)
        # 半启动的进程要 terminate 并 wait 回收，不能留僵尸
        self.assertEqual(len(procs), 1)
        procs[0].terminate.assert_called_once()
        procs[0].wait.assert_called_once()

    def test_reaps_process_when_display_number_empty(self) -> None:
        # 不 patch _wait_display_ready：fake popen 写入 b"" 后父进程关闭写端，
        # read 端 EOF 即就绪，走真实的等待路径读出空串（Xvfb 启动即崩溃的表现）
        procs: list = []
        with patch.object(login_session.sys, "platform", "linux"), patch(
            "shutil.which", return_value="/usr/bin/Xvfb"
        ), patch(
            "subprocess.Popen", side_effect=_fake_popen(b"", procs)
        ):
            with self.assertRaisesRegex(RuntimeError, "display 编号"):
                login_session.ensure_virtual_display()
        self.assertNotIn("DISPLAY", os.environ)
        self.assertIsNone(login_session._virtual_display_proc)
        self.assertEqual(len(procs), 1)
        procs[0].terminate.assert_called_once()
        procs[0].wait.assert_called_once()

    def test_popen_failure_closes_pipe_fds(self) -> None:
        """Popen 本身抛异常（如容器内存紧张 fork 报 ENOMEM）时，管道两端 fd
        都必须关闭，长驻进程反复重试不能累积泄漏。"""
        pipes: list[tuple[int, int]] = []
        real_pipe = os.pipe

        def capture_pipe():
            fds = real_pipe()
            pipes.append(fds)
            return fds

        with patch.object(login_session.sys, "platform", "linux"), patch(
            "shutil.which", return_value="/usr/bin/Xvfb"
        ), patch(
            "subprocess.Popen", side_effect=OSError("fork: ENOMEM")
        ), patch("os.pipe", side_effect=capture_pipe):
            with self.assertRaises(OSError):
                login_session.ensure_virtual_display()
        self.assertNotIn("DISPLAY", os.environ)
        self.assertEqual(len(pipes), 1)
        for fd in pipes[0]:
            with self.assertRaises(OSError):
                os.fstat(fd)


if __name__ == "__main__":
    unittest.main()
