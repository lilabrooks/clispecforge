# Local quality checks. Mirrors the GitHub Actions workflows.
#
#   make check       Run lint, type-check, tests, and coverage on the active
#                    interpreter. This is the everyday command.
#   make check-all   Run the everyday gate across every supported Python
#                    version. Uses isolated uv environments, so it does not
#                    replace .venv or create a project lockfile.
#
# Individual targets (lint, typecheck, test, coverage) are available too.

PYTHON ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)
RUFF ?= $(if $(wildcard .venv/bin/ruff),.venv/bin/ruff,ruff)
MYPY ?= $(if $(wildcard .venv/bin/mypy),.venv/bin/mypy,mypy)
PYTEST ?= $(if $(wildcard .venv/bin/pytest),.venv/bin/pytest,pytest)
VERSIONS ?= 3.12 3.13 3.14
SNYK ?= snyk
SNYK_ORG ?=
# Snyk's pip scanner shells out to a `python` executable to resolve the
# dependency tree. Prefer the project venv; fall back to python3 so a bare
# checkout without an activated venv still works (macOS has no plain `python`).
SNYK_PYTHON ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)
SNYK_OPEN_SOURCE_SEVERITY ?= low
SNYK_CODE_SEVERITY ?= low
SNYK_ORG_ARG := $(if $(SNYK_ORG),--org=$(SNYK_ORG),)
SNYK_PYTHON_ARG := --command=$(SNYK_PYTHON)

.PHONY: check lint format typecheck test coverage snyk snyk-open-source snyk-code check-all

check: lint typecheck coverage

lint:
	$(RUFF) check .
	$(RUFF) format --check .

format:
	$(RUFF) format .

typecheck:
	$(MYPY)

test:
	$(PYTEST)

coverage:
	@$(PYTHON) -c 'import coverage' >/dev/null 2>&1 || { \
		echo "coverage is not installed. Run '$(PYTHON) -m pip install -e \".[dev]\"'."; \
		exit 127; \
	}
	$(PYTHON) -m coverage run -m pytest
	$(PYTHON) -m coverage report

snyk: snyk-open-source snyk-code

# Install the full requirements.txt into the scanning interpreter first so Snyk
# resolves the complete transitive tree. Without this, packages that aren't
# installed can't be resolved, and --skip-unresolved would silently drop them
# from the scan (under-reporting vulns) while the Snyk dashboard, which resolves
# everything server-side, still flags them.
snyk-open-source:
	@command -v $(SNYK) >/dev/null 2>&1 || { \
		echo "snyk CLI not found. Install it, then run 'snyk auth'."; \
		exit 127; \
	}
	$(SNYK_PYTHON) -m pip install -q -r requirements.txt
	$(SNYK) test --file=requirements.txt --package-manager=pip --severity-threshold=$(SNYK_OPEN_SOURCE_SEVERITY) $(SNYK_PYTHON_ARG) $(SNYK_ORG_ARG)

snyk-code:
	@command -v $(SNYK) >/dev/null 2>&1 || { \
		echo "snyk CLI not found. Install it, then run 'snyk auth'."; \
		exit 127; \
	}
	$(SNYK) code test --severity-threshold=$(SNYK_CODE_SEVERITY) $(SNYK_ORG_ARG) .

check-all:
	@command -v uv >/dev/null 2>&1 || { \
		echo "check-all needs uv (https://docs.astral.sh/uv/). Install it, or run 'make check' per interpreter."; \
		exit 1; \
	}
	@for v in $(VERSIONS); do \
		echo "=== Python $$v ==="; \
		uv run --isolated --no-project --python $$v --with-editable ".[dev]" -- \
			$(MAKE) check PYTHON=python RUFF=ruff MYPY=mypy PYTEST=pytest || exit 1; \
	done
	@echo "All versions passed."
