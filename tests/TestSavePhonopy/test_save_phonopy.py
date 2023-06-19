import sys, os
import cellconstructor as CC
import cellconstructor.Phonons

import pytest
import numpy as np

def test_phonopy_input():

    # Go to the current directory
    total_path = os.path.dirname(os.path.abspath(__file__))
    os.chdir(total_path)

    dyn = CC.Phonons.Phonons()
    dyn.load_phonopy()
    dyn.CC.Phonons.save_phonopy
    dyn.save_qe("prova")


if __name__ == "__main__":
    test_phonopy_input()
