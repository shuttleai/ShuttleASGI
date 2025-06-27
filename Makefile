.PHONY: compile release test annotate buildext check-isort check-black


cyt:
	cython shuttleasgi/url.pyx
	cython shuttleasgi/exceptions.pyx
	cython shuttleasgi/headers.pyx
	cython shuttleasgi/cookies.pyx
	cython shuttleasgi/contents.pyx
	cython shuttleasgi/messages.pyx
	cython shuttleasgi/scribe.pyx
	cython shuttleasgi/baseapp.pyx

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
	cython shuttleasgi/url.pyx -a
	cython shuttleasgi/exceptions.pyx -a
	cython shuttleasgi/headers.pyx -a
	cython shuttleasgi/cookies.pyx -a
	cython shuttleasgi/contents.pyx -a
	cython shuttleasgi/messages.pyx -a
	cython shuttleasgi/scribe.pyx -a
	cython shuttleasgi/baseapp.pyx -a


build: test
	python -m build


prepforbuild:
	pip install --upgrade build


testrelease:
	twine upload -r testpypi dist/*


release: clean compile artifacts
	twine upload -r pypi dist/*


test:
	pytest tests/


itest:
	APP_DEFAULT_ROUTER=false pytest itests/


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
	@flake8 itests 2>&1
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
