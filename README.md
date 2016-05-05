# README #

A probabilistic calibration method for discrete element models of granular materials using the particle filter

Monte Carlo simulations are prepared by parallel Yade sessions with parameter sets generated by Halton sequence. Only the observation data file is needed to beforehand. The names and ranges of parameters have to be in the same order. Number of simulation steps and observation data must be the same. The identified values come in the forms of probability density functions if the covariance is wisely chosen.

The following packages are needed:

* Primary:
    Discrete Element Method: Yade (http://yade-dem.org/)
    Halton number generator: ghalton (https://pypi.python.org/pypi/ghalton)
    Particle filter code:    particle_filter.f90 (compilable with gfortran)

* Others:
    numpy
    matplotlib
 
* Files

  ./PeriSp_*n*_0.68* are txt files that save configurations of DEM packing consist of *n* elements with 0.68 initial void ratio and negligible inter-particle forces.

  ./mcTriaxCL.py and ./mcTriaxHM.py are Yade scripts for DEM simulations of quasi-static compression tests. CL and HM stand for Cundall's Linear law and Hertz-Mindlin law.

  ./example contains the following files that consist a minimal working example

     main: getParams.py
     Yade: mcTriax.py
     Halton number: tableGenerator.py
     plot figures: plotResults.py
     parameter table: table.dat (generated by tableGenerator.py)
     test data: obsdata.dat
     *others* are generated by the main script to be used by the particle filter PF.exe