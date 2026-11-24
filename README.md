# agent-error-taxonomy

Classify an agent or service failure into a named category with a routed fix
action, instead of retrying blind.

Feed it an error message (or a log file) and it returns one JSON object:
`{category, action, description, input_preview}` — machine-readable, so a
wrapper script or an orchestrator can branch on the action without parsing
prose.

## Who it's for

Devs and agent operators orchestrating flaky third-party providers,
marketplaces, and RPCs — anyone whose retry loop needs to know *why* something
failed before deciding what to do next. Retrying a dead platform for an hour,
or hammering a rate-limited API, is what happens when every failure looks the
same. It shouldn't.

## The taxonomy

| Category | Action | Meaning |
|---|---|---|
| `AUTH` | `rotate_key` | API key revoked, expired, or invalid (401, "Invalid API Key") |
| `RATE_LIMIT` | `retry_backoff` | Rate limit or quota hit (429, "quota exceeded") |
| `TEMPORARY` | `retry` | Transient server error (500/502/503/504, gateway timeout) |
| `PLATFORM_DEAD` | `mark_dead` | Endpoint removed or service gone (connection refused, DNS failure) |
| `MODEL_DEPRECATED` | `update_model` | Model string deprecated or removed by the provider |
| `INSUFFICIENT_FUNDS` | `fund_wallet` | Wallet lacks funds/gas for the transaction |
| `PARSING` | `fix_parser` | Response parsing failed — schema mismatch |
| `UNKNOWN` | `investigate` | No pattern matched — a human or a deeper check decides |

Matching is a regex pattern table, checked in the order above. First match
wins.

## Usage

```console
$ python3 error-taxonomy.py "429 Too Many Requests"
{
  "category": "RATE_LIMIT",
  "action": "retry_backoff",
  "description": "Hit rate limit or quota",
  "input_preview": "429 Too Many Requests"
}

$ python3 error-taxonomy.py /path/to/failing-job.log   # leading / = read as file
$ python3 error-taxonomy.py                            # no arg: list the categories
```

Run the tests (one sample error per category):

```console
$ python3 test_error_taxonomy.py
```

## The workflow it encodes: diagnose before retry

1. **One failure = read the log.** Pipe the actual error text through the
   classifier before doing anything else.
2. **Act on the category, not the symptom.** `rotate_key`, `mark_dead`, and
   `update_model` are terminal for that attempt — no amount of retrying fixes
   them. `retry` and `retry_backoff` are the only categories where trying
   again makes sense, and they have different waits.
3. **Two failures with the same category = stop and diagnose properly.**
   Never reach for a third blind workaround.
4. **`UNKNOWN` is a backlog item, not a retry.** If the same unknown error
   keeps recurring, add a pattern for it — that's how the table grows.

## Honest limits

- **A starting set, not a universal classifier.** The pattern table comes from
  one operator's incident history across LLM providers, marketplaces, and EVM
  RPCs. Your failure modes will differ; the table is a plain dict at the top
  of the file precisely so you can extend and reorder it.
- **First match wins, and patterns are blunt.** A `503` inside a larger error
  message classifies as `TEMPORARY` even if the root cause was auth. Order
  and pattern specificity matter — tune them for your stack.
- **It classifies text, not truth.** It never probes the service itself; for
  pre-flight reachability checks, pair it with a prober (see
  `agent-preflight-probe`).

## License

MIT — see `LICENSE`.
