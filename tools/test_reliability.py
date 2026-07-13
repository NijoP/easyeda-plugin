#!/usr/bin/env python3
"""Tests for Phase-2 reliability tools: diagnose + recover (pure logic, no git/net).
Run: python3 tools/test_reliability.py"""
import diagnose, recover


def test_classify():
    assert diagnose.classify("Unauthorized", http=401)["class"].startswith("EDA-1")
    assert diagnose.classify("", http=429)["class"] == "EDA-5"
    assert diagnose.classify("kicad-cli: command not found")["class"] == "KI-5"
    assert diagnose.classify("ModuleNotFoundError: No module named 'x'")["class"] == "SC-2"
    assert diagnose.classify("fatal: could not read Username for github")["class"] == "GIT-AUTH"
    assert diagnose.classify("some weird thing")["class"] == "SC-1"
    # retryability drives auto-recovery decisions
    assert diagnose.classify("", http=429)["retryable"] is True
    assert diagnose.classify("kicad-cli: command not found")["retryable"] is False


def test_retry():
    # transient error recovers after backoff
    calls = {"n": 0}
    def flaky():
        calls["n"] += 1
        if calls["n"] < 3:
            raise TimeoutError("timed out")
        return "done"
    r = recover.retry(flaky, attempts=3, retry_on=lambda e: True, sleep=lambda s: None)
    assert r["ok"] and r["v"] == "done" and r["attempts"] == 3

    # non-idempotent: a failed live write is NOT retried (tried exactly once)
    calls2 = {"n": 0}
    def once():
        calls2["n"] += 1
        raise ValueError("boom")
    r2 = recover.retry(once, idempotent=False, sleep=lambda s: None)
    assert r2["ok"] is False and calls2["n"] == 1 and r2["attempts"] == 1

    # non-retryable class stops after one try (via the diagnoser)
    def missing():
        raise Exception("kicad-cli: command not found")
    r3 = recover.retry(missing, attempts=3, sleep=lambda s: None)
    assert r3["ok"] is False and r3["attempts"] == 1
    assert r3["diagnosis"]["class"] == "KI-5"


if __name__ == "__main__":
    test_classify()
    test_retry()
    print("PASS — diagnose + recover: classification, backoff-retry, idempotency guard.")
