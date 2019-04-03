.PHONY: build clean develop

develop: 
	python setup.py develop

build:
	python setup.py sdist bdist_wheel

clean:
	rm -rf .tox .eggs *.egg-info build .pytest_cache
	find . -name "__pycache__" -type d -print0 | xargs -0 rm -rf
	find . -name "*.pyc" -delete
