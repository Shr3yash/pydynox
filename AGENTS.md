# Agent instructions

pydynox is an async-first DynamoDB ORM for Python, with a Rust core exposed through
PyO3. Python 3.11+ is required. Methods without a prefix are async; synchronous
methods use `sync_`. Keep both APIs in sync when changing behavior.

## Read before making changes

Start with [.ai/README.md](.ai/README.md). Detailed guidance lives in `.ai/`:

- [Project context](.ai/project-context.md): architecture and public API.
- [Coding guidelines](.ai/coding-guidelines.md): Python/Rust responsibilities and style.
- [Async-first design](.ai/async-first.md): method naming and API parity.
- [Testing guidelines](.ai/testing-guidelines.md): fixtures and test conventions.
- [Common mistakes](.ai/common-mistakes.md): pitfalls to check before submitting.
- [Dependencies](.ai/dependencies.md): keep runtime dependencies minimal.
- [Writing style](.ai/writing-style.md): use short sentences and simple English.
- [Acceptance criteria](.ai/acceptance-criteria.md): library validation checklist.

Keep detailed rules in those files rather than copying them into this one.

## Repository layout

- `src/`: Rust operations, serialization, AWS SDK calls, and PyO3 bindings.
- `python/pydynox/`: Python models, client wrappers, attributes, and integrations.
- `tests/unit/`: tests using mocks or the in-memory backend.
- `tests/integration/`: tests using LocalStack through testcontainers.
- `docs/`: guides and executable examples.
- `zensical.toml`: documentation navigation and site configuration.
- `scripts/`: documentation build helpers.

## Setup and checks

Run commands from the repository root. Install uv and a stable Rust toolchain first.

```bash
uv sync --group docs

# Rebuild the Python extension after changing Rust code.
uv run --with maturin maturin develop

# Python lint and format checks.
uv run ruff check python/ tests/ benchmarks/ scripts/
uv run ruff format --check python/ tests/ benchmarks/ scripts/
uv run ty check python/pydynox/

# Rust checks.
cargo fmt --all -- --check
cargo clippy --all-targets -- -D warnings

# Library tests.
uv run pytest tests/unit/ -v
uv run pytest tests/integration/ -v
```

Integration tests require a running Docker daemon. Their fixtures start LocalStack;
unit tests do not need Docker or AWS credentials. Use maturin to build an importable
Python extension; `cargo build` alone does not install it into the Python environment.

## Documentation

Build the site, API reference, and text index in this order:

```bash
uv run --group docs zensical build
uv run --group docs pdoc --html pydynox --skip-errors -o site/api --force
uv run python scripts/generate_llms.py
```

`site/llms.txt` is generated from `zensical.toml` and Markdown page titles. Do not edit
it by hand. The generator checks that every local page it links to exists in the
built site. The Documentation workflow runs these steps and publishes the result.
