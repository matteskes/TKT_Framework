# TKT_Framework

## Requirements

* **Python 3** (installed system-wide)
* **Make** (standard on most Unix-like systems)

The project uses a local virtual environment (`.venv/`) for dependencies.

## Usage

By default, running `make` (with no arguments) will execute the application:

```sh
make
```

or explicitly:

```sh
make run
```

## Available Commands

### Setup

* **`make install`**
  Creates a virtual environment in `.venv/` and installs dependencies from `requirements.txt`.

### Development

* **`make test`**
  Runs the test suite with `pytest`.

* **`make coverage`**
  Run coverage tests. Regular test results will not show up.

* **`make typecheck`**
  Performs static type checking using `mypy`.

* **`make lint`**
  Runs `ruff` to check code style and linting issues.

* **`make format`**
  Formats the code with `black` and `isort`.

* **`make force-fix`**
  Runs `ruff` with automatic fixes (including unsafe ones).

* **`make check`**
  Runs type checking, linting, and formatting in one step.

### Execution

* **`make run`**
  Runs the application (`python -m TKT`). Equivalent to just `make`.
