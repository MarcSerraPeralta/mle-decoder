# mle-decoder

Most-likely error (MLE) decoder that uses gurobi to solve the mixed-interger (linear) programming problem


# MLE optimization description

The problem of finding the most likely error can be mapped to a mixed-integer (linear) programming (MILP) problem. 
This can be solved by optimization solvers like Gurobi. The mapping to a MILP problem is

![alt text](https://github.com/MarcSerraPeralta/mle-decoder/blob/main/images/image.jpg?raw=true)

_(source: https://arxiv.org/abs/2403.03272)_
