.PHONY: compile release test annotate buildext check-isort check-black


cyt:
	cython3 shuttleasgi/url.pyx
	cython3 shuttleasgi/exceptions.pyx
	cython3 shuttleasgi/headers.pyx
	cython3 shuttleasgi/cookies.pyx
	cython3 shuttleasgi/contents.pyx
	cython3 shuttleasgi/messages.pyx
	cython3 shuttleasgi/scribe.pyx
	cython3 shuttleasgi/baseapp.pyx

compile: cyt
	python3 setup.py build_ext --inplace


clean:
	rm -rf dist/
	rm -rf build/
	rm -f shuttleasgi/*.c
	rm -f shuttleasgi/*.so


buildext:
	python3 setup.py build_ext --inplace


annotate:
	cython3 shuttleasgi/url.pyx -a
	cython3 shuttleasgi/exceptions.pyx -a
	cython3 shuttleasgi/headers.pyx -a
	cython3 shuttleasgi/cookies.pyx -a
	cython3 shuttleasgi/contents.pyx -a
	cython3 shuttleasgi/messages.pyx -a
	cython3 shuttleasgi/scribe.pyx -a
	cython3 shuttleasgi/baseapp.pyx -a


build: test
	python3 -m build


prepforbuild:
	pip install --upgrade build


testrelease:
	twine upload -r testpypi dist/*


release: clean compile artifacts
	twine upload -r pypi dist/*


test:
	pytest tests/


itest:
	pytest itests/


init:
	pip install -r requirements.txt


test-v:
	pytest -v


test-cov-unit:
	pytest --cov-report html --cov=shuttleasgi tests


test-cov:
	pytest --cov-report html --cov=shuttleasgi --disable-warnings


lint: check-flake8 check-isort check-black

format:
	@isort shuttleasgi 2>&1
	@isort tests 2>&1
	@isort itests 2>&1
	@black shuttleasgi 2>&1
	@black tests 2>&1
	@black itests 2>&1

check-flake8:
	@echo "$(BOLD)Checking flake8$(RESET)"
	@flake8 shuttleasgi 2>&1
	@flake8 tests 2>&1


check-isort:
	@echo "$(BOLD)Checking isort$(RESET)"
	@isort --check-only shuttleasgi 2>&1
	@isort --check-only tests 2>&1
	@isort --check-only itests 2>&1


check-black:  ## Run the black tool in check mode only (won't modify files)
	@echo "$(BOLD)Checking black$(RESET)"
	@black --check shuttleasgi 2>&1
	@black --check tests 2>&1
	@black --check itests 2>&1
