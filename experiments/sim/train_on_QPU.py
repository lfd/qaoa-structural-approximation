from .sim import ket_s, Uqaoa, C_hamiltonian
import numpy as np
import scipy as sc


def train(target: [int], n: int, init_angles=[0, 0]) -> sc.optimize.OptimizeResult:
    def F(mangle, pangle):
        C = C_hamiltonian(n, target)
        ket_qaoa = Uqaoa(n, C, pangle, mangle) * ket_s(n)
        return abs(ket_qaoa.dag() * C * ket_qaoa)

    res = sc.optimize.minimize(lambda angls: -1 * F(angls[0], angls[1]),   
                               init_angles,
                               method="COBYLA")

    res["x"][0] = ((res["x"][0] + np.pi / 2) % np.pi) - np.pi/2
    res["x"][1] = res["x"][1] % (2 * np.pi)

    return res
    
    

