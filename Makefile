# Makefile for fica
# ----------------------
# To generate a release, use `make release` with the `VERSION` argument:
#   $ make release VERSION=0.0.1
#
# To run tests, use `make test` with the `TESTPATH` and/or `PYTESTOPTS` arguments:
#   $ make test
#
# The `testcov` target can be used to build a local copy of the code coverage in HTML:
#   $ make testcov
#
# To build the docs, use `make docs`:
#   $ make docs

PYTEST        = pytest
TESTPATH      = tests
PYTESTOPTS    = -vv
COVERAGE      = coverage
DATE         := $(shell date "+%F")

release:
	rm dist/* || :
	echo '__version__ = "$(VERSION)"' > fica/version.py
	git add fica/version.py
	git commit -m "update version info for v$(VERSION)"
	git push origin stable
	python3 setup.py sdist bdist_wheel
	hub release create -a dist/*.tar.gz -a dist/*.whl -m 'v$(VERSION)' $(VERSION)
	python3 -m twine upload dist/*

test:
	$(PYTEST) $(TESTPATH) $(PYTESTOPTS)

testcov:
	$(COVERAGE) run -m pytest $(TESTPATH) $(PYTESTOPTS) 

.PHONY: htmlcov
htmlcov: testcov
	$(COVERAGE) html

.PHONY: docs
docs:
	$(MAKE) -C docs html
