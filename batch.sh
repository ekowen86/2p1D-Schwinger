#!/bin/bash

# *** batch script for lattice runs ***

# copies relevant code to a new directory in the batch directory, then compiles
# and runs. note that running this script multiple times with the same set of
# parameters will overwrite the directory each time.

L=$1 # lattice size
NZ=$2 # number of slices in extra dimension (ignored if D=2)
D=$3 # number of dimension (2 or 3)
BETA=$4 # lattice coupling
EPSZ=$5 # ratio of lattice coupling in extra dimension
M=$6 # fermion mass
N_THERM=$7 # number of thermalization sweeps
N_SWEEPS=$8 # number of sweeps per data collection
N_DATA=$9 # number of data values to collect
R_SMEAR=$((L/2-2)) # maximum smearing radius
WF_DT=0.02 # time step for wilson flow
WF_STEPS=1000 #$((R_SMEAR*R_SMEAR*50/8)) # number of wilson flow steps

BETAZ=$(echo "${EPSZ} * ${BETA}" | bc)

# calculate beta * 1000 and m * 1000
BETA1000=$(printf "%.0f" $(echo "${BETA} * 1000" | bc))
if [[ ${M} == -* ]]
then
    # negative mass
    M1000=$(printf "m%.0f" $(echo "-(${M}) * 1000" | bc))
else
    # positive mass
    M1000=$(printf "p%.0f" $(echo "${M} * 1000" | bc))
fi

# copy and rename the relevant folder
mkdir batch
NAME=batch/schw_${L}_${NZ}_${BETA1000}_${M1000}
echo ${NAME}
rm -r ${NAME}
cp -r wilson/${D}D ./${NAME}
# cp -r staggered/${D}D ./${NAME}

(cd ${NAME}; ./launcher.sh ${L} ${NZ} ${BETA} ${BETAZ} ${M} \
    ${N_THERM} ${N_SWEEPS} ${N_DATA} ${WF_STEPS} ${WF_DT})
