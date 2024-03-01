TEST = pytest --verbose -vv
LINT = ruff check --fix --unsafe-fixes .

.PHONY: test
test:
	poetry run coverage run -m $(TEST)

.PHONY: coverage
coverage: test
	poetry run coverage report -m

.PHONY: lint
lint:
	poetry run $(LINT)

.PHONY: translator
translator:
	python3 -m src.translator.main $(ARGS)

.PHONY: machine
machine:
	python3 -m src.machine.main $(ARGS)

.PHONY: update-golden
update-golden:
	poetry run coverage run -m $(TEST) --update-goldens
