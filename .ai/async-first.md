# Async-first design

pydynox is async-first. This means:

1. Methods are async by default; synchronous versions use the `sync_` prefix
2. Async and sync APIs must have feature parity
3. New features start with async, then add sync
4. Docs show async examples first, sync as alternative

## Why async-first?

Python has a GIL (Global Interpreter Lock). Only one thread runs Python code at a time. Async lets Python do other work while waiting for I/O.

pydynox is written in Rust. When you call an async method:

1. Python calls Rust via PyO3
2. Rust releases the GIL immediately
3. Rust runs the DynamoDB call using tokio
4. Python is free to run other coroutines
5. When done, Rust reacquires the GIL and returns

This means pydynox async operations are truly non-blocking.

## API parity checklist

When adding a new feature, ensure both sync and async versions have:

- Same method signature (except `sync_` prefix)
- Same return type (or async equivalent)
- Same properties (e.g., `last_evaluated_key` on query results)
- Same behavior

## Async method naming

| Async (default) | Sync |
|-----------------|------|
| `await model.save()` | `model.sync_save()` |
| `await model.delete()` | `model.sync_delete()` |
| `await model.update()` | `model.sync_update()` |
| `await Model.get()` | `Model.sync_get()` |
| `Model.query()` | `Model.sync_query()` |
| `Model.scan()` | `Model.sync_scan()` |
| `await Model.batch_get()` | `Model.sync_batch_get()` |
| `BatchWriter` | `SyncBatchWriter` |
| `await client.put_item()` | `client.sync_put_item()` |
| `await client.get_item()` | `client.sync_get_item()` |

## Result classes

Async results are separate classes but must have same properties:

- `ModelQueryResult` / `AsyncModelQueryResult`
- `ModelScanResult` / `AsyncModelScanResult`
- `GSIQueryResult` / `AsyncGSIQueryResult`
- `LSIQueryResult` / `AsyncLSIQueryResult`

All must expose `last_evaluated_key` for pagination.

## Testing

Every async feature needs tests. See `tests/integration/async_ops/` for examples.

## See also

- ADR 018: Async-first design
- docs/guides/async-first.md
