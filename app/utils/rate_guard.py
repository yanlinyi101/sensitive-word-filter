"""
rate_guard.py — 轻量熔断器

两种触发条件（满足任一即熔断，关闭 Gemini 出口）：
  1. 短时突发：10 分钟内超过 BURST_LIMIT 次审查请求
  2. 每日上限：当日 LLM 调用次数超过 DAILY_LLM_LIMIT

熔断后 Gemini 调用被跳过（降级为纯 DFA+规则结果），不影响正常审查流程。
通过 POST /api/admin/reset（需正确密码）手动恢复。
"""

import os
import threading
import time
from collections import deque
from datetime import date


class RateGuard:
    def __init__(self):
        self._lock = threading.Lock()

        # 突发检测参数
        self._burst_limit: int = int(os.getenv("BURST_LIMIT", "30"))
        self._burst_window: int = int(os.getenv("BURST_WINDOW_SECONDS", "600"))
        self._request_times: deque = deque()

        # 每日 LLM 上限
        self._daily_llm_limit: int = int(os.getenv("LLM_DAILY_LIMIT", "300"))
        self._llm_count: int = 0
        self._llm_date: date = date.today()

        # 熔断状态
        self._tripped: bool = False
        self._trip_reason: str = ""

    # ------------------------------------------------------------------
    # 公开接口
    # ------------------------------------------------------------------

    def record_request(self) -> None:
        """每次收到 /api/review 请求时调用，检测突发流量。"""
        now = time.monotonic()
        with self._lock:
            self._request_times.append(now)
            cutoff = now - self._burst_window
            while self._request_times and self._request_times[0] < cutoff:
                self._request_times.popleft()
            if not self._tripped and len(self._request_times) >= self._burst_limit:
                self._tripped = True
                self._trip_reason = (
                    f"突发流量：{self._burst_window}s 内收到 "
                    f"{len(self._request_times)} 次请求（上限 {self._burst_limit}）"
                )

    def llm_allowed(self) -> bool:
        """调用 Gemini 前检查：熔断中或超日限则返回 False。"""
        with self._lock:
            if self._tripped:
                return False
            self._reset_daily_if_needed()
            return self._llm_count < self._daily_llm_limit

    def record_llm_call(self) -> None:
        """每次实际发出 Gemini 请求后调用。"""
        with self._lock:
            self._reset_daily_if_needed()
            self._llm_count += 1
            if not self._tripped and self._llm_count >= self._daily_llm_limit:
                self._tripped = True
                self._trip_reason = (
                    f"每日 LLM 调用上限：已调用 {self._llm_count} 次"
                    f"（上限 {self._daily_llm_limit}）"
                )

    def status(self) -> dict:
        with self._lock:
            self._reset_daily_if_needed()
            return {
                "tripped": self._tripped,
                "trip_reason": self._trip_reason,
                "llm_calls_today": self._llm_count,
                "daily_llm_limit": self._daily_llm_limit,
                "recent_requests_in_window": len(self._request_times),
                "burst_limit": self._burst_limit,
                "burst_window_seconds": self._burst_window,
            }

    def reset(self) -> None:
        with self._lock:
            self._tripped = False
            self._trip_reason = ""
            self._request_times.clear()

    # ------------------------------------------------------------------
    # 内部
    # ------------------------------------------------------------------

    def _reset_daily_if_needed(self) -> None:
        """必须在 _lock 持有时调用。"""
        today = date.today()
        if today != self._llm_date:
            self._llm_count = 0
            self._llm_date = today


# 全局单例
rate_guard = RateGuard()
