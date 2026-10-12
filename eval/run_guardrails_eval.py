import json
import time
from collections import defaultdict
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()  # لازم قبل استيراد الـ agent

from writer_editor.Agents.Guardrails_Agent import guardrail_agent

REPEATS = 3
FALLBACK_TEXT = "Guardrail validation fallback allowed the request."
DATA = Path(__file__).parent / "guardrails_dataset.jsonl"
OUT = Path(__file__).parent / "guardrails_results_v3.json"


def main():
    rows = [
        json.loads(line)
        for line in DATA.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    results = []
    for i, r in enumerate(rows, 1):
        passes = 0
        errors = 0
        for _ in range(REPEATS):
            out = guardrail_agent(
                {"user_query": r["query"], "iteration": 0, "llm_calls": 0}
            )
            allowed = bool(out.get("guardrail_allowed", False))
            reason = out.get("guardrail_reason", "")

            if reason == FALLBACK_TEXT:
                errors += 1
            elif allowed == r["expected_allowed"]:
                passes += 1
            time.sleep(2)  # rate limit

        valid = REPEATS - errors
        print(f"[{i}/{len(rows)}] {passes}/{valid} | {r['category']:10s} | {r['query'][:50]}")
        results.append({**r, "passes": passes, "valid_runs": valid, "errors": errors})

    # ---- الملخص ----
    total_pass = sum(x["passes"] for x in results)
    total_valid = sum(x["valid_runs"] for x in results)
    total_errors = sum(x["errors"] for x in results)

    print("\n" + "=" * 50)
    if total_valid:
        print(f"Accuracy: {total_pass}/{total_valid} = {total_pass / total_valid:.0%}")
    print(f"Errors (الـ LLM فشل): {total_errors}")

    by_cat = defaultdict(lambda: [0, 0])
    for x in results:
        by_cat[x["category"]][0] += x["passes"]
        by_cat[x["category"]][1] += x["valid_runs"]
    print("\nPer category:")
    for cat, (ok, tot) in by_cat.items():
        print(f"  {cat:10s} {ok}/{tot}")

    always_wrong = [x for x in results if x["valid_runs"] and x["passes"] == 0]
    unstable = [x for x in results if 0 < x["passes"] < x["valid_runs"]]

    print(f"\nدايماً غلط: {len(always_wrong)}")
    for x in always_wrong:
        print(f"  - ({x['category']}) {x['query']}")
    print(f"\nمتذبذب (مرة صح ومرة غلط): {len(unstable)}")
    for x in unstable:
        print(f"  - ({x['category']}) {x['passes']}/{x['valid_runs']} | {x['query']}")

    OUT.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nDone, results saved to: {OUT}")


if __name__ == "__main__":
    main()