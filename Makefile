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
SERVER = $(VENV)/bin/$(PYTHON) -m http.server

PYTEST_FLAGS = --verbose
PYTEST_FILES = tests
COVERAGE_DIR = $(TKT)/
COV_REPORT   = term-missing

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

ifneq (,$(and $(filter test,$(MAKECMDGOALS)),$(filter coverage,$(MAKECMDGOALS))))
# run test and coverage rules at the same time
test:
	-$(PYTEST) --cov=$(COVERAGE_DIR) --cov-report=$(COV_REPORT) $(PYTEST_FLAGS) $(PYTEST_FILES)
	$(if $(findstring html,$(COV_REPORT)), $(SERVER) -d htmlcov $(PORT))
coverage:
	@:
else
# define test and coverage as separate rules
test: $(VENV)
	$(PYTEST) $(PYTEST_FLAGS) $(PYTEST_FILES)
coverage: $(VENV)
	-$(PYTEST) --cov=$(COVERAGE_DIR) --cov-report=$(COV_REPORT) $(TEST_DIR)
	$(if $(findstring html,$(COV_REPORT)), $(SERVER) -d htmlcov $(PORT))
endif

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
