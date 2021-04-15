.PHONY: all cover lint test

all: lint test cover

pip_install: Pipfile.lock
pip_update:
	pipenv update --dev > /dev/null
Pipfile.lock: Pipfile
	pipenv install --dev > /dev/null

cover: test
	pipenv run coverage html
	pipenv run coverage report

test: pip_install test_only
test_only:
	pipenv run coverage run -m pytest -v

lint: pip_install lint_only lint_types
lint_only:
	pipenv run flake8 proglove_streams
	pipenv run pylint --rcfile=.pylintrc proglove_streams
	pipenv run bandit --quiet --recursive  --exclude proglove_streams/tests proglove_streams
lint_types:
	pipenv run mypy --config-file=.mypy.ini proglove_streams

run:
	pipenv run python3 -m proglove_streams
