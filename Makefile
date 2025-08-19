TKT = TKT

PYTHON = python3
VENV   = .venv

PIP    = $(VENV)/bin/$(PYTHON) -m pip
PYTEST = $(VENV)/bin/$(PYTHON) -m pytest
MYPY   = $(VENV)/bin/$(PYTHON) -m mypy
RUFF   = $(VENV)/bin/$(PYTHON) -m ruff
BLACK  = $(VENV)/bin/$(PYTHON) -m black
ISORT  = $(VENV)/bin/$(PYTHON) -m isort

PYTEST_FLAGS = --verbose
COVERAGE_DIR = $(TKT)/

run: $(VENV)
	$(VENV)/bin/$(PYTHON) -m $(TKT)

install:
	touch requirements.txt
	$(MAKE) "$(VENV)"

$(VENV): requirements.txt
	if test ! -d "$(VENV)"; then $(PYTHON) -m venv "$(VENV)"; fi
	$(PIP) install --upgrade pip -r requirements.txt
	$(MYPY) --install-types --non-interactive
	touch "$(VENV)"

test: $(VENV)
	$(PYTEST) $(PYTEST_FLAGS) $(PYTEST_FILES)

coverage: $(VENV)
	FLAGS="--cov=$(COVERAGE_DIR) --cov-report=term-missing"; \
	$(MAKE) test PYTEST_FLAGS="$$FLAGS" 2> /dev/null

typecheck: $(VENV)
	$(MYPY) $(TKT)

lint: $(VENV)
	$(RUFF) check $(TKT)

format: $(VENV)
	$(BLACK) $(TKT)
	$(ISORT) $(TKT)

force-fix: $(VENV)
	$(RUFF) check --fix --unsafe-fixes $(TKT)

check: format typecheck lint

.PHONY: run install test coverage typecheck lint format force-fix check
.SILENT: install test coverage check $(VENV)
