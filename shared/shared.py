
"""Shared operations (between assembly, disassembly and execution."""

# Import i4004 processor
from hardware.processor import Processor  # noqa
from hardware.suboperations.utility import zfl  # noqa


def coredump(chip: Processor, filename: str) -> bool:
    """
    Take the memory and write to a given filename.

    Parameters
    ----------
    chip : Processor
        The chip targetted for the coredump

    filename: str, mandatory
        The filename to write to

    Returns
    -------
    True

    Raises
    ------
    N/A

    Notes
    -----
    N/A

    """

    # Import platform-specific code
    from platforms.platforms import get_current_datetime  # noqa

    errordate = 'Date/Time:' + get_current_datetime() + '\n\n'
    tabs = '\t\t\t'
    cr = '\n'
    with open(filename + '.core', "w") as of:
        of.write('\n\n' + errordate)
        of.write('Processor Characteristics:\n\n')
        of.write('MAX_4_BITS :           ' + str(chip.MAX_4_BITS) + tabs)
        of.write('PAGE_SIZE :            ' + str(chip.PAGE_SIZE) + cr)
        of.write('STACK_SIZE :           ' + str(chip.STACK_SIZE) + tabs)
        of.write('MSB :                  ' + str(chip.MSB) + cr)

        of.write('MEMORY_SIZE_RAM :      ' + str(chip.MEMORY_SIZE_RAM) + tabs)
        of.write('NO_REGISTERS :         ' + str(chip.NO_REGISTERS) + cr)
        of.write('MEMORY_SIZE_ROM :      ' + str(chip.MEMORY_SIZE_ROM) + tabs)
        of.write('NO_ROM_PORTS :         ' + str(chip.NO_ROM_PORTS) + cr)
        of.write('MEMORY_SIZE_PRAM :     ' + str(chip.MEMORY_SIZE_PRAM) + tabs)
        of.write('NO_CHIPS_PER_BANK :    ' + str(chip.NO_CHIPS_PER_BANK) + cr)
        of.write('RAM_BANK_SIZE :        ' + str(chip.RAM_BANK_SIZE) + tabs)
        of.write('RAM_CHIP_SIZE :        ' + str(chip.RAM_CHIP_SIZE) + cr)
        of.write('RAM_REGISTER_SIZE :    ' + str(chip.RAM_REGISTER_SIZE) + tabs)    # noqa
        of.write('NO_COMMAND_REGISTERS : ' + str(chip.NO_COMMAND_REGISTERS) + cr)   # noqa
        of.write('NO_STATUS_REGISTERS :  ' + str(chip.NO_STATUS_REGISTERS) + tabs)  # noqa
        of.write('NO_STATUS_CHARACTERS : ' + str(chip.NO_STATUS_CHARACTERS) + cr)   # noqa
        of.write('\n\nProcessor Status:\n\n')
        of.write('PIN 10               : ' + str(chip.PIN_10_SIGNAL_TEST) + cr)
        of.write('Program Counter      : ' + str(chip.PROGRAM_COUNTER) + cr)
        stack = ''
        for i in chip.STACK:
            stack = stack + str(chip.STACK[i]) + ', '
        ln = len(stack)-2
        stack = stack[:ln]
        of.write('Stack/Pointer        : (' + stack + ') / ' +
                 str(chip.STACK_POINTER) + cr)
        of.write('ACBR                 : ' + str(chip.ACBR) + '\n')
        of.write('Carry                : ' + str(chip.CARRY) + '\n')
        acc = chip.read_accumulator()
        of.write('Accumulator          : ' + str(acc) + '\n')

        of.write('DRAM Bank            : ' + str(chip.CURRENT_DRAM_BANK) + cr)
        of.write('RAM Bank             : ' + str(chip.CURRENT_RAM_BANK) + cr)
        of.write('WPM Counter          : ' + str(chip.WPM_COUNTER) + cr)
        of.write('\n\nRegisters:\n\n')
        r = 0
        for i in chip.REGISTERS:
            if r < 10:
                spaces = ' '
            else:
                spaces = ''
            of.write('[' + spaces + str(r) + ']\t')
            r = r + 1
        of.write('\n')
        spaces = '  '
        for i in chip.REGISTERS:
            of.write(spaces + str(i) + '\t\t')

        return True


def print_messages(quiet: bool, msgtype: str, chip: Processor,
                   param0) -> None:
    if not quiet:
        if msgtype == 'EXEC':
            print()
            print('EXECUTING PROGRAM: ')
            print()
        if msgtype == 'BLANK':
            print()
        if msgtype == 'ACC':
            acc = chip.read_accumulator()
            print('Accumulator : ' + str(acc) + '  (0b ' +
                  str(Processor.decimal_to_binary(4, acc)) + ')')
        if msgtype == 'CARRY':
            print('Carry       :', chip.read_carry())
        if msgtype == 'ASM':
            print('Address  Label   Address        Assembled            ' +
                  '          Line     Op/Operand')
            print(' (Dec)            (Bin)           (Bin)          (Dec)')
            print('                            Word 1     Word 2')
        if msgtype == 'PROG':
            print()
            print()
            print('Program Code:', param0)
            print()
        if msgtype == 'LABELS':
            print()
            print('Labels:')
            print('Address   Label')
            for _i in range(len(param0)):  # noqa
                print('{:>5}     {}'.format(param0[_i]['address'], param0[_i]['label']))  # noqa


def determine_filetype(inputfile: str) -> str:
    """
    Determine the filetype of a specific input file.
    In the context of reloading a previously assembled file for
    execution or disassembly.
    Parameters
    ----------
    inputfile: str, mandatory
        The filename to examine
    Returns
    -------
    filetype: str
        OBJ if an object file complete with metadata
        BIN if a binary assembled file.
    Raises
    ------
    N/A
    Notes
    -----
    N/A
    """
    file = open(inputfile, "rb")
    bites = file.read(12)[2:9]
    if bites == b'program':
        filetype = 'OBJ'
    else:
        filetype = 'BIN'
    return filetype


def do_error(message: str):
    """
    Print an assembly/runtime error message

    Parameters
    ----------
    message: str, mandatory
        The error message to display

    Returns
    -------
    N/A

    Raises
    ------
    N/A

    Notes
    -----
    N/A

    """
    print()
    print(message)
    return True


def get_opcodeinfo(self: Processor, ls: str, mnemonic: str) -> dict:
    """
    Given a mnemonic retrieve details about the it from the opcode table.

    Parameters
    ----------
    self : Processor, mandatory
        The instance of the processor containing the registers, accumulator etc

    ls: str, mandatory
        's' or 'S' indicating whether the mnemonic contains the full mnemonic
        or not - e.g.    nop   as a mnemonic would be found if ls = 'S' or 's'
                         nop() as a mnemonic would be found if ls != 'S' or 's'

    mnemonic: str, mandatory
        The mnemonic to locate

    Returns
    -------
    opcodeinfo
        The information about the mnemonic required in JSON form,
        or

           {"opcode": -1, "mnemonic": "N/A"}

        if the mnemonic is not found.

    Raises
    ------
    N/A

    Notes
    -----
    N/A

    """
    if ls.upper() == 'S':
        opcodeinfo = next((item for item in self.INSTRUCTIONS
                          if str(item["mnemonic"][:3]) == mnemonic),
                          {"opcode": -1, "mnemonic": "N/A"})
    else:
        opcodeinfo = next((item for item in self.INSTRUCTIONS
                          if str(item["mnemonic"]) == mnemonic),
                          {"opcode": -1, "mnemonic": "N/A"})
    return opcodeinfo


def get_opcodeinfobyopcode(self: Processor, opcode: int) -> dict:
    """
    Given an opcode, retrieve details about it from the opcode table.

    Parameters
    ----------
    self : Processor, mandatory
        The instance of the processor containing the registers, accumulator etc

    opcode: int, mandatory
        The opcode to locate

    Returns
    -------
    opcodeinfo
        The information about the mnemonic required in JSON form,
        or

           {"opcode": -1, "mnemonic": "N/A"}

        if the mnemonic is not found.

    Raises
    ------
    N/A

    Notes
    -----
    N/A

    """
    # opcodeinfo = next((item for item in self.INSTRUCTIONS
    #                  if item['opcode'] == opcode),
    #                  {"opcode": -1, "mnemonic": "N/A"})
    opcodeinfo = {"opcode": -1, "mnemonic": "N/A"}
    for item in self.INSTRUCTIONS:
        if item['opcode'] == opcode:
            opcodeinfo = item
    return opcodeinfo


def retrieve_program(chip: Processor, location: str) -> list:
    """
    Retrieve the assembled program from the specified location.

    Parameters
    ----------
    chip : Processor, mandatory
        The instance of the processor containing the registers, accumulator etc

    location : str, mandatory
        The location to which the program should be loaded

    Returns
    -------
    loc: list
        The program from the location specified

    Raises
    ------
    N/A

    Notes
    -----
    N/A

    """
    if location == 'rom':
        loc = chip.ROM
    if location == 'ram':
        loc = chip.PRAM
    return loc


def translate_mnemonic(chip: Processor, _tps: list, exe: str,
                       opcode: str, task: str, words: int, quiet: bool) -> str:
    """
    Formulate the opcodes into mnemonics ready for execution.

    Parameters
    ----------
    chip : Processor, mandatory
        The instance of the processor containing the registers, accumulator etc

    _tps: list, mandatory
        List representing the memory of the i4004 into which the
        newly assembled instructions will be placed.

    exe: str, mandatory
        pre-formatted exe mnemonic ready for processing

    opcode: str, mandatory
        Opcode of the current instruction

    task: str, mandatory
        'D' for Disassembly
        'E' for Execution

    words: int, optional (supply 0)
        The number of words an instruction uses

    quiet: bool, mandatory
        Whether quiet mode is on

    Returns
    -------
    exe: str
        A correctly formed, ready-for execution mnemonic

    Raises
    ------
    N/A

    Notes
    -----
    N/A

    """
    custom_opcode = False
    cop = ''

    # Only mnemonic with 2 characters - fix
    if exe[:3] == 'ld ':
        exe = exe[:2] + exe[3:]

    # Ensure that the correct arguments are passed to the operations
    if exe[:3] == 'fim':
        value = str(_tps[chip.PROGRAM_COUNTER + 1])
        exe = exe.replace('p', '').replace('data8)', '') + value + ')'

    if exe[:3] == 'isz':
        # Remove opcode from 1st byte to get register
        first_byte = zfl(str(_tps[chip.PROGRAM_COUNTER] & 15), 4)
        exe = 'isz(' + str(int(first_byte, 2))
        exe = exe + ',' + str(_tps[chip.PROGRAM_COUNTER + 1]) + ')'

    if exe[:4] == 'jcn(':
        custom_opcode = True
        address = _tps[chip.PROGRAM_COUNTER + 1]
        conditions = zfl(str(bin(_tps[chip.PROGRAM_COUNTER])[2:], 8)[4:])
        b10address = str(address)
        cop = exe.replace('address8', b10address)
        exe = exe[:4] + str(int(conditions, 2)) + ',' + b10address + ')'

    if exe[:4] in ('jun(', 'jms('):
        custom_opcode = True
        # Remove opcode from 1st byte
        hvalue = zfl(bin(_tps[chip.PROGRAM_COUNTER] &
                     0xffff0000)[2:], 8)[:4]
        lvalue = zfl(bin(_tps[chip.PROGRAM_COUNTER + 1])[2:], 8)
        whole_value = str(int(hvalue + lvalue, 2))
        cop = exe.replace('address12', whole_value)
        exe = exe[:4] + whole_value + ')'

    if task == 'D':
        if exe[:3] == 'end':  # pseudo-opcode (directive "end" - stop program)
            opcode = ''
            custom_opcode = False
        if custom_opcode:
            custom_opcode = False
            exe = cop
            if not quiet:
                print('{:4}  {:>8}  {:<10}'.format(chip.PROGRAM_COUNTER, opcode, cop.replace('()', '')))  # noqa
        else:
            if not quiet:
                print('{:4}  {:>8}  {:<10}'.format(chip.PROGRAM_COUNTER, opcode, exe.replace('()', '')))  # noqa

        chip.PROGRAM_COUNTER = chip.PROGRAM_COUNTER + words

    if task == 'E':
        if custom_opcode:
            custom_opcode = False
            exe = cop
            if not quiet:
                print('  {:>7}  {:<10}'.format(opcode, cop.replace('()', '')))  # noqa
        else:
            if not quiet:
                print('  {:>7}  {:<10}'.format(opcode, exe.replace('()', '')))  # noqa

    return exe
