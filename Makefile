make: install

clean:
	rm -rf build dist __pycache__ *.egg-info

dist: clean
	python3 setup.py sdist bdist_wheel

upload:
	python3 -m twine upload dist/*

install: dist
	pip install --force-reinstall --no-deps dist/*.whl

.PHONY: clean dist upload install
