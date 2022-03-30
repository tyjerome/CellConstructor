import cellconstructor as CC
import cellconstructor.Structure
import cellconstructor.Methods

import subprocess

import ase, ase.io
import ase.calculators.calculator

import cellconstructor.Settings as Settings

import cellconstructor.Units
import copy

import numpy as np
import copy
import sys, os



class Calculator:
    def __init__(self):
        """
        CELLCONSTRUCTOR  CALCULATOR
        ===========================
        
        This is an alternative to ASE calculators, which often do not work.
        It is explicitely done for cellconstructor and python-sscha
        
        """

        self.label = "label"
        self.directory = None 
        self.command = None 
        self.results = {}
        self.structure = None  



def get_energy_forces(calculator, structure):
    """
    Accepts both an ase calculaotr and a calculator of CellConstructor
    """

    if isinstance(calculator, ase.calculators.calculator.Calculator):
        atm = structure.get_ase_atoms()
        atm.set_calculator(calculator)
        return atm.get_total_energy(), atm.get_forces()
    elif isinstance(calculator, Calculator):
        calculator.calculate(structure)
        return calculator.results["energy"], calculator.results["forces"]
    else:
        raise ValueError("Error, unknown calculator type")

def get_results(calculator, structure, get_stress = True):
    """
    Accepts both an ASE calculator and a Calculator from Cellconstructor
    and computes all the implemented properties (energy, forces and stress tensor).
    """

    results = {}
    if isinstance(calculator, ase.calculators.calculator.Calculator):
        atm = structure.get_ase_atoms()
        atm.set_calculator(calculator)
        results["energy"] = atm.get_total_energy()
        results["forces"] = atm.get_forces()
        if get_stress:
            results["stress"] = atm.get_stress(voigt = False)
    elif isinstance(calculator, Calculator):
        calculator.calculate(structure)
        results =  calculator.results
        if get_stress:
            results["stress"] = CC.Methods.transform_voigt(results["stress"], voigt_to_mat = True)
    else:
        raise ValueError("Error, unknown calculator type")

    return results


class FileIOCalculator(Calculator):
    def __init__(self):
        Calculator.__init__(self)
        self.structure = None
        self.output_file = "PREFIX.pwo"

    def write_input(self, structure):
        if self.directory is None:
            self.directory = os.path.abspath(".")

        if not os.path.isdir(self.directory):
            os.makedirs(self.directory)
        
        # This is not thread safe, as writing the input override the structure of the shared calculator object
        # Which is then overridden by the read_results
        #self.structure = structure.copy()

    def calculate(self, structure):
        self.write_input(structure)
        self.execute()
        self.read_results()

    def set_label(self, lbl):
        self.label = lbl

    def set_directory(self, directory):
        self.directory = directory
    
    def execute(self):
        #cmd = "cd {} && {} && cd ..".format(self.directory, self.command.replace("PREFIX", self.label))
        cmd = self.command.replace("PREFIX", os.path.join(os.path.abspath(self.directory),self.label))
        outputfname = self.output_file.replace("PREFIX", os.path.join(os.path.abspath(self.directory),self.label))


        new_env = {k: v for k, v in os.environ.items() if "MPI" not in k if "PMI" not in k}
        sys.stdout.flush()
        with open(os.path.join(self.directory, outputfname), "w") as foutput:
            proc = subprocess.Popen(cmd, shell = True, env = new_env, cwd = self.directory, stdout = foutput)
        sys.stdout.flush()
        errorcode = proc.wait()
        sys.stdout.flush()

        
        #os.system(cmd)

    def read_results(self):
        pass 


class Espresso(FileIOCalculator):
    def __init__(self,  input_data = {}, pseudopotentials = {}, masses = None, command = "pw.x -i PREFIX.pwi", kpts = (1,1,1), koffset = (0,0,0)):
        """
        ESPRESSO CALCULATOR
        ===================

        parameters
        ----------
            data_input : dict
                Dictionary of the Quantum Espresso PW input namespace
            pseudopotentials : dict
                Dictionary of the file names of the pseudopotentials
            masses : dict
                Dictionary of the masses (in UMA) of the specified atomic species
        """
        FileIOCalculator.__init__(self)

        self.command = command
        self.kpts = kpts
        self.koffset = koffset
        self.input_data = copy.deepcopy(input_data)  # Copy to avoid double modification
        self.pseudopotentials = pseudopotentials
        self.output_file = "PREFIX.pwo"
        if masses is None:
            masses = {}
            for atm in pseudopotentials:
                masses[atm] = 1.000
        self.masses = masses

        assert len(list(self.pseudopotentials)) == len(list(self.masses)), "Error, pseudopotential and masses must match"


    def set_label(self, lbl, override_prefix = True, *args, **kwargs):
        FileIOCalculator.set_label(self, lbl, *args, **kwargs)

        # Enforce the override of the prefix
        if override_prefix:
            if "control" in self.input_data:
                self.input_data = copy.deepcopy(self.input_data)
                self.input_data["control"].update({"prefix" : lbl})

    def setup_from_ase(self, ase_calc):
        """
        Copy the parameters from the ASE calculator
        """

        for kwarg in ase_calc.parameters:
            self.__setattr__(kwarg, copy.deepcopy(ase_calc.parameters[kwarg]))

        self.set_label(ase_calc.label)

        #self.input_data = copy.deepcopy(ase_calc.parameters["input_data"])
        #self.kpts = ase_calc.parameters["kpts"]
        #self.koffset = ase_calc.parameters["koffset"]
        #self.pseudopotentials = copy.deepcopy(ase_calc.parameters["pseudopotentials"])

    def write_input(self, structure):
        FileIOCalculator.write_input(self, structure)

        typs = np.unique(structure.atoms)

        total_input = copy.deepcopy(self.input_data)
        total_input["system"].update({"nat" : structure.N_atoms, "ntyp" : len(typs), "ibrav" : 0})
        #total_input["control"].update({"outdir" : self.directory, "prefix" : self.label})
        if not "prefix" in  total_input["control"]:
            total_input["control"].update({"prefix" : self.label}) 

        scf_text = "".join(CC.Methods.write_namelist(total_input))

        print("TOTAL INPUT:")
        print(total_input)

        scf_text += """
ATOMIC_SPECIES
"""
        for atm in typs:
            scf_text += "{}  {}   {}\n".format(atm, self.masses[atm], self.pseudopotentials[atm])
        
        scf_text += """
K_POINTS automatic
{} {} {} {} {} {}
""".format(self.kpts[0], self.kpts[1], self.kpts[2],
            self.koffset[0], self.koffset[1], self.koffset[2])
        
        scf_text += structure.save_scf(None, get_text = True)

        filename = os.path.join(self.directory, self.label + ".pwi")

        with open(filename, "w") as fp:
            fp.write(scf_text)
        

    def read_results(self):
        FileIOCalculator.read_results(self)


        filename = os.path.join(self.directory, self.label + ".pwo")

        print('READING RESULTS FROM FILE ', filename)
        
        #   Settings.all_print("reading {}".format(filename))
        #atm = ase.io.read(filename)

        energy = 0
        read_forces = False
        counter = 0
        stress = np.zeros((3,3), dtype = np.double)

        read_stress = False
        got_stress = False
        read_structure = False
        read_coords = False
        alat = CC.Units.A_TO_BOHR
        if self.structure is None:
            read_structure = True
        else:
            forces = np.zeros_like(self.structure.coords)

        with open(filename, "r") as fp:
            for line in fp.readlines():
                line = line.strip()
                data = line.split()

                # Avoid white lines
                if not line:
                    continue

                if read_structure:
                    new_data = line.replace("=", " ").split()
                    if new_data[0] == "celldm(1)":
                        alat *= float(new_data[1])
                    
                    if "number of atoms/cell" in line:
                        nat = int(data[-1])
                        self.structure = CC.Structure.Structure(nat)
                        self.structure.has_unit_cell = True
                        self.structure.unit_cell = np.eye(3)
                        forces = np.zeros_like(self.structure.coords)

                    if data[0] == "a(1)":
                        self.structure.unit_cell[0,:] = [float(x) * alat for x in data[3:-1]]
                    if data[0] == "a(2)":
                        self.structure.unit_cell[1,:] = [float(x) * alat for x in data[3:-1]]
                    if data[0] == "a(3)":
                        self.structure.unit_cell[2,:] = [float(x) * alat for x in data[3:-1]]
                    
                    if "Cartesian axes" in line:
                        read_coords = True


                    if read_coords:
                        # Improve the split of the line to avoid merging numbers
                        data = line.replace("-", " -").replace("(", "( ").split()
                        if len(data) == 10:
                            i_atm = int(data[0]) - 1
                            self.structure.coords[i_atm, :] = [float(x) for x in data[6:9]]
                            self.structure.atoms[i_atm] = data[1]
                            if i_atm == self.structure.N_atoms - 1:
                                read_coords = False
                                read_structure = False
                            continue



                if line[0] == "!":
                    energy = float(data[4])

                if "Forces acting on atoms" in line:
                    read_forces = True
                    read_stress = False
                    continue
                
                if "total   stress" in line:
                    read_stress = True
                    read_forces = False
                    counter = 0
                    continue
                
                if read_forces and len(data) == 9:
                    if data[0] == "atom":
                        counter += 1

                        at_index = int(data[1]) - 1
                        forces[at_index, :] = [float(x) for x in data[6:]]
                    
                    if counter >= self.structure.N_atoms:
                        read_forces = False
                
                if read_stress and len(data) == 6:
                    stress[counter, :] = [float(x) for x in data[:3]]
                    counter += 1
                    if counter == 3:
                        got_stress = True
                        read_stress = False

                
        # Convert to match ASE conventions
        energy *= CC.Units.RY_TO_EV
        forces *= CC.Units.RY_TO_EV / CC.Units.BOHR_TO_ANGSTROM
        stress *= CC.Units.RY_PER_BOHR3_TO_EV_PER_A3
        stress = CC.Methods.transform_voigt(stress)  # To be consistent with ASE, use voigt notation
        
        print('READING RESULTS : energy = {}.'.format(energy))

        self.results = {"energy" : energy, "forces" : forces}
        if got_stress:
            # Use voit
            self.results.update({"stress" : - stress})
        

        

















