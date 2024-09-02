# Contributing

This project welcomes contributions and suggestions. Please submit a PR to the `main` branch with 
any updates. Make sure to update the changelog with any information about the contribution.


## Environment Setup

To install development dependencies, use [`poetry`](https://python-poetry.org/):

```
poetry install
```

## Running Tests

To run the tests for `fica`, use the `test` `Makefile` target.

```
make test
```

To run tests with coverage or generate the HTML coverage report, use the `testcov` or `htmlcov`
targets, respectively.


## Building the Documentation

To build a local copy of the documentation, use the `docs` target of the `Makefile`.

```
make docs
```

This will create HTML output in the `docs/_build/html` directory which you can view in your browser.
