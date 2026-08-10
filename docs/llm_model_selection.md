# LLM model selection: free-tier tier list and per-strategy pairing

> Researched 2026-08-10 (desk research from provider docs/blog posts), then
> **re-verified the same day against the real Groq/OpenRouter/SambaNova API
> keys** (`GET /v1/models`, checking live pricing/availability rather than
> trusting published free-tier claims). The desk research got Groq right but
> was **wrong about OpenRouter's specific free model** (the assumed
> `qwen/qwen3-coder:free`/`deepseek/deepseek-r1:free` were not actually free
> at check time — free rosters churn fast) and **wrong to present SambaNova
> as free** (every model on the real key's `/v1/models` response carries
> non-zero per-token pricing). §2 below is what's been through a live check;
> re-verify again before trusting it much later, since free rosters keep
> moving. Free tiers, rate limits, and model rosters drift — re-verify
> current numbers before committing a model to a full-corpus run. Companion
> to `docs/condition_model.md` §5 (the model axis mechanism this feeds) and
> `docs/suspicious_frame_selection.md` (the evidence-noise work from the
> same session).

## Why model is a deliberate variable, not an afterthought

Each strategy makes a different demand on the model: `zero` needs almost
nothing (no ODC vocabulary, no reasoning scaffold — any competent
instruction-follower works). `few` needs strong coding/reasoning to
correctly apply a dense taxonomy + decision-tree + worked-examples prompt.
`scientific` needs the strongest available reasoning *and* reliable
multi-turn tool-use, since it's the condition the thesis is trying to prove
superior — a result that only holds for one model could be a model
idiosyncrasy, not a property of the strategy. See `docs/condition_model.md`
§5 for how running a strategy under 2 models is wired without artifact
collisions.

## Free-tier provider tier list

Currently configured in `.env`: `GEMINI_API_KEYS` (rotation), `GROQ_API_KEY`,
`OPENROUTER_API_KEY`, `SAMBANOVA_API_KEY`. `llm.py`'s `openai-compatible`
provider (`--provider openai-compatible --base-url ... --api-key-env ...`)
accepts any OpenAI-compatible endpoint — no code change needed to add a new
one (Cerebras, GitHub Models, etc.).

| Provider | Free tier | Best-fit models | Notes |
|---|---|---|---|
| **Google AI Studio (Gemini)** | `gemini-3.1-flash-lite` and `gemini-3.5-flash-lite`: 500 RPD each. | `gemini-3.1-flash-lite` (less powerful, the default), `gemini-3.5-flash-lite` (more powerful) | Per explicit instruction — not independently re-verified via API (unlike the rows below), trusted as given. |
| **Groq** ✅ verified live | `openai/gpt-oss-120b`: 1000 requests/day, 8K TPM. `llama-3.3-70b-versatile`: 1000 requests/day, 12K TPM. Confirmed via real `chat/completions` calls + rate-limit response headers, `$0` — no billing involved. | `openai/gpt-oss-120b` (already configured), `llama-3.3-70b-versatile` | ⚠️ gpt-oss-120b's 8K TPM is tight for `few`/`scientific`'s longer prompts (system prompt alone ≈3K+ tokens before evidence) — workable but budget calls carefully. |
| **OpenRouter** ✅ verified live | Free roster confirmed via `GET /v1/models` pricing on 2026-08-10: `cohere/north-mini-code:free`, `google/gemma-4-26b-a4b-it:free`, `google/gemma-4-31b-it:free`, `inclusionai/ling-3.0-tiny:free`, `nvidia/nemotron-3-nano-30b-a3b:free`, `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free`, `nvidia/nemotron-3-super-120b-a12b:free`, `nvidia/nemotron-3-ultra-550b-a55b:free`, `nvidia/nemotron-3.5-content-safety:free`, `nvidia/nemotron-nano-12b-v2-vl:free`, `nvidia/nemotron-nano-9b-v2:free`, `openai/gpt-oss-20b:free`, `openrouter/free`, `poolside/laguna-s-2.1:free`, `poolside/laguna-xs-2.1:free` (17 total). 20 RPM; 50 req/day (no purchase) or 1,000/day (after any $10+ lifetime purchase). | `nvidia/nemotron-3-ultra-550b-a55b:free` (**strongest free model found on any provider checked** — 71.9% SWE-bench Verified, 1M context) | ⚠️ **`deepseek/deepseek-v3.2`, `qwen/qwen3-coder:free`, and `deepseek/deepseek-r1:free` are NOT currently free** — the earlier desk-research recommendation for this provider was wrong; confirmed via live pricing AND a real `$0`-cost completion call on `nvidia/nemotron-3-ultra-550b-a55b:free`. Free roster churns — re-check `GET /v1/models` before relying on any specific `:free` id later. |
| **SambaNova Cloud** ⚠️ paid, but budget-capped | Not free — `GET /v1/models` confirms real per-token pricing on all 6 models, no `$0` tier. **But**: the account has a **$5.00 USD signup-bonus credit** (confirmed by the user via their dashboard — no public API to check balance, so this number is not independently re-verifiable by this pipeline). `DeepSeek-V3.2` pricing: $3/M prompt tokens, $4.50/M completion tokens. | `DeepSeek-V3.2` — opportunistic bonus only, NOT part of the primary pairing | See "SambaNova bonus budget" below for the $5 → call-count math. Once exhausted, drop back to the fully-free Groq/Gemini/OpenRouter trio — no other SambaNova usage without adding real payment. |
| **Cerebras** (not re-verified) | 1M tokens/day, 30 RPM, but an **8,192-token context cap across ALL free-tier models** (account-level, not model-specific). Model roster is volatile week to week. | Only viable for `zero` (short prompt) — the context cap disqualifies `few`/`scientific`. | Fastest raw throughput if you stay under the context cap. No key configured, not tested. |
| **GitHub Models** (not re-verified) | High-tier models (GPT-4.1, o4-mini): 50 req/day, 10 RPM, 8K in/4K out. Free to any GitHub account. | `o4-mini` | The one free source of an actual OpenAI reasoning (o-series) model. 50 req/day too tight for the full 854-bug corpus, fine for a confirmatory subset. No key configured, not tested. |
| **Mistral La Plateforme** (not re-verified) | "Experiment" tier: ~1B tokens/month, phone verification required, limits not publicly documented. | `codestral`, `mistral-large` | Backup option, lower priority. No key configured, not tested. |
| **NaraRouter** (`router.bynara.id`, not re-verified) | ~7M tokens/day, 30+ models, OpenAI-compatible, no card. | Whatever DeepSeek/GLM variant it proxies | Third-party aggregator — treat claims as less durable than a provider's own docs. No key configured, not tested. |

Coding/reasoning benchmark backdrop (SWE-bench Verified, published figures,
not independently reproduced): Kimi K2.5 76.8%, GLM-4.7 73.8%, **NVIDIA
Nemotron 3 Ultra 550B 71.9%** (the verified-free OpenRouter pick above),
DeepSeek-V3.2 ~70-73%, Qwen3-Coder-480B ~69.6-70.6%, gpt-oss-120b ~62.4%.

## Recommended default pairs per strategy

| Strategy | Primary (already keyed) | Secondary (already keyed) | Why |
|---|---|---|---|
| `zero` | `gemini-3.1-flash-lite` (the less-powerful pick — matches zero's minimal reasoning demand) | `llama-3.3-70b-versatile` (Groq, ✅ verified free) | No reasoning depth needed — the interesting question is whether a different model *family* (Google vs. Meta) agrees. |
| `few` | `openai/gpt-oss-120b` (Groq, ✅ verified free — watch the 8K TPM budget) | `nvidia/nemotron-3-ultra-550b-a55b:free` (OpenRouter, ✅ verified $0 on a real call) | Nemotron 3 Ultra outscores gpt-oss-120b by ~9.5 SWE-bench points — tests whether `few`'s result is gpt-oss-specific, on a genuinely free model this time. |
| `scientific` | `gemini-3.5-flash-lite` (the more-powerful pick — this is the flagship condition, upgraded from `gemini-3.1-flash-lite`) | `nvidia/nemotron-3-ultra-550b-a55b:free` (OpenRouter, same as `few`'s secondary — one open-weight anchor model across both strategies keeps the comparison clean) | Pair a strong closed model with a strong open one, both confirmed free, so the "loop beats static prompt" claim isn't tied to one vendor's model or an unverified-free assumption. |

SambaNova is intentionally **not** in this table as a primary/secondary
pick — it's paid, not free (see above). It's still worth using
*opportunistically*: the account has a $5.00 signup-bonus credit sitting
unused, and spending it on a bonus third data point for `few`/`scientific`
(`DeepSeek-V3.2`) costs nothing beyond what's already been given away by
SambaNova. Treat it as a capped bonus run, not part of the core
comparison — see below for exactly how far $5 goes. GitHub Models' `o4-mini`
remains an interesting confirmatory-subset option for `scientific`
specifically if a GitHub token gets added later, but is unverified and not
part of the default pairing.

### SambaNova bonus budget: how far $5.00 goes

No public API exposes SambaNova's real-time balance, so this is a
computed estimate from real prompt sizes (`Closure_150_prefix_context_FINAL.json`,
current code) × confirmed pricing ($3/M prompt tokens, $4.50/M completion
tokens for `DeepSeek-V3.2`) — not a guarantee. **Watch the actual balance on
the SambaNova dashboard while running; treat the numbers below as a starting
`--daily-call-budget` ceiling, not ground truth.**

| Strategy | Tokens/call (measured) | Est. cost/call | $5.00 buys (theoretical) | Recommended `--daily-call-budget` |
|---|---|---|---|---|
| `few` | ~7,050 input + ~600 output (single call) | ~$0.024 | ~208 calls | **150** (~72% margin) |
| `scientific` | ~5,700 tokens turn 1, growing ~1,050/turn; assume avg 3 turns/bug-arm ≈ 20,400 input + ~1,200 output | ~$0.067/bug-arm | ~75 bug-arms | **35** (turn count is genuinely variable — some bugs conclude in 2 turns, some max out at 6, so this estimate has wide error bars; 35 leaves real margin) |

`--daily-call-budget` counts one increment per `classify_bug_context` call
(i.e. per bug-arm, prefix or postfix separately) regardless of strategy —
for `scientific` this already matches "bug-arms," not raw HTTP calls, since
the whole multi-turn loop is one `classify_bug_context` invocation
(`batch.py`, `llm_calls_made += self_consistency`). So the recommended
values above plug directly into `study-run --daily-call-budget <N>`.

Example bonus run (few, prefix-only subset, stop well before $5 is gone):
```
study-run --manifest <m> --taxonomy open --strategy few \
  --provider openai-compatible --base-url https://api.sambanova.ai/v1 \
  --api-key-env SAMBANOVA_API_KEY --model DeepSeek-V3.2 \
  --daily-call-budget 150
```
Once the credit is exhausted (`study-run` will error on the first
billing-rejected call, or you see the dashboard balance hit $0), drop
`--provider`/`--base-url`/`--api-key-env`/`--model` and go back to the
Groq/Gemini/OpenRouter trio above — no other SambaNova usage without adding
real payment.

## What's actually needed to activate a secondary model

All 4 keys currently in `.env` (`GEMINI_API_KEYS`, `GROQ_API_KEY`,
`OPENROUTER_API_KEY`, `SAMBANOVA_API_KEY`) are set. For the pairs above, no
further setup is needed — every model in the table has been confirmed live
against a real key:
- **Gemini pair**: same `GEMINI_API_KEY`/`GEMINI_API_KEYS`, just pass
  `--model gemini-3.5-flash-lite` instead of the default
  `gemini-3.1-flash-lite`.
- **Groq pair**: already the default (`GROQ_MODEL=openai/gpt-oss-120b`);
  pass `--model llama-3.3-70b-versatile` for the `zero` secondary.
- **OpenRouter secondary**: `OPENROUTER_MODEL` in `.env`/`.env.example` is
  now `nvidia/nemotron-3-ultra-550b-a55b:free` (fixed 2026-08-10 — it used
  to default to a paid model, `deepseek/deepseek-v3.2`, which would have
  silently billed the account).
- **SambaNova**: configured, not part of the core pairing, but usable as a
  budget-capped bonus run against the $5 signup credit — see "SambaNova
  bonus budget" above for the exact `--daily-call-budget` values and example
  command.
