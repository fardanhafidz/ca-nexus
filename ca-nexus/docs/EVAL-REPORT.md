# EVAL-REPORT — golden queries G-01..G-08 (generated from data/eval_report.json)

Retrieval index: Qdrant real, 96 docs, REAL embeddings openai/text-embedding-3-small via OpenRouter (1536). Rerun: DATABASE_URL=... QDRANT_URL=... OPENROUTER_API_KEY=... python scripts/eval_golden.py

| ID | Query | Route | Route OK | Retrieval | Extra |
|---|---|---|---|---|---|
|G-01|VSHH-4505 high vibration trip action on KC-4501|graph|True|True|{"rrf": {"hit": true, "n": 5}, "dense_only": {"hit": true, "n": 5}, "hits": 5, "graph_edges": 40}|
|G-02|What does SEQ-4501 protect?|graph|True|True|{"rrf": {"hit": true, "n": 5}, "dense_only": {"hit": true, "n": 5}, "hits": 5, "graph_edges": 40}|
|G-03|Mechanical seal spare parts for GA-1201A|vector|True|True|{"rrf": {"hit": true, "n": 5}, "dense_only": {"hit": true, "n": 5}, "hits": 5, "graph_edges": 40}|
|G-04|total downtime and cost EA-5601|combined|True|True|{"sql_rows": 1, "sql_reproducible": true}|
|G-05|corrective vs preventive count KC-4501|combined|True|True|{"sql_rows": 1, "sql_reproducible": true}|
|G-08|MTBF CT-7801|unsupported|True||{}|

No success percentages claimed before validator review (T0.3). Semantic quality: hits above use real embeddings; validator judges correctness.
