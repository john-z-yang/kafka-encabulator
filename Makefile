.PHONY: setup test clean

setup: requirements.txt
	pyenv local 3.11.4
	pip install -r requirements.txt

test:
	pytest

clean:
	rm -rf src/__pycache__ tests/__pycache__