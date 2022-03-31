[![Python build](https://github.com/sappelhoff/ecomp_experiment/actions/workflows/build.yml/badge.svg)](https://github.com/sappelhoff/ecomp_experiment/actions/workflows/build.yml)
[![Python style](https://github.com/sappelhoff/ecomp_experiment/actions/workflows/style.yml/badge.svg)](https://github.com/sappelhoff/ecomp_experiment/actions/workflows/style.yml)
[![Python test](https://github.com/sappelhoff/ecomp_experiment/actions/workflows/test.yml/badge.svg)](https://github.com/sappelhoff/ecomp_experiment/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/sappelhoff/ecomp_experiment/branch/main/graph/badge.svg?token=TC2BCYGJAJ)](https://codecov.io/gh/sappelhoff/ecomp_experiment)
[![DOI](https://zenodo.org/badge/406799654.svg)](https://zenodo.org/badge/latestdoi/406799654)

# eComp Experiment

This Python package implements the eComp experiment.

The archived version can be found on Zenodo:

- doi: forthcoming

## Installation

1. Download [miniconda](https://docs.conda.io/en/latest/miniconda.html)
1. Run `conda install mamba -c conda-forge`
1. Run the following commands from the root of this repository

```shell
mamba env create -f environment.yml
conda activate ecomp_experiment
pre-commit install
pip install -e .
```

## Versioning

We follow a [CalVer](https://calver.org/) inspired versioning scheme.

Namely, each version consists of `YYYY.MINOR.MICRO[.devX]`,
where `YYYY` is the full year,
`MINOR` is increased for each release that includes new features or behavior changes,
`MICRO` is increased for each release that only consists of bug fixes
or changes that don't impact the behavior of the software.

The `[.devX]` modifier is added for unreleased versions,
where `X` is replaced by a number starting with `0`.

For example, we started developing this package in 2021 in an unreleased version,
so the initial version of the package was `2021.1.0.dev0`,
signalling that the next release (currently in development iteration 0; see `dev0`),
will most likely be `2021.1`.

## Running the experiment

The experiment is intended to be run with simultaneous recording of EEG and eye-tracking data.

For more information on this, please see the `EEG` and `eye-tracking` directories respectively.

## Further resources

All important details are reported in the original paper for the project:

- preprint: forthcoming
- journal article: forthcoming

The analysis code is available:

- repository: https://github.com/sappelhoff/ecomp_analysis
- doi: forthcoming

The data is available in several formats:

- sourcedata
    - repository: https://gin.g-node.org/sappelhoff/mpib_ecomp_sourcedata
    - doi: forthcoming
- derivatives
    - repository: https://gin.g-node.org/sappelhoff/mpib_ecomp_derivatives
    - doi: forthcoming
- BIDS formatted
    - repository: https://gin.g-node.org/sappelhoff/mpib_ecomp_dataset
    - doi: forthcoming
