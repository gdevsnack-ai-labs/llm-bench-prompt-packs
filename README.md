# LLM Benchmark Prompt Packs

Public, reusable prompt packs for local LLM, agent, and application-quality benchmarks.

This repository separates **benchmark inputs** from the benchmark runner. It is intended to make prompt sets versioned, inspectable, and reusable across different models and execution harnesses.

## Included pack

### Self Bench Pack v1

`packs/self-bench-pack-v1.json` contains 24 self-designed prompts:

| Category | Count | Focus |
|---|---:|---|
| `ui` | 9 | Single-file bilingual UI and application tasks |
| `game` | 8 | Playable bilingual HTML games |
| `service` | 4 | Local-first service and dashboard tasks |
| `progressive` | 3 | Phase 1 → 2 → 3 extension without rebuilding |

Every prompt includes:

- Korean + English user-visible UI requirements
- Korean font and UTF-8 rendering requirements
- responsive design and no-placeholder quality bar
- a self-test and verification loop for agent-style execution
- explicit evaluation axes such as instruction compliance, functionality, UI quality, and self-verification

This is a **functional application-generation prompt pack**, not a standard academic knowledge benchmark.

## Quick start

```bash
python3 scripts/build_self_bench_pack.py
```

The builder regenerates:

```text
packs/self-bench-pack-v1.json
```

The builder performs basic integrity checks:

- exactly 24 prompts
- unique prompt IDs
- bilingual requirements present
- self-test loop present
- selected phrases from the source-pattern review absent

Validate the generated pack with the repository schema:

```bash
python3 - <<'PY'
import json
from pathlib import Path

pack = json.loads(Path('packs/self-bench-pack-v1.json').read_text(encoding='utf-8'))
items = pack['all']
assert len(items) == 24
assert len({item['id'] for item in items}) == 24
print('OK:', len(items), 'prompts')
PY
```

## Prompt format

Each prompt has a stable ID, category, title, text, and provenance fields:

```json
{
  "id": "self-ui-01",
  "title": "한국 주식 대시보드",
  "category": "ui",
  "text": "...",
  "source": "SELF-DESIGNED",
  "source_video": "..."
}
```

The top-level `all` array is convenient for runners. Category-specific arrays are provided for filtering and reporting.

## Provenance and attribution

The pack was written as an original set. Earlier public prompt collections were used only to study broad task-shape patterns such as requirements lists, quality constraints, and progressive extension. Their raw prompt text and raw collection files are **not** included here.

Do not treat the `source` field as a claim that the pack reproduces or republishes another collection. It identifies the design provenance of this pack.

## Relationship to benchmark runners

This repository contains reusable inputs and the builder. A separate benchmark source repository contains execution harnesses, production adapters, local fixtures, and measurement reports. Keeping the two layers separate makes it possible to reuse the prompt pack without exposing private production paths or internal run logs.

A runner should record at least:

- prompt pack name and version
- prompt ID
- model and serving backend
- generation settings
- validation protocol
- raw output and normalized result
- limitations and repeat count

## Scope and limitations

- The pack measures practical instruction following and application generation, not general intelligence.
- Self-test requirements measure an agent workflow, not a single-shot completion.
- Results depend on the runner, tools, browser, model context, and verification harness.
- A prompt passing a structural gate does not prove semantic factuality or production readiness.

## License

The prompt pack, metadata, and documentation are licensed under **Creative Commons Attribution 4.0 International (CC BY 4.0)**.

Suggested attribution:

> Self Bench Pack v1, gdevsnack-ai-labs, licensed under CC BY 4.0.

See [LICENSE](LICENSE) and the official [CC BY 4.0 legal code](https://creativecommons.org/licenses/by/4.0/legalcode).
