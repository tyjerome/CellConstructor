# CellConstructor

Welcome to the CellConstructor python package!

## Requirements

To correnctly install and use the package, you need to have
1. python >= 2.7 and < 3
2. ASE : Atomic Simulation Environment (suggested but not mandatory)
3. numpy
4. scipy
5. A fortran compiler
6. Lapack

The fortran compiler is required to compile the fortran libraries 
from Quantum ESPRESSO.

Suggested, but not required, is the installation of ASE and spglib. 
The presence of a valid ASE installation will enable some more features, 
like the possibility to load structures by any ASE supported file format, 
or the possibility to export the structures into a valid ASE Atoms class.
This library is able to compute symmetries from the structure, 
and inside the symmetry module there is a convertor to let CellConstructure 
dealing with symmetries extracted with spglib. 
However, for a more carefull symmetry analisys, we suggest the use of external tools like ISOTROPY.
This package can generate ISOTROPY input files for more advanced symmetry detection.

Please, note that some fortran libraries are needed to be compiled, therefore the Python header files should be localized by the compiling process. 
This requires the python distutils and developing tools to be properly installed.
On ubuntu this can be achieved by running:
```bash
sudo apt-get install python-dev
```

If you are using anaconda or pip, it should be automatically installed.


## Installation

Once you make sure to have all the required packages installed on your system
and working, just type on the terminal

```bash
python setup.py install
```

while you are located in the same directory as the setup.py script is.

This program is also distributed upon PyPI. You can install it by typing

```bash
pip install CellConstructor
```
In this way you will not install the last developing version.

If the compilation of the modules fails and you are using
an anaconda module on a 64bit machine, you have to install the conda gcc version.
You can do this by typing (on Linux):

```bash
conda install gxx_linux-64
```
or (on MacOS):
```bash
conda install clangxx_osx-64
```


NOTE:
If you want to install the package into a system python distribution, the
installation commands should be executed as a superuser. 
Otherwise, append the --user flag to either the setup.py or the pip installation. 
In this way no administrator privilages is required, but the installation will be effective only for the current user.
Note that some python distribution, like anaconda, does not need the superuser, as they have an installation path inside the HOME directory.

## GO!

To test if the installation runned properly, run the examples reported 
in the test directory. The python code in these tests should be
almost self explaining and introduce you to the potentiality of this library.

Please, note that all the functions of the library have a proper numpy style
docstring.

You can test the installation using the script:
```bash
cellconstructor_test.py
```

