# Contributing

This project welcomes contributions and suggestions. Please submit a PR to the `main` branch with 
any updates. Make sure to update the changelog with any information about the contribution.


## Environment Setup

To set up an environment for working on `fica`, we recommend using 
[Conda](https://docs.conda.io/en/latest/miniconda.html). This repo contains an 
[`environment.yml`](environment.yml) file which defines all of the requirements for a development
environment.

Running

```
conda env create -f environment.yml
```

will create a conda environment called `fica` with the necessary packages installed for Python.


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
