.PHONY: check format

check:
	ruff check .
	ruff format --check .

format:
	ruff check --fix .
	ruff format .
