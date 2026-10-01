import json

import collect as c
import design as d


def test_full_task_grid():
    tasks = c.build_tasks(d.MODELS, d.all_queries(), d.CONDITIONS, d.REPEATS)
    assert len(tasks) == 45 * 9 * 3 * 3
    assert len({c.task_key(t) for t in tasks}) == len(tasks)


def test_prompt_is_prefix_plus_query():
    q = d.all_queries()[0]
    t = c.build_tasks(d.MODELS[:1], [q], {"P5": d.CONDITIONS["P5"]}, 1)[0]
    assert t["prompt"] == d.persona_prefix(d.CONDITIONS["P5"]) + q["text"]
    assert t["condition"] == "P5"


def write(path, rows):
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def rec(repeat, finish="stop", text="Київстар"):
    return {"model": "m", "query_id": "tel-01", "condition": "B", "repeat": repeat,
            "finish_reason": finish, "response_text": text}


def test_set_aside_incomplete_moves_truncated_errors_and_empty(tmp_path):
    path = tmp_path / "responses.jsonl"
    write(path, [rec(1), rec(2, finish="length"), rec(3, text=""), rec(4, finish="error")])
    assert c.set_aside_incomplete(path) == 3
    assert [r["repeat"] for r in c.load_jsonl(path)] == [1]
    assert len(c.load_jsonl(tmp_path / "responses_incomplete.jsonl")) == 3


def test_run_collection_skips_done(tmp_path, monkeypatch):
    path = tmp_path / "r.jsonl"
    tasks = c.build_tasks(["m"], d.all_queries()[:1], {"B": d.CONDITIONS["B"]}, 2)
    write(path, [{**tasks[0], "finish_reason": "stop", "response_text": "x"}])
    called = []
    monkeypatch.setattr(c, "call_model", lambda client, t: called.append(t) or {**t, "finish_reason": "stop", "response_text": "y"})
    monkeypatch.setattr(c, "make_client", lambda: _NullClient())
    assert c.run_collection(tasks, path, workers=1) == []
    assert [t["repeat"] for t in called] == [2]
    assert len(c.load_jsonl(path)) == 2


class _NullClient:
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

def test_wave2_tasks_are_base_and_placebo_only():
    tasks = c.tasks_for("wave2")
    assert len(tasks) == 45 * 2 * 3 * 3
    assert {t["condition"] for t in tasks} == {"B", "PL"}
