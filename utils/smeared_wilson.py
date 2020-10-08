import numpy as np
import matplotlib.pyplot as plt
import bz2
import scipy.optimize as opt
import cmath
import sys
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

id = "16_1_10000_p0"
R = 16
n_max = 100
n_data = 100

def jackknife_mean(a, n_sub):
	if (n_sub == 0):
		n_sub = len(a)
	f_sub = float(n_sub) # number of data subsets
	start = 0 # start of current block of data
	count = len(a) # number of data points
	size = count / n_sub # size of each block

	a_bar = np.mean(a)
	d_a = 0.0

	for n in range(0, n_sub):
		end = np.minimum(start + size, count)
		r = range(start, end)

		# copy each array and delete the current subset
		a_del = np.delete(a, r)

		# calculate the creutz ratio and add to the error
		d_a += (np.mean(a_del) - a_bar)**2.0

		start = end

	d_a = np.sqrt((f_sub - 1) / f_sub * d_a)
	return (a_bar, d_a)


def creutz_ratio(w00, w01, w11):
	w00_bar = np.mean(w00)
	w01_bar = np.mean(w01)
	w11_bar = np.mean(w11)
	return -np.log(w00_bar * w11_bar / w01_bar**2.0)


def jackknife_creutz(w00, w01, w11, n_sub):
	if (n_sub == 0):
		n_sub = len(w00)
	f_sub = float(n_sub) # number of data subsets
	start = 0 # start of current block of data
	count = len(w00) # number of data points
	size = count / n_sub # size of each block

	chi_bar = creutz_ratio(w00, w01, w11)
	d_chi = 0.0

	for n in range(0, n_sub):
		end = np.minimum(start + size, count)
		r = range(start, end)

		# copy each array and delete the current subset
		w00_d = np.delete(w00, r)
		w01_d = np.delete(w01, r)
		w11_d = np.delete(w11, r)

		# calculate the creutz ratio and add to the error
		d_chi += (creutz_ratio(w00_d, w01_d, w11_d) - chi_bar)**2.0

		start = end

	d_chi = np.sqrt((f_sub - 1) / f_sub * d_chi)
	return (chi_bar, d_chi)


def parse_data_file(file):
	a = np.empty((n_max+1,n_data))
	i = 0
	for line in file.readlines():
		tok = line.split()
		n = int(tok[0])
		a[n,i] = float(tok[1])
		if (n == n_max):
			i += 1
	return a


filename = "../batch/schw_" + id + "/data/rect/rectWL"
w00file = open(filename + "_" + str(R) + "_" + str(R) + ".dat", "r")
w00 = parse_data_file(w00file)
w01file = open(filename + "_" + str(R) + "_" + str(R+1) + ".dat", "r")
w01 = parse_data_file(w01file)
w10file = open(filename + "_" + str(R+1) + "_" + str(R) + ".dat", "r")
w10 = parse_data_file(w10file)
w11file = open(filename + "_" + str(R+1) + "_" + str(R+1) + ".dat", "r")
w11 = parse_data_file(w11file)

N = np.empty(n_max+1)
chi = np.empty(n_max+1)
d_chi = np.empty(n_max+1)

for n in range(0,n_max):
	N[n] = n
	chi[n], d_chi[n] = jackknife_creutz(w00[n], (w01[n] + w10[n]) / 2.0, w11[n], 5)

# plot creutz ratio vs n_wf
plt.figure()
plt.xlim(0, 200)
plt.ylim(0.0,0.12)
# plt.yscale("log")
# plt.ylim(0.0, W[1] + 0.1)
plt.errorbar(N, chi, yerr=d_chi, color="blue", marker='o', ms=5, mew=0.5, mfc='none', linestyle='none', linewidth=0.5, capsize=2.5, capthick=0.5)
plt.xlabel("$n_{wf}$")
plt.ylabel("$\chi(R,R)$")
plt.savefig("../plots/" + id + "_wf.pdf")
plt.close()
