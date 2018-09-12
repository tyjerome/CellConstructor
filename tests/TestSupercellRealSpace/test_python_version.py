# -*- coding: utf-8 -*-

import numpy as np

import cellconstructor as CC
import cellconstructor.Phonons


SUPER_DYN = "../TestPhononSupercell/dynmat"
NQIRR = 8
SUPERCELL = (3, 3, 2)


dyn = CC.Phonons.Phonons(SUPER_DYN, NQIRR)


fc = dyn.GetRealSpaceFC(SUPERCELL)
fc_new = fc.copy()


print "Real space:"
print fc[:6, :6]

print "First one:"
print dyn.dynmats[0]


print "Distances"
super_structure =  dyn.structure.generate_supercell(SUPERCELL)
m =super_structure.get_masses_array()
nq = np.prod(SUPERCELL)
nat_sc = dyn.structure.N_atoms *nq

_m_ = np.zeros(3*nat_sc)
for i in range(nat_sc):
    _m_[3 * i : 3*i + 3] = m[i]
    
m_mat = np.outer(1 / np.sqrt(_m_), 1 / np.sqrt(_m_))

fc *= m_mat

w_tot = np.sqrt(np.abs(np.real(np.linalg.eigvals(fc))))
w_tot.sort()

w_old = np.zeros(len(w_tot))

for i in range(nq):
    w,p = dyn.DyagDinQ(i)
    w_old[ i * len(w) : (i+1) * len(w)] = w

w_old.sort()    
print "Freq:"
print "\n".join ( [" %.5f vs %.5f" % (w_tot[i] * CC.Phonons.RY_TO_CM, w_old[i] * CC.Phonons.RY_TO_CM) for i in range (len(w_tot))])


# Try to revert the code

dynmats_new = CC.Phonons.GetDynQFromFCSupercell(fc_new, np.array(dyn.q_tot), dyn.structure, super_structure)
print np.sqrt(np.sum( (dynmats_new[2,:,:] - dyn.dynmats[2])**2 ))

#print "\n".join ( ["RATIO: %.5f " % (w_tot[i] / w_old[i] ) for i in range (len(w_tot))])