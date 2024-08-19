import numpy as np
import seaborn as sns
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


def plot(n=10, phi=1.2, ts=np.linspace(0, np.pi, 100), est_T_size_fract=0.5):
    target = np.unique(np.random.randint(0, 2**n - 1, int(est_T_size_fract * 2**n)))
    size_T = len(target)
    p_in_T = p_d_in_target(n, target)
    vals = np.zeros(len(ts), dtype=np.cfloat)

    for d in range(n + 1):
        vals += p_in_T[d] * size_T * np.exp(-1j * phi) * f(ts, d, n)
        vals += (sc.special.binom(n, d) - p_in_T[d] * size_T) * f(ts, d, n)

    return sns.lineplot(x=ts, y=(size_T / 2**n) * np.abs(vals)**2)


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


def plot_F_with_num_of_d_in_T(n=10,
                              phi=1.2,
                              ts=np.linspace(0, np.pi, 100),
                              target=None,
                              est_T_size_fract=0.5):

    if target is None:
        target = uniform_target(n, est_T_size_fract)

    vals = np.zeros(len(ts), dtype=np.cfloat)

    for k in target:
        vals += np.abs(calc_c_k(k, n, phi, target, ts))**2

    return sns.lineplot(x=ts, y=vals / (2**n))


def plot_F_with_external_mean_over_c_k(n=10,
                                       phi=1.2,
                                       ts=np.linspace(0, np.pi, 100),
                                       target=None,
                                       est_T_size_fract=0.5,
                                       label=None):

    if target is None:
        target = uniform_target(n, est_T_size_fract)

    vals = np.zeros(len(ts), dtype=np.cfloat)

    for k in target:
        vals += np.abs(calc_c_k(k, n, phi, target, ts))**2

    vals /= len(target)

    return sns.lineplot(x=ts, y= (len(target)/2**n) * vals, label=label)


def plot_F_with_internal_mean_over_c_k(n=10,
                                       phi=1.2,
                                       ts=np.linspace(0, np.pi, 100),
                                       target=None,
                                       est_T_size_fract=0.5,
                                       label=None):
    if target is None:
        target = uniform_target(n, est_T_size_fract)

    size_T = len(target)
    p_in_T = p_d_in_target(n, target)
    vals = np.zeros(len(ts), dtype=np.cfloat)

    for d in range(n + 1):
        vals += p_in_T[d] * size_T * np.exp(-1j * phi) * f(ts, d, n)
        vals += (sc.special.binom(n, d) - p_in_T[d] * size_T) * f(ts, d, n)

    return sns.lineplot(x=ts, y=(size_T / 2**n) * np.abs(vals)**2, label=label)


def plot2(n=10,
                                       phi=1.2,
                                       ts=np.linspace(0, np.pi, 100),
                                       target=None,
                                       est_T_size_fract=0.5,
                                       label=None):
    if target is None:
        target = uniform_target(n, est_T_size_fract)

    size_T = len(target)
    p_in_T = p_d_in_target(n, target)
    vals = np.zeros(len(ts), dtype=np.cfloat)

    for d1 in range(n + 1):
        for d2 in range(n + 1):
            tmp_vals = np.zeros(len(ts), dtype=np.cfloat)
            tmp_vals += p_in_T[d1] * p_in_T[d2] * 2 * (1 - np.cos(phi))
            tmp_vals += sc.special.binom(n, d2) * p_in_T[d1] * (np.exp(-1j * phi) - 1)
            tmp_vals += sc.special.binom(n, d1) * p_in_T[d2] * (np.exp(1j * phi) - 1)
            tmp_vals += sc.special.binom(n, d1) * sc.special.binom(n, d2)

            vals += tmp_vals * f(ts, d1, n) * f(ts, d2, n, conj=True)

    return sns.lineplot(x=ts, y=(size_T / 2**n) * np.abs(vals), label=label)


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


def plot_with_Im_Re(n=10,
                    phi=1.2,
                    ts=np.linspace(0, np.pi, 100),
                    target=None,
                    est_T_size_fract=0.5,
                    label=None):
    if target is None:
        target = uniform_target(n, est_T_size_fract)

    vals = np.zeros(len(ts), dtype=np.cfloat)

    for k in target:
        p_in_T = count_ds_for_k_in_target(n, k, target)

        for d1 in range(n + 1):
            for d2 in range(n + 1):
                vals += (w(d1, d2, n, phi, "Re", p_in_T) +
                         w(d1, d2, n, phi, "Im", p_in_T)) * f(ts, d1, n) * f(ts, d2, n)

    return sns.lineplot(x=ts, y=np.abs(vals) / (2**n), label=label)


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


def plot_with_cov(n=10,
                  phi=1.2,
                  ts=np.linspace(0, np.pi, 100),
                  target=None,
                  est_T_size_fract=0.5,
                  label=None):
    
    if target is None:
        target = uniform_target(n, est_T_size_fract)

    ds = [[] for d in range(n+1)]
    
    for k in target:
        tmp = count_ds_for_k_in_target(n, k, target)
        for d in range(n+1):
            ds[d].append(tmp[d])
    
    cov = np.cov(ds)
    mean_ds = list(map(lambda d: np.mean(d), ds))
    
    E_c_k = np.zeros(len(ts), dtype=np.cfloat)

    for d in range(n + 1):
        E_c_k += (mean_ds[d] * np.exp(-1j * phi) + (sc.special.binom(n, d) - mean_ds[d])) * f(ts, d, n)

    vals = np.zeros(len(ts), dtype=np.cfloat)
    vals += np.abs(E_c_k)**2
    
    for d1 in range(n+1):
        for d2 in range(n+1):
            vals += 2 * (1 - np.cos(phi)) * cov[d1][d2] * f(ts, d1, n) * f(ts, d2, n, conj=True)
    
    vals /= 2**n

    sns.lineplot(x=ts, y=len(target) * np.real(vals))


def plot_with_Pd(n=10,
                 phi=1.2,
                 ts=np.linspace(0, np.pi, 100),
                 target=None,
                 est_T_size_fract=0.5,
                 label=None):
    
    ds = []
    ds_per_run = [[] for d in range(n+1)]
    
    for m in range(10):
        target = uniform_target(n=n, est_T_size_fract=est_T_size_fract)
        for k in target:
            # tmp = count_ds_for_k_in_target(n, k, target)
            # for d in range(n+1):
            #     ds_per_run[d].append(tmp[d])
            for z in target:
                ds.append(binhamming(k,z))

    _, nds = np.unique(ds, return_counts=True)
    Pd = nds  / sum(nds)

    T_size = 2**n * est_T_size_fract

    Eck = np.zeros(len(ts), dtype=np.cfloat)
    for d in range(n+1):
        Eck += (Pd[d] * T_size * np.exp(-1j * phi) + (sc.special.binom(n, d) - Pd[d] * T_size)) * f(ts, d, n)
        # Eck += (np.mean(ds[d]) * np.exp(-1j * phi) + (sc.special.binom(n, d) - np.mean(ds[d]))) * f(ts, d, n)

        
    vals = np.zeros(len(ts), dtype=np.cfloat)
    vals += np.abs(Eck)**2
   
    # _cov = np.cov(ds_per_run)

    def cov(d1, d2):
        if d1 == 0 or d2 == 0:
            return 0

        return 1 if d1 == d2 else 0
        # return 0.5 * T_size**2 * Pd[d1] * Pd[d2]
        # return _cov[d1][d2]
        
    for d1 in range(n+1):
        for d2 in range(n+1):
            vals += 2 * (1 - np.cos(phi)) * cov(d1, d2) * f(ts, d1, n) * f(ts, d2, n, conj=True)
    
    vals /= 2**n

    sns.lineplot(x=ts, y=len(target) * np.real(vals))
