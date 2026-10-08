SCRIPT  = a_maze_ing.py
CONFIG  = config.txt
RUN     = poetry run
MYPY_FLAGS = --warn-return-any --warn-unused-ignores --ignore-missing-imports \
             --disallow-untyped-defs --check-untyped-defs

.PHONY: install run debug clean lint lint-strict

install:
	@if ! command -v poetry > /dev/null; then \
		echo "Error: poetry is not installed (see README)"; \
		exit 1; \
	fi
	poetry install

run:
	$(RUN) python $(SCRIPT) $(CONFIG)

debug:
	$(RUN) python -m pdb $(SCRIPT) $(CONFIG)

clean:
	find . -path ./.venv -prune -o -type d -name "__pycache__" \
		-exec rm -rf {} +
	rm -rf .mypy_cache .pytest_cache dist build *.egg-info

lint:
	$(RUN) flake8 .
	$(RUN) mypy . $(MYPY_FLAGS)

lint-strict:
	$(RUN) flake8 .
	$(RUN) mypy . --strict
