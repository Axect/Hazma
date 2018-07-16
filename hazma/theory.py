from .gamma_ray_limits.gamma_ray_limit_parameters import A_eff_e_astrogam
from .gamma_ray_limits.gamma_ray_limit_parameters import T_obs_e_astrogam
from .gamma_ray_limits.gamma_ray_limit_parameters import draco_params
from .gamma_ray_limits.gamma_ray_limit_parameters import default_bg_model
from .gamma_ray_limits.gamma_ray_limit_parameters import energy_res_e_astrogam
from .gamma_ray_limits.compute_limits import (unbinned_limit as ubl,
                                              binned_limit as bl)
from .cmb import f_eff, cmb_limit
from .gamma_ray_limits.compute_limits import get_detected_spectrum
from .constraint_parameters import sv_inv_MeV_to_cm3_per_s

import numpy as np
from skimage import measure
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
    def spectra(self, e_gams, cme):
        pass

    @abstractmethod
    def spectrum_functions(self):
        pass

    def total_spectrum(self, e_gams, e_cm):
        """Returns total gamma ray spectrum.

        Parameters
        ----------
        e_gams : float or float numpy.array
            Photon energy or energies at which to compute the spectrum.
        e_cm : float
            DM center of mass energy.

        Returns
        -------
        tot_spec : float numpy.array
            Array containing the total annihilation spectrum.
        """
        if hasattr(e_gams, "__len__"):
            return self.spectra(e_gams, e_cm)["total"]
        else:
            return self.spectra(np.array([e_gams]), e_cm)["total"]

    @abstractmethod
    def positron_spectra(self, e_ps, e_cm):
        pass

    def total_positron_spectrum(self, e_ps, e_cm):
        """Returns total positron ray spectrum.

        Parameters
        ----------
        e_ps : float or float numpy.array
            Positron energy or energies at which to compute the spectrum.
        e_cm : float
            DM center of mass energy.

        Returns
        -------
        tot_spec : float numpy.array
            Array containing the total annihilation positron spectrum.
        """
        if hasattr(e_ps, "__len__"):
            return self.positron_spectra(e_ps, e_cm)["total"]
        else:
            return self.positron_spectra(np.array([e_ps]), e_cm)["total"]

    @abstractmethod
    def positron_lines(self, e_cm):
        pass

    def binned_limit(self, measurement, n_sigma=2.):
        return bl(self.total_spectrum, self.gamma_ray_lines, self.mx, False,
                  measurement, n_sigma)

    def binned_limits(self, mxs, measurement, n_sigma=2.):
        lims = []

        for mx in mxs:
            self.mx = mx
            lims.append(self.binned_limit(measurement, n_sigma))

        return np.array(lims)

    def unbinned_limit(self, A_eff=A_eff_e_astrogam,
                       energy_res=energy_res_e_astrogam,
                       T_obs=T_obs_e_astrogam, target_params=draco_params,
                       bg_model=default_bg_model, n_sigma=5.,
                       debug_msgs=False):
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
        return ubl(self.total_spectrum, self.gamma_ray_lines, self.mx, False,
                   A_eff, energy_res, T_obs, target_params, bg_model, n_sigma,
                   debug_msgs=debug_msgs)

    def unbinned_limits(self, mxs, A_eff=A_eff_e_astrogam,
                        energy_res=energy_res_e_astrogam,
                        T_obs=T_obs_e_astrogam, target_params=draco_params,
                        bg_model=default_bg_model, n_sigma=5.,
                        debug_msgs=False):
        """Computes gamma ray constraints over a range of DM masses.

        See documentation for :func:`unbinned_limit`.
        """
        lims = []

        for mx in mxs:
            self.mx = mx
            lims.append(self.unbinned_limit(A_eff, energy_res, T_obs,
                                            target_params, bg_model, n_sigma,
                                            debug_msgs))

        return np.array(lims)

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
        f_eff_dm = f_eff(self.total_spectrum, self.gamma_ray_lines,
                         self.total_positron_spectrum, self.positron_lines,
                         self.mx, x_kd)

        return cmb_limit(self.mx, f_eff_dm)

    def cmb_limits(self, mxs, x_kd=1.0e-4):
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
        lims = []

        for mx in mxs:
            self.mx = mx
            lims.append(self.cmb_limit(x_kd))

        return np.array(lims)

    def f_eff(self, x_kd=1.0e-4):  # TODO: clean this up...
        spec_fn = self._get_f_eff_spec_fn()
        pos_spec_fn = self._get_f_eff_pos_spec_fn()

        return f_eff(spec_fn, self.gamma_ray_lines, pos_spec_fn,
                     self.positron_lines, self.mx, x_kd)

    def f_effs(self, mxs, x_kd=1.0e-4):
        f_eff_vals = []

        for mx in mxs:
            self.mx = mx
            f_eff_vals.append(self.f_eff(x_kd))

        return np.array(f_eff_vals)

    def custom_constrain(self, param_grid, ls_or_img="image"):
        """Computes constraints over grid of parameter values.

        Parameters
        ----------
        param_grid : 2D array of parameters
            Parameter values at which to compute constraints.
        ls_or_img : "image" or "ls"
            Controls whether this function returns level sets or images.

        Returns
        -------
        constrs : dict
            A dictionary containing the constraints on the theory in the (p1,
            p2) plane.

            If ls_or_img is "ls", the values are level sets. A level set is a
            list of curves, where each curve is a list of values of (p1, p2)
            defining the parameter values that saturate the constraint. If
            ls_or_img is "image", each value is a 2D numpy.array I(x,y) such
            that I_ij > 0 when (p1_vals[i], p2_vals[j]) is not excluded by the
            corresponding constraint and I_ij < 0 if (p1_vals[i], p2_vals[j])
            is excluded by the constraint.
        """
        n_rows, n_cols = param_grid.shape
        constraints = self.constraints()

        # Store the constraint images. Note that p1 and p2 must be swapped
        # so we can use Cartesian rather than matrix indexing.
        imgs = {cn: np.zeros([n_rows, n_rows]) for cn in constraints.keys()}

        # Loop over the parameter grid
        for i in range(n_rows):
            for j in range(n_cols):
                # Set this theory's parameters to the values at this point
                self.__dict__.update(param_grid[i, j].__dict__)

                # Compute all constraints at this point in parameter space
                for cn, fn in constraints.iteritems():
                    imgs[cn][i, j] = fn()

        if ls_or_img == "image":
            return imgs
        elif ls_or_img == "ls":
            return {cn: _img_to_ls(img) for cn, img in imgs}

    def constrain(self, p1, p1_vals, p2, p2_vals, ls_or_img="image"):
        """Computes constraints over 2D slice of parameter space.

        Parameters
        ----------
        p1 : string
            Name of a parameter to constraint.
        p1_vals : np.array
            Values of p1 at which to compute constraints. Must be sorted.
        p2 : string
            Name of the other parameter to constraint. Must be different than
            p1.
        p2_vals : np.array
            Values of p2 at which to compute constraints. Must be sorted.
        ls_or_img : "image" or "ls"
            Controls whether this function returns level sets or images.

        Returns
        -------
        constrs : dict
            A dictionary containing the constraints on the theory in the (p1,
            p2) plane.

            If ls_or_img is "ls", the values are level sets. A level set is a
            list of curves, where each curve is a list of values of (p1, p2)
            defining the parameter values that saturate the constraint. If
            ls_or_img is "image", each value is a 2D numpy.array I(x,y) such
            that I_ij > 0 when (p1_vals[i], p2_vals[j]) is not excluded by the
            corresponding constraint and I_ij < 0 if (p1_vals[i], p2_vals[j])
            is excluded by the constraint.
        """
        if p1 == p2:
            raise ValueError("Parameters being constrained must not be the "
                             "same. Both are %s." % p1)

        n_p1s, n_p2s = len(p1_vals), len(p2_vals)
        constraints = self.constraints()

        # Store the constraint images. Note that p1 and p2 must be swapped
        # so we can use Cartesian rather than matrix indexing.
        imgs = {cn: np.zeros([n_p2s, n_p1s]) for cn in constraints.keys()}

        # Loop over the parameter values
        for idx_p1, p1_val in np.ndenumerate(p1_vals):
            for idx_p2, p2_val in np.ndenumerate(p2_vals):
                setattr(self, p1, p1_val)
                setattr(self, p2, p2_val)

                # Compute all constraints at this point in parameter space
                for cn, fn in constraints.iteritems():
                    imgs[cn][idx_p2[0], idx_p1[0]] = fn()

        if ls_or_img == "image":
            return imgs
        elif ls_or_img == "ls":
            return {cn: _img_to_ls(img) for cn, img in imgs}

    @abstractmethod
    def constraints(self):
        """Get a dictionary of all available constraints.

        Notes
        -----
        Each key in the dictionary is the name of a constraint. Each value is a
        function that is positive when the constraint is satisfied and negative
        when it is not.
        """
        pass

    def constrain_gamma_helper(self, p2, p2_vals, measurement, n_sigma=2):
        """Computes constraints on a parameter from gamma ray experiments.

        Notes
        -----
        p2 must not depend on mx or the center of mass energy.
        """
        vx = 1.0e-3
        e_cm = 2.*self.mx*(1 + 0.5*vx**2)  # TODO: change this!

        # Factor to convert dN/dE to Phi/<sigma v>
        dm_flux_factor = (measurement.target.J * measurement.target.dOmega /
                          (2. * 4. * np.pi * self.mx**2))

        # Energy range over which to compute convolved spectrum
        e_bin_min, e_bin_max = measurement.bins[0][0], measurement.bins[-1][1]

        def get_bin_fluxes(spec_fn, line_fn):
            """Gets Phi/<sigma v> for a particular channel.
            """
            dnde_det = get_detected_spectrum(spec_fn, line_fn, e_bin_min,
                                             e_bin_max, e_cm,
                                             measurement.energy_res, 500)
            return np.array([dm_flux_factor*dnde_det.integral(bl, br)
                             for bl, br in measurement.bins])

        # Compute Phi/<sigma v> in each bin for each final state
        fs_bin_fluxes = {fs: get_bin_fluxes(spec_fn, lambda e_cm: {})
                         for fs, spec_fn in
                         self.spectrum_functions().iteritems()
                         if fs != "total"}
        # line_bin_fluxes = {fs: get_bin_fluxes(None, line_fn) for fs, line_fn
        #                    in self.gamma_ray_lines(cme) if fs != "total"}

        def flux_difference(p2, p2_val):
            """Compute difference between Phi_obs+N*sigma - Phi_th.
            """
            setattr(self, p2, p2_val)

            # Compute cross sections
            css = self.cross_sections(e_cm)
            # Get fluxes by multiplying <sigma v>
            bin_fluxes = np.array([bf * css[fs] * vx * sv_inv_MeV_to_cm3_per_s
                                   for fs, bf in fs_bin_fluxes.iteritems()])
            # bin_fluxes += np.array([bf * css[fs] * vx * sv_inv_MeV_to_cm3_per_s
            #                         for fs, bf in line_bin_fluxes])

            print "phi_obs = ", \
                measurement.fluxes+n_sigma*measurement.upper_errors
            print "phi_th = ", bin_fluxes.sum(axis=0)

            return np.min(measurement.fluxes+n_sigma*measurement.upper_errors -
                          bin_fluxes.sum(axis=0))

        return np.array([flux_difference(p2, p2v) for p2v in p2_vals])

    def constrain_gamma(self, p1, p1_vals, p2, p2_vals, measurement,
                        n_sigma=2):
        """Computes constraints from gamma ray experiments in the p1-p2 plane.

        Notes
        -----
        p1 must not depend on mx or the center of mass energy.
        """
        img = np.zeros([len(p2_vals), len(p1_vals)])

        for idx_p1, p1_val in enumerate(p1_vals):
            setattr(self, p1, p1_val)

            # Compute constraint function along the current column
            img[idx_p1, :] = self.constrain_gamma_helper(p2, p2_vals,
                                                         measurement, n_sigma)

        return img


def _img_to_ls(p1_vals, p2_vals, img):
    """Finds levels sets for an image.
    """
    contours_raw = measure.find_contours(img, level=0)
    contours = []

    # Convert from indices to values of p1 and p2
    for c in contours_raw:
        p1s = c[:, 1] / len(p1_vals) * (p1_vals[-1] - p1_vals[0]) + p1_vals[0]
        p2s = c[:, 0] / len(p2_vals) * (p2_vals[-1] - p2_vals[0]) + p2_vals[0]
        contours.append(np.array([p1s, p2s]))

    return contours
