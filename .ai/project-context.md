# Project Context

## What is pydynox?

A fast DynamoDB ORM for Python. The name comes from:
- **Py** = Python
- **Dyn** = DynamoDB
- **Ox** = Oxide (Rust)

## Tech Stack

- **Rust core** - All the heavy work (serialization, compression, encryption)
- **PyO3** - Python bindings for Rust
- **maturin** - Build tool for PyO3 projects

## Performance Goal

This library aims to be SUPER fast. Speed is a core feature, not an afterthought.

Every decision about where code lives should consider performance. See `coding-guidelines.md` for details.

## Project Info

- License: Apache-2.0
- Hosted on: GitHub
- Status: Stable (see `pyproject.toml` for the current version and Python requirement)

## Building the Project

**IMPORTANT**: This is a PyO3 project. Never use `cargo build` directly.

Always use maturin:

```bash
# Development build
uv run --with maturin maturin develop

# Release build (faster)
uv run --with maturin maturin develop --release

# Build wheel for distribution
uv run --with maturin maturin build --release
```

The `cargo build` command will not produce a usable Python module. Only maturin knows how to build PyO3 bindings correctly.

## Project Structure

```
pydynox/
├── src/                    # Rust code
│   ├── lib.rs             # Main module, exports to Python
│   ├── client/            # DynamoDB client
│   ├── basic_operations/  # put, get, delete, update, query
│   ├── batch_operations/  # batch_write, batch_get
│   ├── transaction_operations/ # transact_write, transact_get
│   ├── serialization.rs   # Python <-> DynamoDB conversion
│   ├── compression.rs     # zstd compression
│   ├── kms/               # KMS encryption
│   └── errors.rs          # Custom error types
├── python/pydynox/        # Python wrappers
│   ├── __init__.py        # Public API exports
│   ├── model.py           # Model base class
│   ├── client/            # DynamoDBClient wrappers
│   ├── attributes/        # Field types
│   ├── exceptions.py      # Custom exceptions
│   ├── _internal/         # Internal helpers
│   │   ├── _compression.py # Compression functions
│   │   └── _encryption.py  # Encryption functions
│   └── integrations/      # Pydantic, etc.
├── tests/
│   ├── integration/       # Integration tests (need Docker for LocalStack)
│   └── unit/              # Unit tests
├── Cargo.toml             # Rust dependencies
└── pyproject.toml         # Python config
```

## Public vs Internal API

The public API is what users import from `pydynox`. Keep it small and clean.

### What Goes in Public API

- `Model`, `ModelConfig` - The ORM classes users extend
- `DynamoDBClient` - The client users create
- `Condition`, `Action` - Query/update builders
- `QueryResult`, `BatchWriter`, `Transaction` - Operation helpers
- Attribute types like `StringAttribute`, `NumberAttribute`

### What Stays Internal

- Compression functions (`_internal/_compression.py`)
- Encryption functions (`_internal/_encryption.py`)
- Serialization helpers
- Size calculation internals

### Naming Convention

- Public modules: `model.py`, `client.py`, `query.py`
- Internal modules: `_internal/_compression.py`, `_internal/_encryption.py`
- Internal folder: `_internal/`

## Lambda Cold Start Note

This is important for AWS Lambda. Cold start happens once, then the same container handles many requests.

- **Cold start (once)**: Model class loading, field setup, client creation → Python is fine
- **Warm invocations (many)**: Serialize, query, save, transform → Must be Rust

Focus optimization on the hot path (warm invocations). That's where users feel the speed.
