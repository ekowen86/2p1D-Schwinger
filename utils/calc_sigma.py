import numpy as np
import matplotlib.pyplot as plt
import bz2
import scipy.optimize as opt
import cmath
import sys
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

id = "16_1_10000_p0"
L = int(16) # lattice size
R_half = int(L / 2) # half lattice size
R_min = 1 # min R value for fit
R_max = 3 # max R value for fit


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
	lines = file.readlines()
	a = np.empty(len(lines))
	for i, line in enumerate(lines):
		tok = line.split()
		a[i] = float(tok[0])
	return a


chi = np.empty(R_half - 2)
d_chi = np.empty(R_half - 2)
R = np.zeros(R_half - 2) # R values
_R2 = np.zeros(R_half - 2) # 1/R^2 values

print("\nCalculating Creutz ratios...")
for r in range(0, R_half - 2):

	# get R and 1/R^2
	R[r] = (r + 1.0)
	_R2[r] = 1 / R[r]**2.0

	# use a wilson flow time with a smearing radius of R-2 when
	# calculating a Creutz ratio chi(R,R), rounded down to the nearest
	# multiple of 0.02.
	# R_smear = sqrt(4 * T) in 2 dimensions
	R_smear = np.maximum(np.minimum(R[r]-4, 8), 0)
 	n_wf = int(R_smear**2.0 / 4.0 * 50.0)
#  	n_wf = np.maximum(n_wf, 0)
 	n_wf = 0
 	print("n_wf = %d" % n_wf)

	filename = "../batch/schw_" + id + "/data/rect/rectWL_hits" + str(n_wf)

	# get W(R,R)
	file00 = open(filename + "_" + str(r+1) + "_" + str(r+1) + ".dat", "r")
	w00 = parse_data_file(file00)
# 	print("w00 = %.12f" % np.mean(w00))

	# get W(R+1,R)
	file01 = open(filename + "_" + str(r+1) + "_" + str(r+2) + ".dat", "r")
	file10 = open(filename + "_" + str(r+2) + "_" + str(r+1) + ".dat", "r")
	w01 = parse_data_file(file01)
	w10 = parse_data_file(file10)
# 	print("w01 = %.12f" % np.mean(w01))
# 	print("w10 = %.12f" % np.mean(w10))

	# get W(R+1,R+1)
	file11 = open(filename + "_" + str(r+2) + "_" + str(r+2) + ".dat", "r")
	w11 = parse_data_file(file11)
# 	print("w11 = %.12f" % np.mean(w11))

	# calculate Creutz ratio
	chi[r], d_chi[r] = jackknife_creutz(w00, (w01 + w10) / 2.0, w11, 5)
	print("chi(%d,%d) = %.12f (%.12f)" % (r+1, r+1, chi[r], d_chi[r]))

# best fit for string tension
print("\nFitting string tension and plotting...")

def sigma_fit(R, sqrt_sigma, B):
	return sqrt_sigma**2.0 + B / R**2.0
# 	return sqrt_sigma**2 + B * (1 / R**2 + 1 / (L - R)**2)
# 	return sqrt_sigma**2 + B * (L / (R * (L - R)))**2

popt, pcov = opt.curve_fit(sigma_fit, R[R_min-1:R_max], chi[R_min-1:R_max], [0.05, 1.0], sigma=d_chi[R_min-1:R_max])
sqrt_sigma = popt[0]
d_sqrt_sigma = np.sqrt(pcov[0][0])
B = popt[1]
d_B = np.sqrt(pcov[1][1])
print("\nchi(R,R) = sigma + B / R^2")
print("B = %.12f (%.12f)" % (B, d_B))
print("sigma = %.12f (%.12f)" % (sqrt_sigma**2, 2 * np.abs(sqrt_sigma) * d_sqrt_sigma))
print("sqrt(sigma) = %.12f (%.12f)" % (np.abs(sqrt_sigma), d_sqrt_sigma))

# calculate best fit curves
R_A = np.linspace(0.001, R_half, 1000)
_R2_A = np.zeros(len(R_A))
chi_A = np.zeros(len(R_A))
for r in range(0, len(R_A)):
	chi_A[r] = sigma_fit(R_A[r], sqrt_sigma, B)
	_R2_A[r] = 1 / R_A[r]**2
# 	_R2_A[r] = 1 / R_A[r]**2 + 1 / (L - R_A[r])**2

plt.rcParams.update({
    "text.usetex": False,
    "font.family": "sans-serif"})

# plot chi vs R
plt.figure()
plt.xlim(0, 16)
# plt.yscale("log")
plt.ylim(0.0, chi[1] + 0.1)
plt.errorbar(R, chi, yerr=d_chi, color="blue", marker='o', ms=5, mew=0.5, mfc='none', linestyle='none', linewidth=0.5, capsize=2.5, capthick=0.5)
plt.plot(R_A, chi_A, color="blue", linewidth=0.5)
plt.xlabel("$R$")
plt.ylabel("$\chi(R,R)$")
plt.savefig("../plots/" + id + "_sigma_r.pdf")
plt.close()

# plot chi vs 1/R^2
plt.figure()
plt.xlim(0, 0.3)
# plt.yscale("log")
plt.ylim(0.0, chi[1] + 0.1)
plt.errorbar(_R2[1:], chi[1:], yerr=d_chi[1:], color="blue", marker='o', ms=5, mew=0.5, mfc='none', linestyle='none', linewidth=0.5, capsize=2.5, capthick=0.5)
plt.plot(_R2_A, chi_A, color="blue", linewidth=0.5)
plt.xlabel("$1/R^2$")
plt.ylabel("$\chi(R,R)$")
plt.savefig("../plots/" + id + "_sigma.pdf")
plt.close()
