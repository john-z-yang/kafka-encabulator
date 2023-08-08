.PHONY: setup test clean

setup: requirements.txt
	pip install -r requirements.txt

test:
	pytest

clean:
	rm -rf src/__pycache__ tests/__pycache__ .pytest_cache