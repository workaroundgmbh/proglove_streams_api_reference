.PHONY: all lint test cover

all: lint test cover

cover: test
	poetry run coverage html
	poetry run coverage report

test: test_only
test_only:
	poetry run coverage run -m pytest -vv

format: 
	poetry run black proglove_streams
	poetry run isort proglove_streams
	poetry run autoflake --quiet --recursive --remove-duplicate-keys --remove-all-unused-imports --remove-unused-variables proglove_streams

lint: lint_only lint_types
lint_only:
	poetry run ruff check --fix proglove_streams
	poetry run bandit --quiet --recursive  --exclude proglove_streams/tests -c pyproject.toml proglove_streams
lint_types:
	poetry run mypy --fast-module-lookup  proglove_streams

run:
	poetry run python3 -m proglove_streams
