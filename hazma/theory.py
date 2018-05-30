from .gamma_ray_limits.gamma_ray_limit_parameters import A_eff_e_astrogam
from .gamma_ray_limits.gamma_ray_limit_parameters import T_obs_e_astrogam
from .gamma_ray_limits.gamma_ray_limit_parameters import draco_params
from .gamma_ray_limits.gamma_ray_limit_parameters import default_bg_model
from .gamma_ray_limits.gamma_ray_limit_parameters import energy_res_e_astrogam
from .gamma_ray_limits.compute_limits import unbinned_limit, binned_limit
from .cmb import f_eff, cmb_limit

import numpy as np
from abc import ABCMeta, abstractmethod


class Theory(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def description(self):
        pass

    @classmethod
    @abstractmethod
    def list_final_states(cls):
        pass

    @abstractmethod
    def cross_sections(self, cme):
        pass

    @abstractmethod
    def branching_fractions(self, cme):
        pass

    @abstractmethod
    def gamma_ray_lines(self, cme):
        """Returns the energies of and branching fractions into monochromatic
        gamma rays produces by this theory.
        """
        pass

    @abstractmethod
    def spectra(self, eng_gams, cme):
        pass

    @abstractmethod
    def spectrum_functions(self):
        pass

    @abstractmethod
    def positron_spectra(self, eng_es, e_cm):
        pass

    @abstractmethod
    def positron_lines(self, e_cm):
        pass

    def binned_limit(self, measurement, n_sigma=2.):
        def spec_fn(e_gams, e_cm):
            if hasattr(e_gams, "__len__"):
                return self.spectra(e_gams, e_cm)["total"]
            else:
                return self.spectra(np.array([e_gams]), e_cm)["total"]

        return binned_limit(spec_fn, self.gamma_ray_lines, self.mx, False,
                            measurement, n_sigma)

    def binned_limits(self, mxs, measurement, n_sigma=2.):
        def binned_limit_change_mass(mx):
            self.mx = mx
            return self.binned_limit(measurement, n_sigma)

        return np.vectorize(binned_limit_change_mass)(mxs)

    def unbinned_limit(self, A_eff=A_eff_e_astrogam,
                       energy_res=energy_res_e_astrogam,
                       T_obs=T_obs_e_astrogam, target_params=draco_params,
                       bg_model=default_bg_model, n_sigma=5.):
        """Computes smallest value of <sigma v> detectable for given target and
        experiment parameters.

        Notes
        -----
        We define a signal to be detectable if

        .. math:: N_S / sqrt(N_B) >= n_\sigma,

        where :math:`N_S` and :math:`N_B` are the number of signal and
        background photons in the energy window of interest and
        :math:`n_\sigma` is the significance in number of standard deviations.
        Note that :math:`N_S \propto \langle \sigma v \rangle`. While the
        photon count statistics are properly taken to be Poissonian and using a
        confidence interval would be more rigorous, this procedure provides a
        good estimate and is simple to compute.

        Parameters
        ----------
        dN_dE_DM : float -> float
            Photon spectrum per dark matter annihilation as a function of
            photon energy
        mx : float
            Dark matter mass
        dPhi_dEdOmega_B : float -> float
            Background photon spectrum per solid angle as a function of photon
            energy
        self_conjugate : bool
            True if DM is its own antiparticle; false otherwise
        n_sigma : float
            Number of standard deviations the signal must be above the
            background to be considered detectable
        delta_Omega : float
            Angular size of observation region in sr
        J_factor : float
            J factor for target in MeV^2 / cm^5
        A_eff : float
            Effective area of experiment in cm^2
        T_obs : float
            Experiment's observation time in s

        Returns
        -------
        <sigma v> : float
            Smallest detectable thermally averaged total cross section in units
            of cm^3 / s
        """
        def spec_fn(e_gams, e_cm):
            if hasattr(e_gams, "__len__"):
                return self.spectra(e_gams, e_cm)["total"]
            else:
                return self.spectra(np.array([e_gams]), e_cm)["total"]

        return unbinned_limit(spec_fn, self.gamma_ray_lines, self.mx, False,
                              A_eff, energy_res, T_obs, target_params,
                              bg_model, n_sigma)

    def unbinned_limits(self, mxs, A_eff=A_eff_e_astrogam,
                        energy_res=energy_res_e_astrogam,
                        T_obs=T_obs_e_astrogam, target_params=draco_params,
                        bg_model=default_bg_model, n_sigma=5.):
        """Computes gamma ray constraints over a range of DM masses.

        See documentation for :func:`unbinned_limit`.
        """
        def unbinned_limit_change_mass(mx):
            self.mx = mx
            return self.unbinned_limit(A_eff, energy_res, T_obs, target_params,
                                       bg_model, n_sigma)

        return np.vectorize(unbinned_limit_change_mass)(mxs)

    def cmb_limit(self, x_kd=1.0e-4):
        """Computes CMB limit on <sigma v>.

        Parameters
        ----------
        x_kd: float
            T_kd / m_x, where T_kd is the dark matter's kinetic decoupling
            temperature.

        Returns
        -------
        <sigma v> : float
            Upper bound on <sigma v>.
        """
        def spec_fn(e_gams, e_cm):
            if hasattr(e_gams, "__len__"):
                return self.spectra(e_gams, e_cm)["total"]
            else:
                return self.spectra(np.array([e_gams]), e_cm)["total"]

        def pos_spec_fn(e_ps, e_cm):
            if hasattr(e_ps, "__len__"):
                return self.positron_spectra(e_ps, e_cm)["total"]
            else:
                return self.positron_spectra(np.array([e_ps]), e_cm)["total"]

        f_eff_dm = f_eff(spec_fn, self.gamma_ray_lines, pos_spec_fn,
                         self.positron_lines, self.mx, x_kd)

        return cmb_limit(self.mx, f_eff_dm)

    def cmb_limits(self, mxs, x_kd=1.0e-4):  # TODO: clean this up...
        """Computes CMB limit on <sigma v>.

        Parameters
        ----------
        mxs : np.array
            DM masses at which to compute the CMB limits.
        x_kd: float
            T_kd / m_x, where T_kd is the dark matter's kinetic decoupling
            temperature.

        Returns
        -------
        svs : np.array
            Array of upper bounds on <sigma v> for each mass in mxs.
        """
        def cmb_limit_change_mass(mx):
            self.mx = mx
            return self.cmb_limit(x_kd)

        return np.vectorize(cmb_limit_change_mass)(mxs)

    def f_eff(self, x_kd=1.0e-4):  # TODO: clean this up...
        def spec_fn(e_gams, e_cm):
            if hasattr(e_gams, "__len__"):
                return self.spectra(e_gams, e_cm)["total"]
            else:
                return self.spectra(np.array([e_gams]), e_cm)["total"]

        def pos_spec_fn(e_ps, e_cm):
            if hasattr(e_ps, "__len__"):
                return self.positron_spectra(e_ps, e_cm)["total"]
            else:
                return self.positron_spectra(np.array([e_ps]), e_cm)["total"]

        return f_eff(spec_fn, self.gamma_ray_lines, pos_spec_fn,
                     self.positron_lines, self.mx, x_kd)

    def f_effs(self, mxs, x_kd=1.0e-4):
        def f_eff_change_mass(mx):
            self.mx = mx
            return self.f_eff(x_kd)

        return np.vectorize(f_eff_change_mass)(mxs)
