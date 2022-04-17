# Makefile for fica
# ----------------------
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
