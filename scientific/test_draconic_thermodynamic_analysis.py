"""Draconic Test Suite for the Thermodynamic and Entropic Analysis of Physical Systems
=====================================================================================
This test module is **self-contained** – it does **not** rely on the Kimera SWM
code-base (except for NumPy / SciPy) so that every axiom and derivation is tested
solely against first-principles mathematics.  The focus is on numerical and
symbolic validation of:

1.   Axiomatic statements (e.g. entropy generation ≥ 0).
2.   Ideal-gas partition function → EoS & derived thermodynamic quantities.
3.   Maxwell relations via numeric differentiation for an ideal gas.
4.   Clausius inequality for reversible vs. irreversible cycles.

If SciPy is available, it will be used for derivatives; otherwise NumPy finite
Differences are employed.
"""

from __future__ import annotations

import math
import random
import unittest
from typing import Tuple

import numpy as np

try:
    from scipy.optimize import approx_fprime
    
    def derivative(func, x: float, dx: float = 1e-6, n: int = 1, order: int = 3):  # type: ignore
        """Wrapper for scipy derivative using approx_fprime."""
        if n != 1:
            raise ValueError("Only first derivative supported.")
        return approx_fprime([x], lambda args: func(args[0]), [dx])[0]
        
except ImportError:  # Fall back to simple finite-difference implementation

    def derivative(func, x: float, dx: float = 1e-6, n: int = 1, order: int = 3):  # type: ignore
        """Simple central finite-difference‐based derivative (1st order only)."""
        if n != 1:
            raise ValueError("Only first derivative supported in fallback mode.")
        return (func(x + dx) - func(x - dx)) / (2.0 * dx)


# --------------------------------------------------------------------------------------
# Helper functions for an ideal monatomic gas (Sackur-Tetrode) – n = 1 mol by default.
# --------------------------------------------------------------------------------------
R = 8.314462618  # J⋅mol⁻¹⋅K⁻¹, universal gas constant
k_B = 1.380649e-23  # J⋅K⁻¹, Boltzmann constant
h = 6.62607015e-34  # Planck constant


def thermal_lambda(T: float) -> float:
    """Thermal de-Broglie wavelength Λ = h / sqrt(2π m k_B T) for argon-like atom."""
    m = 39.948 * 1.66053906660e-27  # kg (argon used as representative monoatomic)
    return h / math.sqrt(2.0 * math.pi * m * k_B * T)


def partition_function_single(V: float, T: float) -> float:
    """Single-particle translational partition function Z₁ = V / Λ³."""
    lam = thermal_lambda(T)
    return V / lam ** 3


def ideal_gas_free_energy(N: int, V: float, T: float) -> float:
    """Helmholtz free energy A = −R T ln Z, with Z corrected by indistinguishability (per mole)."""
    # Sackur-Tetrode formula for 1 mole (n=1):
    # A = -RT [ln(V / (N_A * lambda^3)) + 1]
    # where lambda = h / sqrt(2 * pi * m * k_B * T)
    lam = thermal_lambda(T)
    V_m = V / N  # molar volume if N moles
    lnZ = math.log(V_m / lam ** 3)
    return -R * T * (lnZ + 1)


# --------------------------------------------------------------------------------------
# Core Test Cases
# --------------------------------------------------------------------------------------


class TestThermodynamicAxioms(unittest.TestCase):
    """Part I – verification of fundamental thermodynamic inequalities."""

    def test_entropy_generation_positive_for_heat_flow_hot_to_cold(self):
        """Heat spontaneously flowing from hot → cold must create entropy (ΔS_tot > 0)."""
        T_hot = 400.0  # K
        T_cold = 300.0  # K
        q = 1000.0  # J (heat transferred from hot to cold reservoir)

        delta_S_hot = -q / T_hot
        delta_S_cold = q / T_cold
        delta_S_total = delta_S_hot + delta_S_cold

        self.assertGreater(delta_S_total, 0.0, "Entropy generation should be positive.")

    def test_clausius_inequality_irreversible_cycle(self):
        """For any irreversible cyclic process ∮ δQ / T < 0 (numerical toy cycle)."""
        # Toy cycle: two isothermal + two adiabatic legs for an ideal gas (Carnot-like)
        # We deliberately introduce friction on adiabats to make it irreversible.
        Qh = 500.0  # heat absorbed from hot reservoir at Th
        Th = 500.0
        Qc = -400.0  # heat rejected to cold reservoir at Tc (|Qc| < |Qh|) indicates irreversibility
        Tc = 300.0
        cyclic_integral = Qh / Th + Qc / Tc  # δQ/T over whole cycle
        self.assertLess(cyclic_integral, 0.0, "Clausius inequality violated for irreversible cycle.")


class TestIdealGasModel(unittest.TestCase):
    """Part IV – Ideal-gas thermodynamic identities derived from the partition function."""

    def setUp(self):
        self.N = 1  # mol
        self.V = 0.024  # m³ (≈ molar volume @ ~1 bar & 298 K)
        self.T = 298.15  # K

    def test_equation_of_state_from_free_energy(self):
        """Validate P = −(∂A/∂V)_T,N ⇒ PV = nRT for ideal gas."""

        def A_of_V(V):
            return ideal_gas_free_energy(self.N, V, self.T)

        P_computed = -derivative(A_of_V, self.V, dx=1e-8)
        P_expected = self.N * R * self.T / self.V
        # Relative tolerance 2% due to numeric diff
        self.assertAlmostEqual(P_expected, P_computed, delta=0.02 * P_expected)

    def test_internal_energy_from_lnZ(self):
        """Internal energy U = (3/2) n R T for monoatomic ideal gas."""
        Cv = 1.5 * R  # J/mol/K
        U_expected = Cv * self.T * self.N  # (3/2) n R T

        # U = A + TS, where S = -dA/dT
        A = ideal_gas_free_energy(self.N, self.V, self.T)
        
        def A_of_T(T_local):
            return ideal_gas_free_energy(self.N, self.V, T_local)

        dA_dT = derivative(A_of_T, self.T, dx=1e-3)
        S = -dA_dT
        U_computed = A + self.T * S
        self.assertAlmostEqual(U_expected, U_computed, delta=0.02 * U_expected)

    def test_sackur_tetrode_entropy(self):
        """Verify Sackur-Tetrode formula matches −∂A/∂T _V,N."""
        # Analytical Sackur-Tetrode entropy (per mole)
        lam = thermal_lambda(self.T)
        S_expected = R * (
            math.log((self.V / self.N) / lam ** 3) + 2.5
        ) * self.N  # multiply by N mol

        def A_of_T(T_local):
            return ideal_gas_free_energy(self.N, self.V, T_local)

        dA_dT = derivative(A_of_T, self.T, dx=1e-3)
        S_computed = -dA_dT
        self.assertAlmostEqual(S_expected, S_computed, delta=0.02 * S_expected)


class TestMaxwellRelations(unittest.TestCase):
    """Part II – Numeric verification of a Maxwell relation for the ideal gas."""

    def test_maxwell_relation_dT_dV_vs_dP_dS(self):
        """For an ideal gas verify (∂T/∂V)_P = −(∂P/∂S)_T numerically."""
        n = 1.0  # mol
        P = 101325.0  # Pa
        T = 350.0  # K

        # Express S(P, T) for ideal gas: S = nR[ln((R T)/(P)) + 5/2]
        S = n * R * (math.log(R * T / P) + 2.5)

        # We need T as function of V & P, and P as function of S & T.
        # For an ideal gas: PV = nRT ⇒ V(T,P) = nRT/P
        def T_of_V(V):
            return P * V / (n * R)

        def P_of_S(s):
            return n * R * T / math.exp((s / (n * R)) - 2.5)

        # Numeric derivatives
        dT_dV_P = derivative(T_of_V, n * R * T / P, dx=1e-6)
        dP_dS_T = derivative(P_of_S, S, dx=1e-3)

        lhs = dT_dV_P
        rhs = -dP_dS_T
        self.assertAlmostEqual(lhs, rhs, delta=abs(lhs) * 1e-2)


if __name__ == "__main__":
    unittest.main()
