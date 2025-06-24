# mle-decoder

![example workflow](https://github.com/MarcSerraPeralta/mle-decoder/actions/workflows/ci_pipeline.yaml/badge.svg)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![PyPI](https://img.shields.io/pypi/v/mle-decoder?label=pypi%20package)

Most-likely error (MLE) decoder that uses gurobi to solve the mixed-interger (linear) programming problem.

The decoding hypergraph is specified using `stim.DetectorErrorModel`.


## MLE optimization description

The problem of finding the most likely error can be mapped to a mixed-integer (linear) programming (MILP) problem. 
This can be solved by optimization solvers like Gurobi. The mapping to a MILP problem is _(source: https://arxiv.org/abs/2403.03272)_

![alt text](https://github.com/MarcSerraPeralta/mle-decoder/blob/main/images/mle_description.png?raw=true)

Note that $C_i \in \\{-1, +1\\}$. 


## Setting up the gurobi license

1. Create a free academic account
2. Request a license, which will give you a license key
3. Install the Gurobi Optimizer (or install `gurobipy` through conda) so that we can run the `grbgetkey` command
4. Run `grbgetkey xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` using your license number
5. At the end of `~/.bashrc` add `export GRB_LICENSE_FILE=/path/to/license.lic` where the license path is printed when running the previous step
6. Run `source ~/.bashrc` or open a new terminal and check that the license installation is successful by running the `gurobi.sh` command
