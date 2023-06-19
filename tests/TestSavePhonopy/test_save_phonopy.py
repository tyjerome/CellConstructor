import sys, os
import cellconstructor as CC
import cellconstructor.Phonons

import pytest
import numpy as np

def test_phonopy_input():

    # Go to the current directory
    total_path = os.path.dirname(os.path.abspath(__file__))
    os.chdir(total_path)

    dyn = CC.Phonons.Phonons() # Load the CaSiO3 dynamical matrices
    dyn.Phonons.save_phonopy()

    # Load the two Force Constants files and compare them
    # Use assert to check if the numbers are similar
    assert np.abs(numbar_1 - number_2) < 1e-5



if __name__ == "__main__":
    test_phonopy_input()
