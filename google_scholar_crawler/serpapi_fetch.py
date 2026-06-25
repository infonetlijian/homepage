#!/usr/bin/env python3
import os, json, re, time
from datetime import datetime, timezone
import requests

API_URL = "https://serpapi.com/search.json"

def to_int(val):
    if val is None:
        return None
    s = str(val)
    s = re.sub(r"[,\s]", "", s)
    return int(s)

def extract_total_citations(payload):
    # 主要路径：cited_by.table[0].citations.all
    cb = payload.get("cited_by") or {}
    table = cb.get("table")
    if isinstance(table, list) and table:
        row = table[0] or {}
        citations = row.get("citations") or {}
        total = citations.get("all") if isinstance(citations, dict) else citations
        total_int = to_int(total)
        if total_int is not None:
            return total_int
    # 备选：cited_by.value
    v = cb.get("value")
    if v is not None:
        v_int = to_int(v)
        if v_int is not None:
            return v_int
    # 兜底失败
    raise RuntimeError("Cannot locate total citations in SerpApi response")

def main():
    author_id = os.environ["GOOGLE_SCHOLAR_ID"]
    api_key = os.environ["SERPAPI_API_KEY"]

    params = {
        "engine": "google_scholar_author",
        "author_id": author_id,
        "api_key": api_key,
        # 可选参数：返回作者+作品汇总；不依赖 cookies
        "view_op": "list_works",
        "hl": "en",
    }

    # 简单重试（SerpApi 很稳，通常一次成功）
    last_err = None
    for attempt in range(1, 6):
        try:
            r = requests.get(API_URL, params=params, timeout=30)
            r.raise_for_status()
            data = r.json()
            total = extract_total_citations(data)
            name = (data.get("author") or {}).get("name") or ""
            profile_url = f"https://scholar.google.com/citations?user={author_id}"

            # 组织结果
            os.makedirs("results", exist_ok=True)
            gs_full = {
                "source": "serpapi",
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "author_id": author_id,
                "profile_url": profile_url,
                "author_name": name,
                "total_citations": total,
                "raw": data,  # 方便审计
            }
            with open("results/gs_data.json", "w", encoding="utf-8") as f:
                json.dump(gs_full, f, ensure_ascii=False, indent=2)

            shield = {
                "schemaVersion": 1,
                "label": "citations",
                "message": str(total),
                "color": "9cf",
            }
            with open("results/gs_data_shieldsio.json", "w", encoding="utf-8") as f:
                json.dump(shield, f, ensure_ascii=False)

            print(f"[OK] {name} total citations = {total}")
            return
        except Exception as e:
            last_err = e
            print(f"[Attempt {attempt}/5] Failed: {e}")
            time.sleep(3)

    raise SystemExit(f"SerpApi fetch failed: {last_err}")

if __name__ == "__main__":
    main()