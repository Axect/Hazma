import numpy as np

from hazma.positron_spectra import charged_pion as pspec_charged_pion
from hazma.positron_spectra import muon as pspec_muon
from hazma.scalar_mediator.scalar_mediator_positron_spec import dnde_decay_s


class ScalarMediatorPositronSpectra:
    def dnde_pos_pipi(self, positron_energies, cme):
        """
        Positron/electron spectrum from dark matter annihilating into charged
        pions.

        Parameters
        ----------
        positron_energies: float or np.array
            Energies of the positrons/electrons
        cme: float
            Center of mass energy

        Returns
        -------
        dnde: float or np.array
            Positron spectrum evaluated at the `positron_energies`.
        """
        return pspec_charged_pion(positron_energies, cme / 2.0)

    def dnde_pos_mumu(self, positron_energies, cme):
        """
        Positron/electron spectrum from dark matter annihilating into muons

        Parameters
        ----------
        positron_energies: float or np.array
            Energies of the positrons/electrons
        cme: float
            Center of mass energy

        Returns
        -------
        dnde: float or np.array
            Positron spectrum evaluated at the `positron_energies`.
        """
        return pspec_muon(positron_energies, cme / 2.0)

    def dnde_pos_ss(self, positron_energies, cme, fs="total"):
        """
        Positron/electron spectrum from dark matter annihilating into muons

        Parameters
        ----------
        positron_energies: float or np.array
            Energies of the positrons/electrons
        cme: float
            Center of mass energy
        fs: str {'total'}
            String for which final states to consider when computing scalar
            mediator decay spectrum. Options are 'total', 'pi pi' or 'mu mu'.

        Returns
        -------
        dnde: float or np.array
            Positron spectrum evaluated at the `positron_energies`.
        """
        scalar_energy = cme / 2.0
        pws = self.partial_widths()

        if pws["total"] != 0:
            pw_array = np.array([pws["e e"], pws["mu mu"], pws["pi pi"]], dtype=float)
            pw_array /= pws["total"]

            # Factor of 2 since S is self-conjugate
            return 2.0 * dnde_decay_s(
                positron_energies, scalar_energy, self.ms, pw_array, fs
            )
        else:
            return np.zeros_like(positron_energies)

    def positron_spectra(self, positron_energies, cme):
        """
        Positron/electron spectrum from dark matter annihilating into
        charged pions, muons or scalar mediators.

        Parameters
        ----------
        positron_energies: float or np.array
            Energies of the positrons/electrons
        cme: float
            Center of mass energy

        Returns
        -------
        dnde: dict
            Dictionary of the positron spectrum from dark matter annihilating
            into charged pions, muons or scalar mediators. Keys are: 'total',
            'mu mu', 'pi pi' or 's s'.
        """
        bfs = self.annihilation_branching_fractions(cme)

        def spec_helper(bf, spec_fn):
            if bf != 0:
                return bf * spec_fn(positron_energies, cme)
            else:
                return np.zeros_like(positron_energies)

        muon_spec = spec_helper(bfs["mu mu"], self.dnde_pos_mumu)
        pipi_spec = spec_helper(bfs["pi pi"], self.dnde_pos_pipi)
        ss_spec = spec_helper(bfs["s s"], self.dnde_pos_ss)

        total = pipi_spec + muon_spec + ss_spec

        return {"total": total, "mu mu": muon_spec, "pi pi": pipi_spec, "s s": ss_spec}

    def positron_lines(self, cme):
        """
        Positron/electron lines from dark matter annihilating into
        electrons/positrons.

        Parameters
        ----------
        cme: float
            Center of mass energy

        Returns
        -------
        dnde: dict
            Dictionary of dictionaries. Each sub-dictionary contains the
            location of the line and the branching fraction for the
            corresponding dark matter annihilation process.
        """
        bf = self.annihilation_branching_fractions(cme)["e e"]

        return {"e e": {"energy": cme / 2.0, "bf": bf}}
