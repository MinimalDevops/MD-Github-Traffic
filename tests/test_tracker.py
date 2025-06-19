import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import github_traffic_tracker as tracker


def test_load_repositories(tmp_path, monkeypatch):
    yaml_content = """\
repos:
  - owner: foo
    repo: bar
  - owner: baz
    repo: qux
"""
    yaml_file = tmp_path / "repos.yaml"
    yaml_file.write_text(yaml_content)
    monkeypatch.chdir(tmp_path)
    repos = tracker.load_repositories()
    assert repos == [("foo", "bar"), ("baz", "qux")]


def test_fetch_github_traffic(monkeypatch):
    class MockResponse:
        def __init__(self, data):
            self._data = data

        def json(self):
            return self._data

        def raise_for_status(self):
            pass

    def mock_get(url, headers):
        if url.endswith("/views"):
            return MockResponse({"views": [{"timestamp": "2024-06-01T00:00:00Z", "count": 1, "uniques": 1}]})
        return MockResponse({"clones": [{"timestamp": "2024-06-01T00:00:00Z", "count": 2, "uniques": 2}]})

    monkeypatch.setattr(tracker.requests, "get", mock_get)
    views, clones = tracker.fetch_github_traffic("foo", "bar", "token")
    assert views[0]["count"] == 1
    assert clones[0]["count"] == 2


def test_upsert_traffic_metric(monkeypatch):
    executed = {}

    class MockConn:
        def execute(self, sql, params):
            executed.update(params)

        def commit(self):
            executed["committed"] = True

    conn = MockConn()
    tracker.upsert_traffic_metric(conn, "foo/bar", "2024-06-01", 1, 1, 2, 2)
    assert executed["repo_name"] == "foo/bar"
    assert executed["committed"] is True


def test_main_missing_token(monkeypatch, caplog):
    monkeypatch.setattr(tracker, "GITHUB_TOKEN", None)
    caplog.set_level("ERROR")
    tracker.main()
    assert any("GITHUB_TOKEN not set" in m for m in caplog.messages)
