#!/bin/bash

# Simple test script to demonstrate how to use the 2D U(1) code
# The size of the lattice (L) is hardcoded in the main.cpp file
# to make writing new code simpler. Please please edit and remake
# if you wish to vary L.

rm -rf {gauge,data}
mkdir -p {gauge,data/{data,plaq,creutz,polyakov,rect,top,pion,vacuum}}

L=$1 # lattice size
BETA=$3 # lattice coupling
M=$5 # fermion mass
N_THERM=$6 # number of thermalization sweeps
N_SWEEPS=$7 # number of sweeps per data collection
N_DATA=$8 # number of data values to collect
WF_STEPS=$9 # number of wilson flow steps
WF_DT=${10} # wilson flow time step

# configure preamble
#---------------------------------------------------------------
LX=${L}
LY=${L}
# Construct the correct executable
cp main_template.cpp main.cpp
cp Makefile_template Makefile

sed -i '.bak' -e s/__LX__/${LX}/g main.cpp Makefile
sed -i '.bak' -e s/__LY__/${LY}/g main.cpp Makefile

rm *.bak
make
#---------------------------------------------------------------

# The total number of HMC iterations to perform.
HMC_ITER=$((${N_SWEEPS}*${N_DATA}))
# The number of HMC iterations for thermalisation.
HMC_THERM=${N_THERM}
# The number of HMC iterations to skip bewteen measurements.
HMC_SKIP=${N_SWEEPS}
# Dump the gauge field every HMC_CHKPT iterations after thermalisation.
HMC_CHKPT=5000
# If non-zero, read in the HMC_CHKPT_START gauge field.
HMC_CHKPT_START=0
# HMC time steps in the integration
HMC_NSTEP=40
# HMC trajectory time
HMC_TAU=1.0

# The RNG seed
RNG_SEED=1234

# DYNAMIC (1) or QUENCHED (0)
DYN_QUENCH=0

# Lock the Z gauge to unit (1) or allow z dynamics (0)
ZLOCKED=1

# Dynamic fermion parameters
# Fermion mass
MASS=${M}
# Maximum CG iterations
MAX_CG_ITER=1000
# CG tolerance
CG_EPS=1e-16

# Eigensolver parameters
# Tolerance on the residual
TOL=1e-8
# Maximum ARPACK iterations
ARPACK_MAXITER=100000

#polyACC (experimental)
USE_ACC=0
AMAX=11
AMIN=1.0
N_POLY=100

# Measurements: 1 = measure, 0 = no measure
# Polyakov loops
MEAS_PL=0
# Wilson loops and Creutz ratios
MEAS_WL=1
# Pion Correlation function
MEAS_PC=1
# Vacuum trace
MEAS_VT=0

command="./2D-Wilson-LX$LX-LY$LY $BETA $HMC_ITER $HMC_THERM $HMC_SKIP $HMC_CHKPT
         $HMC_CHKPT_START $HMC_NSTEP $HMC_TAU $WF_STEPS $WF_DT $RNG_SEED
	 $DYN_QUENCH $MASS $MAX_CG_ITER $CG_EPS $TOL $ARPACK_MAXITER $USE_ACC $AMAX
    	 $AMIN $N_POLY $MEAS_PL $MEAS_WL $MEAS_PC $MEAS_VT"

echo $command

$command
