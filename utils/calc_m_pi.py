import numpy as np
import matplotlib.pyplot as plt
import bz2
import scipy.optimize as opt
import cmath
import sys
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)


id = "24_5_2000_p300"
L = int(24) # lattice size
R_half = int(L / 2) # half lattice size
R_min = 6 # min R value for fit
R_max = 12 # max R value for fit

def corr_fit(r, m, z):
    a = z * np.exp(-m * r)
    b = z * np.exp(-m * (L - r))
    return a + b

def pion_mass(corr):
    n = len(corr[0])
    r = np.empty(n)
    corr_bar = np.empty(n)
    d_corr = np.empty(n)

    for i in range(0, R_half + 1):
        r[i] = i;
        corr_bar[i] = np.mean(corr[i]);
        d_corr[i] = np.std(corr[i]) / np.sqrt(n);

    popt, pcov = opt.curve_fit(corr_fit, r[R_min-1:R_max], corr_bar[R_min-1:R_max], [0.05, 1.0], sigma=d_corr[R_min-1:R_max])
    m = popt[0]
    d_m = np.sqrt(pcov[0][0])
    z = popt[1]
    d_z = np.sqrt(pcov[1][1])
    return m, d_m, z, d_z

def jackknife_pion_mass(corr, n_sub):
	if (n_sub == 0):
		n_sub = len(corr[0])
	f_sub = float(n_sub) # number of data subsets
	start = 0 # start of current block of data
	count = len(corr[0]) # number of data points
	size = count / n_sub # size of each block

	m_bar, _, z_bar, _ = pion_mass(corr)
	d_m = 0.0
	d_z = 0.0

	for n in range(0, n_sub):
		end = np.minimum(start + size, count)
		r = range(start, end)

		# copy the array and delete the current subset
		corr_d = np.delete(corr, r, 1)

		# calculate the creutz ratio and add to the error
        m_d, _, z_d, _ = pion_mass(corr_d)
        d_m += (m_d - m_bar)**2.0
        d_z += (z_d - z_bar)**2.0

        start = end

	d_m = np.sqrt((f_sub - 1) / f_sub * d_m)
	d_z = np.sqrt((f_sub - 1) / f_sub * d_z)
	return m_bar, d_m, z_bar, d_z

def parse_data_file(file):
    lines = file.readlines()
    a = np.empty((R_half+1,len(lines)))
    i = 0
    for l, line in enumerate(lines):
        tokens = line.split()
        for t, token in enumerate(tokens):
            if (t == 0):
                continue # skip trajectory id
            a[t-1,l] = float(token)
    return a

filename = "../batch/schw_" + id + "/data/pion/pion.dat"
pion_file = open(filename, "r")
C_pi = parse_data_file(pion_file)
m_bar, d_m, z_bar, d_z = jackknife_pion_mass(C_pi, 10)

print("m = %.12f (%.12f)" % (m_bar, d_m))
print("z = %.12f (%.12f)" % (z_bar, d_z))

n = R_half + 1
R = np.empty(n)
corr_bar = np.empty(n)
d_corr = np.empty(n)

for i in range(0, n):
    R[i] = i;
    corr_bar[i] = np.mean(C_pi[i]);
    d_corr[i] = np.std(C_pi[i]) / np.sqrt(n);

# calculate best fit curves
R_A = np.linspace(0, R_half, 1000)
corr_A = np.zeros(len(R_A))
for r in range(0, len(R_A)):
	corr_A[r] = corr_fit(R_A[r], m_bar, z_bar)

plt.rcParams.update({
    "text.usetex": False,
    "font.family": "sans-serif"})

# plot C vs r
plt.figure()
plt.xlim(0, R_half)
plt.yscale("log")
# plt.ylim(0.0, chi[1] + 0.1)
plt.errorbar(R, corr_bar, yerr=d_corr, color="blue", marker='o', ms=5, mew=0.5, mfc='none', linestyle='none', linewidth=0.5, capsize=2.5, capthick=0.5)
plt.plot(R_A, corr_A, color="blue", linewidth=0.5)
plt.xlabel("$R$")
plt.ylabel("$C_{\pi}(R)$")
plt.savefig("../plots/" + id + "_pi_r.pdf")
plt.close()
