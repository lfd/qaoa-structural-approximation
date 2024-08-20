import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from binhamming import binhamming
import scipy as sc
import functools as ft

lfd_colors = ["black", "#E69F00", "#999999", "#009371", "#beaed4", "#ed665a", "#1f78b4", "#009371"]


def f(t, n, d):
    return np.cos(t)**(n - d) * (-1j * np.sin(t))**d


def ck(theta, phi, n, k, target):
    ds = [binhamming(z, k) for z in target]
    d_counts = np.zeros(n + 1)

    for d in ds:
        d_counts[int(d)] += 1

    return ft.reduce(lambda a, b: a + b, [(d_counts[d] * (np.exp(-1j * phi) - 1) + sc.special.binom(n, d)) * f(theta, n, d) for d in range(n+1)])


def plot():
    df_k10 = pd.read_csv("ck_k10.csv")
    df_k13 = pd.read_csv("ck_k13.csv")
    df_k14 = pd.read_csv("ck_k14.csv")

    theta = np.array(df_k10["theta"]).reshape((25, 100))
    phi = np.array(df_k10["phi"]).reshape((25, 100))

    X, Z = np.meshgrid(np.linspace(0, np.pi, 100),
                       np.linspace(0, 3, 100))

    z_k10 = np.array(df_k10["z"]).reshape((25, 100))
    z_k13 = np.array(df_k13["z"]).reshape((25, 100))
    z_k14 = np.array(df_k14["z"]).reshape((25, 100))
    
    fig, ax = plt.subplots(1, 3, subplot_kw={"projection": "3d"})

    fig.set_size_inches((7, 3.5))

    ts = np.linspace(-np.pi / 2, np.pi / 2, 100)
    ps = 1.2
    T = [10, 13, 14]
    n = 5

    ax[0].plot_surface(theta, phi, z_k10, alpha=0.3, color=lfd_colors[1], edgecolor=lfd_colors[1], rstride=2, cstride=2)
    ax[0].plot(ts, np.abs(ck(ts, ps, n, 10, T))**2, linewidth=2, linestyle="dashed", color="black", zs=ps, zdir="y")

    ax[1].plot_surface(theta, phi, z_k13, alpha=0.3, color=lfd_colors[3], edgecolor=lfd_colors[3], rstride=2, cstride=2)
    ax[1].plot(ts, np.abs(ck(ts, ps, n, 13, T))**2, linewidth=2, linestyle="dashed", color="black", zs=ps, zdir="y")

    ax[2].plot_surface(theta, phi, z_k14, alpha=0.3, color=lfd_colors[4], edgecolor=lfd_colors[4], rstride=2, cstride=2)
    ax[2].plot(ts, np.abs(ck(ts, ps, n, 14, T))**2, linewidth=2, linestyle="dashed", color="black", zs=ps, zdir="y")
   
    ax[0].set_xlabel("$\\beta$", labelpad=-3)
    ax[0].tick_params(pad=-3)
    ax[0].view_init(elev=12, azim=-80, roll=0)

    ax[1].set_xlabel("$\\beta$", labelpad=-3)
    ax[1].tick_params(pad=-3)
    ax[1].view_init(elev=12, azim=-80, roll=0)

    ax[2].set_xlabel("$\\beta$", labelpad=-3)
    ax[2].set_ylabel("$\\gamma$", labelpad=-3)
    ax[2].set_zlabel("$|c_k|^2$", labelpad=-3)
    ax[2].tick_params(pad=-3)
    ax[2].view_init(elev=12, azim=-80, roll=0)

    return fig


def main():
    plt.rcParams["text.usetex"] = True
    plt.rcParams["text.latex.preamble"] = r"\usepackage{lmodern}"

    plot()
    plt.tight_layout()
    plt.subplots_adjust(wspace=0, hspace=0)
    plt.savefig("ck_surfaces.pdf", bbox_inches="tight")


if __name__ == "__main__":
    main()
