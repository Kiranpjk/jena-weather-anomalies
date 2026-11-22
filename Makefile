.PHONY: install lint test docker report

install:
	pip install -e ".[dev]"

lint:
	ruff check .

test:
	pytest -q

docker:
	docker build -t jena-anomalies .

report:
	mkdir -p site && python -m jena_anomalies.cli report --html site/index.html
