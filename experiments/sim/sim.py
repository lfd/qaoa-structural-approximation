import qutip as qt
from functools import reduce
import operator

def statenum2proj(n: int, num: int) -> qt.Qobj:
    qubits = list(bin(num)[2:].zfill(n))

    return qt.tensor(map(lambda q: qt.projection(2, q, q), map(int, qubits)))

def num2state(n: int, num: int) -> qt.Qobj:
    qubits = list(bin(num)[2:].zfill(n))

    return qt.tensor(map(lambda q: qt.basis(2, q), map(int, qubits)))

def C_hamiltonian(n: int, target: [int]) -> qt.Qobj:
    return sum(map(lambda num: statenum2proj(n, num), target))


def UC(pangle: float, C: qt.Qobj):
    return (-1j * pangle * C).expm()


def X(n: int, i: int):
    return qt.tensor([qt.sigmax() if i == j else qt.identity(2) for j in range(n)])


def UM(n: int, mangle: float) -> qt.Qobj:
    return (-1j * mangle * sum([X(n, i) for i in range(n)])).expm()


def ket_s(n: int) -> qt.Qobj:
    k0 = qt.tensor([qt.basis(2, 0) for i in range(n)])

    return qt.tensor([qt.core.gates.hadamard_transform(1) for i in range(n)]) * k0 


def Uqaoa(n: int, C: qt.Qobj, pangle: float, mangle: float) -> qt.Qobj:
    return UM(n, mangle) * UC(pangle, C)


def measure_ith_qubit(i: int, n: int, state: qt.Qobj):
    Z0 = qt.tensor([qt.ket2dm(qt.basis(2, 0)) if i == j else qt.identity(2) for j in range(1, n+1)])
    Z1 = qt.tensor([qt.ket2dm(qt.basis(2, 1)) if i == j else qt.identity(2) for j in range(1, n+1)])
    
    return qt.measurement.measure(state, [Z0, Z1])


def measure_bitstring(n: int, state: qt.Qobj):
    s = state.copy()

    bitstring = []
    for i in range(1, n + 1):
        b, s = measure_ith_qubit(i, n, s)
        bitstring.append(b)

    return bitstring
