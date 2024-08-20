import numpy as np
import scipy as sc
from binhamming import binhamming


def f(theta, d, n, conj=False):
    vals = np.cos(theta)**(n-d) * (-1j * np.sin(theta))**d
    return np.conj(vals) if conj else vals


def count_ds(ds, n):
    counts = np.unique(ds, return_counts=True)
    p = np.zeros(n+1)

    for i in range(len(counts[0])):
        d = int(counts[0][i])
        p[d] = counts[1][i]

    return p


def count_ds_for_k_in_target(n, k, target):
    ds = []

    for z in target:
        ds.append(binhamming(k, z))

    return count_ds(ds, n)


def count_ds_in_target(n, target):
    ds = []

    for k in target:
        for z in target:
            ds.append(binhamming(k, z))

    return count_ds(ds, n)


def calc_frequency(ds, n):
    return count_ds(ds, n) / len(ds)


def p_d_in_target(n, target):
    ds = []

    for k in target:
        for z in target:
            ds.append(binhamming(k, z))

    return calc_frequency(ds, n)


def p_d_not_in_target(n, target):
    ntarget = np.setdiff1d(np.array(list(range(2**n))), target)
    ds = []

    for k in target:
        for z in ntarget:
            ds.append(binhamming(k, z))
    return calc_frequency(ds, n)


def calc_d_for_k_in_T(k, n, target):
    ds = []

    for z in target:
        ds.append(binhamming(k, z))

    return count_ds(ds, n)


def calc_c_k(k, n, phi, target, ts):
    vals = np.zeros(len(ts), dtype=np.cfloat)

    nd_in_T = calc_d_for_k_in_T(k, n, target)

    for d in range(n + 1):
        vals += nd_in_T[d] * np.exp(-1j * phi) * f(ts, d, n)
        vals += (sc.special.binom(n, d) - nd_in_T[d]) * f(ts, d, n)

    return vals


def uniform_target(n=10, est_T_size_fract=0.5):
    return np.unique(np.random.randint(0, 2**n - 1, int(est_T_size_fract * 2**n)))


def w(d1, d2, n, phi, ReIm, d_count):
    
    def factor(d, nd, n, phi):
        return nd * np.cos(phi) + sc.special.binom(n, d) - nd

    if ReIm == "Re":
        if d1 % 2 == 0 and d2 % 2 == 0:
            return factor(d1, d_count[d1], n, phi) * factor(d2, d_count[d2], n, phi)
        if d1 % 2 == 0 and (d2 + 1) % 2 == 0:
            return -1j * factor(d1, d_count[d1], n, phi) * d_count[d2] * np.sin(phi)
        if (d1 + 1) % 2 == 0 and d2 % 2 == 0:
            return -1j * factor(d2, d_count[d2], n, phi) * d_count[d1] * np.sin(phi)
        if d1 % 2 == 1 and d2 % 2 == 1:
            return -1 * d_count[d1] * d_count[d2] * np.sin(phi)**2

    if ReIm == "Im":
        if d1 % 2 == 1 and d2 % 2 == 1:
            return -1 * factor(d1, d_count[d1], n, phi) * factor(d2, d_count[d2], n, phi)
        if d1 % 2 == 1 and (d2 + 1) % 2 == 1:
            return 1j * factor(d1, d_count[d1], n, phi) * d_count[d2] * np.sin(phi)
        if (d1 + 1) % 2 == 1 and d2 % 2 == 1:
            return 1j * factor(d2, d_count[d2], n, phi) * d_count[d1] * np.sin(phi)
        if d1 % 2 == 0 and d2 % 2 == 0:
            return d_count[d1] * d_count[d2] * np.sin(phi)**2


def c_k_d(k, d, nd, n, ts, phi, ReIm):

    if ReIm == "Re":
        if d % 2 == 0:
            return (nd * np.cos(phi) + sc.special.binom(n, d) - nd) * f(ts, d, n)
        else:
            return -1j * nd * np.sin(phi) * f(ts, d, n)
    else:
        if d % 2 == 1:
            return -1j * (nd * np.cos(phi) + sc.special.binom(n, d) - nd) * f(ts, d, n)
        else:
            return -1 * nd * np.sin(phi) * f(ts, d, n)
