import numpy as np
import scipy as sc
import pandas as pd
from itertools import product


def E_abs_ck_sqrd(mangle, pangle, n, df_eds, df_ed1d2):
    def pull_Eds(df_eds, d):
        return float(df_eds.loc[df_eds.d == d].Eds.iloc[0])

    def f(mangle, n, d):
        return np.cos(mangle)**(n - d) * (-1j * np.sin(mangle))**d

    def w(n, d1, d2, Ed1, Ed2, Ed1d2, pangle):
        return sum([Ed1d2 * (np.exp(-1j * pangle) - 1) * (np.exp(1j * pangle) - 1),
                    Ed1 * (np.exp(-1j * pangle) - 1) * sc.special.binom(n, d2),
                    Ed2 * (np.exp(1j * pangle) - 1) * sc.special.binom(n, d1),
                    sc.special.binom(n, d1)* sc.special.binom(n, d2)])

    def F(d1, d2, Ed1d2, Ed1, Ed2):
        return w(n, d1, d2, Ed1, Ed2, Ed1d2, pangle) * f(mangle, n, d1) * np.conj(f(mangle, n, d2))

    df = df_ed1d2.copy(deep=True)

    df["Ed1"] = df_ed1d2.apply(lambda r: pull_Eds(df_eds, r.d1), axis=1)
    df["Ed2"] = df_ed1d2.apply(lambda r: pull_Eds(df_eds, r.d2), axis=1)
    
    return np.abs(df.apply(lambda r: F(r.d1, r.d2, r.Ed1d2, r.Ed1, r.Ed2),
                    axis=1,
                    result_type="reduce").sum())

def calc_EF(mangle, pangle, n, df_eds, df_ed1d2, size_T):
    df = pd.DataFrame(np.array(list(product(mangle,pangle))),
                      columns=["mangle", "pangle"])

    def F(r):
        return np.abs((size_T / 2**n) * E_abs_ck_sqrd(r.mangle,
                                                      r.pangle,
                                                      n,
                                                      df_eds.loc[df_eds.n == n],
                                                      df_ed1d2.loc[df_ed1d2.n == n]))

    df["val"] = df.apply(F, axis=1)

    return df


def EF(mangle, pangle, n, df_eds, df_ed1d2, size_T):
    return np.abs((size_T / 2**n) * E_abs_ck_sqrd(mangle,
                                                  pangle,
                                                  n,
                                                  df_eds.loc[df_eds.n == n],
                                                  df_ed1d2.loc[df_ed1d2.n == n]))

def train(n, df_eds, df_ed1d2, size_T, init_angles=[0, 0]):
    def f(angles):
        return -1 * EF(angles[0], angles[1], n, df_eds, df_ed1d2, size_T)

    res = sc.optimize.minimize(f, init_angles)

    res["x"][0] = ((res["x"][0] + np.pi / 2) % np.pi) - np.pi/2
    res["x"][1] = res["x"][1] % (2 * np.pi)

    return res

    
