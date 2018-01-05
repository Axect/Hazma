"""
High level module to generate relativistic phase space points.

* Author - Logan A. Morrison and Adam Coogan
* Date - December 2017

TODO :
    * Write code for `generate_energy_histogram`. Might need to write
      a new lower-level cython module to do this.
"""
from .phase_space_helper_functions import phase_space_point_generator as pspg
from .phase_space_helper_functions import energy_hist_generator as ehg
import numpy as np


def split_point(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def generate_phase_space_point(masses, cme, mat_elem_sqrd=lambda klist: 1):
    """
    Generate a phase space point given a set of
    final state particles and a given center of mass energy.

    Parameters
    ----------
    masses : numpy.ndarray
        List of masses of the final state particles.
    cme : double
        Center-of-mass-energy of the process.
    mat_elem_sqrd : (double)(numpy.ndarray) {lambda klist: 1}
        Function for the matrix element squared.

    Returns
    -------
    phase_space_points : numpy.ndarray
        List of four momenta and a event weight. The returned numpy array is of
        the form {ke1, kx1, ky1, kz1, ..., keN, kxN, kyN, kzN, weight}.
    """

    point = pspg.generate_point(masses, cme)
    point[4 * len(masses)] = mat_elem_sqrd(split_point(point, 4)) * \
        point[4 * len(masses)]
    return point


def generate_phase_space(num_ps_pts, masses, cme,
                         mat_elem_sqrd=lambda klist: 1):
    """
    Generate a specified number of phase space points given a set of
    final state particles and a given center of mass energy.

    Parameters
    ----------
    num_ps_pts : int
        Total number of phase space points to generate.
    masses : numpy.ndarray
        List of masses of the final state particles.
    cme : double
        Center-of-mass-energy of the process.
    mat_elem_sqrd : (double)(numpy.ndarray) {lambda klist: 1}
        Function for the matrix element squared.

    Returns
    -------
    phase_space_points : numpy.ndarray
        List of phase space points. The phase space points are in the form
        {{ke11, kx11, ky11, kz11, ..., keN1, kxN1, kyN1, kzN1, weight1},
            .
            .
            .
         {ke1N, kx1N, ky1N, kz1N, ..., keNN, kxNN, kyNN, kzNN, weightN}}
    """

    return np.array([generate_phase_space_point(masses, cme, mat_elem_sqrd)
                     for _ in range(num_ps_pts)])


def generate_energy_histogram(num_ps_pts, masses, cme,
                              mat_elem_sqrd=lambda klist: 1, num_bins=25):
    """
    Generate a specified number of phase space points given a set of
    final state particles and a given center of mass energy.

    Parameters
    ----------
    num_ps_pts : int
        Total number of phase space points to generate.
    masses : numpy.ndarray
        List of masses of the final state particles.
    cme : double
        Center-of-mass-energy of the process.
    mat_elem_sqrd : (double)(numpy.ndarray) {lambda klist: 1}
        Function for the matrix element squared.

    Returns
    -------
    phase_space_points : numpy.ndarray
        List of phase space points. The phase space points are in the form
        {{ke11, kx11, ky11, kz11, ..., keN1, kxN1, kyN1, kzN1, weight1},
            .
            .
            .
         {ke1N, kx1N, ky1N, kz1N, ..., keNN, kxNN, kyNN, kzNN, weightN}}
    """
    num_fsp = len(masses)

    pts = generate_phase_space(num_ps_pts, masses, cme, mat_elem_sqrd)

    return ehg.space_to_energy_hist(pts, num_ps_pts, num_fsp, num_bins)
