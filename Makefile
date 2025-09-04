TKT      = TKT
TEST_DIR = tests

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
	$(PYTEST) --cov=$(COVERAGE_DIR) --cov-report=term-missing $(TEST_DIR)

typecheck: $(VENV)
	$(MYPY) $(TKT) $(TEST_DIR)

lint: $(VENV)
	$(RUFF) check --show-fixes $(TKT) $(TEST_DIR)/test_*.py

format: $(VENV)
	$(BLACK) $(TKT) $(TEST_DIR)
	$(ISORT) $(TKT) $(TEST_DIR)

force-fix: $(VENV)
	$(RUFF) check --fix --unsafe-fixes $(TKT) $(TEST_DIR)

check: format typecheck lint

.PHONY: run install test coverage typecheck lint format force-fix check
.SILENT: install test coverage check $(VENV)
