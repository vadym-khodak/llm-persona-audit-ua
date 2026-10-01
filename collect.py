"""Збір відповідей LLM за сіткою «модель × запит × умова персони × повтор» через OpenRouter.

Мережеві функції перенесено зі статті 1 (audit.py) без змін логіки.
"""

import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import httpx
import pandas as pd

import design as d

API_URL = "https://openrouter.ai/api/v1/chat/completions"
CATALOG_URL = "https://openrouter.ai/api/v1/models"
RETRYABLE_STATUSES = (408, 429, 500, 502, 503, 504)
DATA = Path(__file__).parent / "data"
PILOT_CATEGORY = "telecom"


def build_tasks(models, queries, conditions, repeats):
    return [
        {
            "model": model,
            "query_id": q["query_id"],
            "category": q["category"],
            "intent": q["intent"],
            "condition": code,
            "repeat": r,
            "prompt": d.persona_prefix(persona) + q["text"],
        }
        for model in models
        for q in queries
        for code, persona in conditions.items()
        for r in range(1, repeats + 1)
    ]


def task_key(t):
    return (t["model"], t["query_id"], t["condition"], t["repeat"])


def load_jsonl(path):
    path = Path(path)
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def write_jsonl(path, rows, mode="w"):
    with Path(path).open(mode, encoding="utf-8") as f:
        f.writelines(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)


def fetch_catalog_prices():
    data = httpx.get(CATALOG_URL, timeout=30).json()["data"]
    return {m["id"]: {"prompt": float(m["pricing"]["prompt"]), "completion": float(m["pricing"]["completion"])} for m in data}


def estimate_cost(tasks, prices, prompt_tokens=80, completion_tokens=1200):
    rows = [
        {"model": t["model"], "cost_usd": prompt_tokens * prices[t["model"]]["prompt"] + completion_tokens * prices[t["model"]]["completion"]}
        for t in tasks
    ]
    return pd.DataFrame(rows).groupby("model").agg(calls=("cost_usd", "size"), cost_usd=("cost_usd", "sum")).round(2)


def make_client(api_key=None, timeout=180):
    api_key = api_key or os.environ["OPENROUTER_API_KEY"]
    return httpx.Client(headers={"Authorization": f"Bearer {api_key}"}, timeout=timeout)


def post_chat(client, payload, attempts=4):
    for attempt in range(attempts):
        resp = client.post(API_URL, json=payload)
        if resp.status_code == 200:
            body = resp.json()
            if "error" not in body:
                return body
        elif resp.status_code not in RETRYABLE_STATUSES:
            raise RuntimeError(f"OpenRouter {resp.status_code}: {resp.text[:300]}")
        time.sleep(2 ** attempt * 2)
    raise RuntimeError(f"OpenRouter не відповів після {attempts} спроб: {resp.status_code} {resp.text[:300]}")


def call_model(client, task, max_tokens=16000):
    payload = {
        "model": task["model"],
        "messages": [{"role": "user", "content": task["prompt"]}],
        "max_tokens": max_tokens,
        "usage": {"include": True},
    }
    body = post_chat(client, payload)
    choice = body["choices"][0]
    return {
        **task,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "served_model": body.get("model"),
        "provider": body.get("provider"),
        "finish_reason": choice.get("finish_reason"),
        "response_text": choice["message"].get("content") or "",
        "usage": body.get("usage"),
    }


def run_collection(tasks, path, workers=6):
    """Дописує результати у JSONL; зібрані ключі пропускає, тож запуск можна переривати й повторювати."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    done = {task_key(r) for r in load_jsonl(path)}
    pending = [t for t in tasks if task_key(t) not in done]
    print(f"Зібрано раніше: {len(done)}, до виконання: {len(pending)}")
    failed = []
    with make_client() as client, path.open("a", encoding="utf-8") as out, ThreadPoolExecutor(workers) as pool:
        futures = {pool.submit(call_model, client, t): t for t in pending}
        for i, future in enumerate(as_completed(futures), start=1):
            try:
                out.write(json.dumps(future.result(), ensure_ascii=False) + "\n")
                out.flush()
            except Exception as e:
                failed.append((task_key(futures[future]), repr(e)))
            if i % 50 == 0 or i == len(pending):
                print(f"  {i}/{len(pending)} (помилок: {len(failed)})")
    return failed


def is_incomplete(r):
    return r["finish_reason"] in ("length", "error") or not r["response_text"]


def set_aside_incomplete(path):
    """Переносить обрізані, помилкові й порожні відповіді в *_incomplete.jsonl, щоб наступний збір їх повторив."""
    path = Path(path)
    rows = load_jsonl(path)
    aside = [r for r in rows if is_incomplete(r)]
    if aside:
        write_jsonl(path.with_name(path.stem + "_incomplete.jsonl"), aside, mode="a")
        write_jsonl(path, [r for r in rows if not is_incomplete(r)])
    return len(aside)


def tasks_for(stage):
    queries = d.all_queries()
    if stage == "pilot":
        return build_tasks(d.MODELS, [q for q in queries if q["category"] == PILOT_CATEGORY], d.CONDITIONS, 1)
    if stage == "wave2":
        # Повторний збір бази й плацебо в один день — контроль часового дрейфу (рецензія 2026-10-01).
        return build_tasks(d.MODELS, queries, {code: d.CONDITIONS[code] for code in ("B", "PL")}, d.REPEATS)
    return build_tasks(d.MODELS, queries, d.CONDITIONS, d.REPEATS)


def main(command):
    from dotenv import find_dotenv, load_dotenv

    load_dotenv(find_dotenv(usecwd=True))
    target = DATA / {"pilot": "pilot.jsonl", "wave2": "responses_wave2.jsonl"}.get(command, "responses.jsonl")
    if command == "estimate":
        prices = fetch_catalog_prices()
        for stage in ("pilot", "full", "wave2"):
            table = estimate_cost(tasks_for(stage), prices)
            print(stage, "\n", table, "\nРазом:", table["cost_usd"].sum())
    elif command in ("pilot", "full", "wave2"):
        failed = run_collection(tasks_for(command), target)
        print("Помилки:", failed[:10], "… всього", len(failed))
    elif command == "aside":
        print("Відкладено:", set_aside_incomplete(DATA / "responses.jsonl"))
    elif command == "aside-wave2":
        print("Відкладено:", set_aside_incomplete(DATA / "responses_wave2.jsonl"))


if __name__ == "__main__":
    main(sys.argv[1])
