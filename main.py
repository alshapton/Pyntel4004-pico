# Import system libraries
import os
import sys


# Import Pyntel4004 functionality
from executer.execute import execute
from executer.exe_supporting import retrieve
from hardware.processor import Processor
from shared.shared import print_messages

'''
package = "Pyntel4004-cli"
core_name = 'Pyntel4004'
cini = core_name + ' core is not installed - use \n\n' + \
        '       pip install ' + core_name + '\n'
module = os.path.basename(sys.argv[0])
__Pyntel4004_version__ = 'Installed'

def is_core_installed(package_name: str):
    """
    Check to see if the Pyntel4004 core is installed

    Parameters
    ----------
    package_name: str, mandatory
        Name of the Pyntel4004 core package

    Returns
    -------
    True    - if the core package is installed
    False   - if not

    Raises
    ------
    N/A

    Notes
    -----
    N/A

    """
    import importlib.util
    spec = importlib.util.find_spec(package_name)
    if spec is None:
        return False
    else:
        return True
'''

def exe(object_code):
    """Execute the object file"""
    # Ensure that the core Pyntel4004 is installed
    # Exit if not
    #if not is_core_installed(core_name):
    #    raise click.ClickException(cini)
    # Create new instance of a processor
    chip = Processor()
    result = retrieve(object_code, chip, True)
    memory_space = result[0]
    operations = {'ldm': chip.ldm,
                  'fim': chip.fim,
                  'src': chip.src,
                  'nop': chip.nop,
                  }
    execute(chip, memory_space, 0, False, False, operations)

object_code='example2.bin'
exe(object_code)