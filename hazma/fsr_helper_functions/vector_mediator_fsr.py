"""Module for computing fsr spectrum from a vector mediator.

@author - Logan Morrison and Adam Coogan.
@data - December 2017

"""
import numpy as np

alpha = 1.0 / 137.0  # Fine structure constant.


def fermion(egam, Q, mf):
    """Return the fsr spectra for fermions from decay of vector mediator.

    Computes the final state radiaton spectrum value dNdE from a vector
    mediator given a gamma ray energy of `eng_gam`, center of mass energy `cme`
    and final state fermion mass `mass_f`.

    Paramaters
    ----------
    eng_gam : float
        Gamma ray energy.
    cme: float
        Center of mass energy of mass of off-shell vector mediator.
    mass_f : float
        Mass of the final state fermion.

    Returns
    -------
    spec_val : float
        Spectrum value dNdE from vector mediator.
    """
    val = 0.0

    e, m = egam / Q, mf / Q

    if 0 < e and e < 0.5 * (1.0 - 2 * m**2):

        pre_factor = alpha / (4 * e *
                              np.sqrt(1 - 4 * m**2) * (1 + 2 * m**2) *
                              np.pi * np.sqrt(Q * (Q - 2 * e * Q)))

        terms = np.array([
            2 * np.sqrt(1 - 2 * e - 4 * m**2) *
            (1 + 2 * m**2 + 2 * e * (-1 + e - 2 * m**2)),
            -2 * np.sqrt(1 - 2 * e) *
            (1 + 2 * (-1 + e) * e - 4 * e * m**2 - 4 * m**4) * np.arctanh(
                np.sqrt(1 - 2 * e - 4 * m**2) /
                np.sqrt(1 - 2 * e)),
            np.sqrt(1 - 2 * e) *
            (1 + 2 * (-1 + e) * e - 4 * e * m**2 - 4 * m**4) *
            np.log(1 + np.sqrt(1 - 2 * e - 4 * m**2) /
                   np.sqrt(1 - 2 * e)),
            - (np.sqrt(1 - 2 * e) *
               (1 + 2 * (-1 + e) * e - 4 * e * m**2 - 4 * m**4) *
               np.log(1 - np.sqrt(1 - 2 * e - 4 * m**2) /
                      np.sqrt(1 - 2 * e)))
        ])

        val = np.real(pre_factor * np.sum(terms))

    return val