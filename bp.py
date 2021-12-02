#!/usr/bin/python3-64 -X utf8


import argparse
from datetime import datetime
import os
import random
import sys
import time


__author__ = 'Brandon Wells <wellsb.prog@gmail.com>'
__license__ = 'MIT'
__origin_date__ = '2021-11-25'
__prog__ = 'bp.py'
__purpose__ = 'colorization module "Better Print" (bp)'
__version__ = '0.1.2'
__version_date__ = '2021-11-29'
__version_info__ = tuple(int(i) for i in __version__.split('.') if i.isdigit())
ver = f'{__prog__} v{__version__} ({__version_date__})'
print_tracker = 0


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Ct:
    """A class of constants used to color strings for console printing. Using
    the full Unicode escape sequence to allow both 8 and 24 bit color here."""
    # ~~~ #     all 3-bit/4-bit 8 bit (256) unicode, plus some grey 256
    A = '\u001b[0m'                         # reset (all attributes off)
    BLACK = '\u001b[38;5;0m'                # black
    RED = '\u001b[38;5;1m'                  # red
    GREEN = '\u001b[38;5;2m'                # green
    YELLOW = '\u001b[38;5;3m'               # yellow
    BLUE = '\u001b[38;5;4m'                 # green
    MAGENTA = '\u001b[38;5;5m'              # yellow
    CYAN = '\u001b[38;5;6m'                 # green
    WHITE = '\u001b[38;5;7m'                # yellow
    BBLACK = '\u001b[38;5;8m'               # bright black (grey)
    BRED = '\u001b[38;5;9m'                 # bright red
    BGREEN = '\u001b[38;5;10m'              # bright green
    BYELLOW = '\u001b[38;5;11m'             # bright yellow
    BBLUE = '\u001b[38;5;12m'               # bright blue
    BMAGENTA = '\u001b[38;5;13m'            # bright magenta
    BCYAN = '\u001b[38;5;14m'               # bright cyan
    BWHITE = '\u001b[38;5;15m'              # bright white
    GREY1 = '\u001b[38;5;255m'              # grey level 1
    GREY2 = '\u001b[38;5;253m'              # grey level 2
    GREY3 = '\u001b[38;5;251m'              # grey level 3
    GREY4 = '\u001b[38;5;249m'              # grey level 4
    GREY5 = '\u001b[38;5;247m'              # grey level 5
    GREY6 = '\u001b[38;5;245m'              # grey level 6
    GREY7 = '\u001b[38;5;243m'              # grey level 7
    GREY8 = '\u001b[38;5;241m'              # grey level 8
    GREY9 = '\u001b[38;5;239m'              # grey level 9
    GREY10 = '\u001b[38;5;237m'             # grey level 10
    GREY11 = '\u001b[38;5;235m'             # grey level 11
    GREY12 = '\u001b[38;5;233m'             # grey level 12
    # ~~~ #     some 24-bit unicode colors
    ORANGE = '\u001b[38;2;233;133;33m'      # orange
    BROWN = '\u001b[38;2;118;65;12m'        # brown


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def get_args():
    """Get CLI arguments from argparse.

    Returns:
        - class 'argparse.ArgumentParser': Command Line Arguments
    """
    # Use argparse to capture cli parameters
    parser = argparse.ArgumentParser(
        prog=__prog__,
        description=f'{Ct.BBLUE}{ver}: {__purpose__}{Ct.A}',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog=f'{Ct.RED}This program has no warranty. Please use with '
               f'caution.{Ct.A}',
        add_help=True)
    parser.add_argument('--log',
                        help='add timestamp logging to output',
                        action='store_true')
    parser.add_argument('--log-file',
                        help='file to save output',
                        metavar=f'{Ct.GREEN}<filename>{Ct.A}',
                        type=str)
    parser.add_argument('--error-log-file',
                        help='file to save output',
                        metavar=f'{Ct.GREEN}<filename>{Ct.A}',
                        type=str)
    parser.add_argument('--no-color',
                        help='don\'t colorize output',
                        action='store_true')
    parser.add_argument('-v',
                        '--verbose',
                        help='3 lvl incremental verbosity (-v, -vv, or -vvv)',
                        action='count',
                        default=0)
    parser.add_argument('--version',
                        help='print program version and exit',
                        action='version',
                        version=f'{ver}')

    return parser.parse_args()


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def validate_args():
    """Validate the cli args before executing main()."""
    def file_check(f_to_c):
        """Check log file or error log file if it exists and if it should be
        appended.

        Args:
            - f_to_c (string): the file to check
        """
        bp([f'Starting validate_args()->file_check({f_to_c}).',
            Ct.BMAGENTA], fil=0, veb=3)
        if os.path.isfile(f_to_c):
            check_append = input(f'{Ct.YELLOW}({f_to_c}) exists. Append? '
                                 f'[Y/N]: {Ct.A}')
            # abort on no
            if check_append[:1].lower() == 'n':
                bp(['Exiting', Ct.YELLOW], fil=0, erl=1)
                sys.exit(1)
            # call file_check again if anything other than y (since n checked)
            elif check_append[:1].lower() != 'y':
                bp([f'{check_append} is not "Y" or "N".', Ct.YELLOW], erl=1,
                   fil=0)
                file_check(f_to_c)
    bp(['Checking if log_file exists and ask if it should be appended.',
        Ct.BMAGENTA], fil=0, veb=2)
    if args.log_file:
        file_check(args.log_file)
    bp(['Checking error_log_file exists and ask if it should be appended.',
        Ct.BMAGENTA], fil=0, veb=2)
    if args.error_log_file:
        file_check(args.error_log_file)
    if args.verbose > 3:
        bp([f'Verbosity level {args.verbose} requested. Using the maximum of '
            '3.', Ct.YELLOW], erl=1)

    return


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def bp(txt: list, erl=0, fil=1, fls=0, inl=0, log=1, num=1, veb=0):
    """Better Print: send output commands here instead of using print command.
    Txt must be sent in the form of pairs of strings in a list. The even
    strings ("0", "2", "4", etc.) contain the output text while the odd strings
    ("1", "3", "5", etc.) contain the color companion that defines the color
    to be applied to the preceding string. There are pre-defined defaults that
    can be overwritten but not required.

    Example:
        - bp(['Hello', Ct.RED, 'world', Ct.A, '!', Ct.GREEN], veb=2)
            - This prints "Hello world!" with the Hello in red, world in
            terminal default color, and the bang in green. This will also only
            print if args.verbose is set to "2" via "-vv".

    Args:
        - txt (list): (required) must be pairs with the even entries a string
                      and odd sections the Ct.color to apply to that string.
        - erl  (int): (optional) 0 = none (default), 1 = WARNING, 2 = ERROR:
                      auto pre-pends ERROR: or WARNING:, colors line Red, and
                      allows routing of only these to error log if requested.
        - fil  (int): (optional) 0 = off, 1 (default)= on: setting zero skips
                      file output even if args requested.
        - fls  (int): (optional) 0 = off (default), 1 = on: flush the text
                      instead of holding on to it. Usually required for in-
                      line text (inl=1) to force output without an end-of-line.
        - inl  (int): (optional) 0 = off (default); 1 = on: text written in-
                      line with no end-of-line character. Make sure to invoke
                      eol with a final bp before moving on.
        - log  (int): (optional) 0 = off; 1 = on (default): allow pre-pend of
                      each print statement with the date. Can be turned off for
                      things like progress bars and % updates.
        - num  (int): (optional) 0 = off; 1 = on (default): print blue numbers
        - veb  (int): (optional) 0-3: value is used to print only as much as
                      requested.

    Return:
        - None
    """
    # ~~~ #     variables section
    # this keeps track of the number of non-inline print statements
    global print_tracker
    # local variables - txt_tmp gets colored, file_tmp does not
    txt_out, file_out = '', ''
    # this provides an empty dict of args in case no args
    args_dict = vars(args) if 'args' in globals() else {}

    # ~~~ #     validate verbosity
    # if verbose not implemented, print everything
    if 'verbose' in args_dict:
        # if error logging set, veb ignored and will be printed
        if args.verbose < veb and erl == 0:
            return      # skip anything with higher verbosity than requested

    # ~~~ #     validate txt list - verify it is in pairs
    txt_l = len(txt)
    if txt_l % 2 != 0:
        raise Exception(f'{Ct.RED}"Better Print" function (bp) -> "txt: (list)'
                        f'": must be in pairs (txt length = {txt_l}){Ct.A}')

    # ~~~ #     veb section - prepend INFO-L(x) to each output with verbose
    if veb > 0 and erl == 0 and log == 0:
        txt_out = f'INFO-L{veb}: '
        file_out = f'INFO-L{veb}: '

    # ~~~ #     error section - pre-pend Error or Warning
    # this overwrites veb section as errors and warnings take precedence
    if erl == 1:
        txt_out = f'{Ct.YELLOW}WARNING: {Ct.A}'
        file_out = 'WARNING: '
    elif erl == 2:
        txt_out = f'{Ct.RED}ERROR: {Ct.A}'
        file_out = 'ERROR: '

    # ~~~ #     colorize and assemble section
    # need enumerate to identify even entries that contain strings
    for idx, val in enumerate(txt):
        if idx % 2 == 0:
            if type(val) != str:
                raise Exception(f'{Ct.RED}"Better Print" function (bp) -> "txt'
                                f' list even entries must be str. txt type = '
                                f'{type(val)}{Ct.A}')
            ent = ''
            j = txt[idx + 1]
            # colorize numbers and reset to default
            if num == 1 and j == Ct.A:
                for i in val[:]:
                    ent += f'{Ct.BBLUE}{i}{Ct.A}' if i.isdigit() else i
            # colorize numbers and reset to requested color for that part
            elif num == 1:
                for i in val[:]:
                    ent += f'{Ct.BBLUE}{i}{j}' if i.isdigit() else i
            # don't colorize numbers
            else:
                ent = val
            # now wrap the color numbered string with the requested color
            txt_out += f'{j}{ent}{Ct.A}'
            # file output is the original value with no console coloration
            file_out += val[:]

    # ~~~ #     log section - prepend time to each output
    # skip if log is not implemented in args
    if 'log' in args_dict:
        if args.log and log == 1:
            dt_now = datetime.now().strftime('[%H:%M:%S]')
            txt_out = f'{dt_now}-{print_tracker}-{txt_out}'
            file_out = f'{dt_now}-{print_tracker}-{file_out}'

    # ~~~ #     no color check
    # skip if no_color not implemented in args
    if 'no_color' in args_dict:
        if args.no_color:
            txt_out = file_out[:]

    # ~~~ #     console output section
    if inl == 0:    # default with new line appended
        sys.stdout.write(f'{txt_out}\n')
        print_tracker += 1
    elif inl == 1 and fls == 0:     # in-line with no flush
        sys.stdout.write(txt_out)
    elif inl == 1 and fls == 1:     # in-line with flush
        sys.stdout.write(txt_out)
        sys.stdout.flush()

    # ~~~ #     file output section
    # skip if file log output not implemented in args
    if 'log_file' in args_dict or 'error_log_file' in args_dict:
        try:
            if args.log_file and fil == 1:
                with open(args.log_file, 'a') as f:
                    f.write(file_out + '\n')
            if args.error_log_file and erl > 0 and fil == 1:
                with open(args.error_log_file, 'a') as f:
                    f.write(file_out + '\n')
        except OSError as e:
            bp([f'exception caught trying to write to {args.log_file} or '
                f'{args.error_log_file}\n\t{e}', Ct.RED], erl=1, fil=0)

    return


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def example_multi_bar(bar_count: int):
    """A multi-bar output example adapted from something found online. Used to
    demonstrate how to use bp to navigate multiple lines with overwrite.

    Args:
        bar_count (int): number of progress bars to display
    """
    bp([f'Create example_multi_bar using: {bar_count}:', Ct.BMAGENTA], veb=3)
    prog_counter = [0] * bar_count
    bp([f'Created prog_counter as: {prog_counter}', Ct.BMAGENTA],
       veb=3)
    bp(["\n" * bar_count, Ct.BLACK], log=0, inl=1, num=0, fil=0)
    # if any bar is less than 100, continue
    while any(x < 100 for x in prog_counter):
        time.sleep(0.01)
        # pull out any progress that are under 100
        unfinished = [(i, v) for (i, v) in enumerate(prog_counter) if v < 100]
        # only care about index; this allows index to not be a tuple
        index, _ = random.choice(unfinished)
        # increment counter
        prog_counter[index] += 1
        # go all the way left 1000 spaces using 'D'
        bp(['\u001b[1000D', Ct.BLACK], log=0, inl=1, num=0, fil=0)
        # go to the level of the index with 'A' going up
        bp([f'\u001b[{str(bar_count)}A', Ct.BLACK], log=0, inl=1, num=0, fil=0)

        for progress in prog_counter:
            width = progress / 2
            bp(['[', Ct.A, '━' * int(width), Ct.BLACK, '─' * (50 -
               int(width)), Ct.GREY1, ']', Ct.A], inl=0, log=0, num=0, fil=0)
    bp(['Finished with example_multi_bar', Ct.BMAGENTA], veb=3)

    return


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def example_progress_bar(symbol='━', empty='─', symbol_color=Ct.A,
                         empty_color=Ct.GREY1, bracket_color=Ct.A,
                         prog_width=50):
    """Show how to make a progress bar using bp.

    Args:
        - symbol (str, optional): the complete symbol. Defaults to '━'.
        - empty (str, optional): the empty symbol. Defaults to '─'.
        - symbol_color (str, optional): 'symbol' color. Defaults to Ct.A.
        - empty_color (str, optional): 'empty' color. Defaults to Ct.GREY1.
        - bracket_color (str, optional): 'bracket' color. Defaults to Ct.A.
        - prog_width (int, optional): progress bar width. Defaults to 50.
    """
    bp(['Entering example_progress_bar', Ct.BMAGENTA], veb=3)
    bp([f'Creating example_progress_bar using: {symbol} | {empty} | '
        f'{symbol_color} | {empty_color} | {bracket_color} | {prog_width}',
        Ct.BMAGENTA], veb=1)
    bp(['[', bracket_color, f'{empty * prog_width}', empty_color, ']',
        bracket_color], inl=1, fls=1, log=0, fil=0)
    bp(["\b" * (prog_width + 1), Ct.A], inl=1, log=0, fil=0)
    for i in range(prog_width):
        time.sleep(0.05)
        bp([symbol, symbol_color], inl=1, fls=1, log=0, fil=0)
    bp(['', Ct.A], inl=0, log=0, fil=0)
    bp(['Finished with example_progress_bar.', Ct.BMAGENTA], veb=2)

    return


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def example_percent_complete(loops=50, loop_color=Ct.BLACK, txt='Progress...'):
    """[summary]

    Args:
        - loops (int, optional): loops to completion. Defaults to 50.
        - loop_color (string, optional): color output. Defaults to Ct.BLACK.
        - txt (str, optional): text after percent. Defaults to 'Progress...'.
    """
    for_loop = 0
    for _ in range(loops):
        time.sleep(0.05)
        for_loop += 1
        bp([f'\u001b[1000D{(for_loop / loops) * 100:.0f}% | {txt}',
            loop_color], inl=1, fls=1, log=0, num=0, fil=0)
    bp(['', Ct.A], log=0, fil=0)
    bp(['Finished with example_percent_complete.', Ct.BMAGENTA], veb=2)

    return


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def examples():
    """Call various examples using bp to show capabilities and ways to make it
    work for you."""
    bp(['Entering examples().', Ct.BMAGENTA], veb=3)
    bp(['This text shows list position 0 with position 1 of default color,',
        Ct.A, ' and this text shows list position 2 with position 3 of Red.'
        ' This uses default settings.',
        Ct.RED])
    bp(['Calling example_progress_bar(symbol="ꟷ", empty="ꟷ", symbol_color='
        'Ct.GREEN).', Ct.BMAGENTA], veb=2)
    example_progress_bar(symbol="ꟷ", empty="ꟷ", symbol_color=Ct.GREEN)
    bp(['Returning from example_progress_bar(symbol="ꟷ", empty="ꟷ", '
        'symbol_color=Ct.GREEN).', Ct.BMAGENTA], veb=3)
    bp(['The next 3 print statements show verbosity levels 1-3 in order. Will'
        ' only be visible if that verbosity level requested', Ct.ORANGE])
    bp(['Verbosity level 1', Ct.BMAGENTA], veb=1)
    bp(['Verbosity level 2', Ct.BMAGENTA], veb=2)
    bp(['Verbosity level 3', Ct.BMAGENTA], veb=3)
    bp(['Calling example_multi_bar(4).', Ct.BMAGENTA], veb=2)
    example_multi_bar(4)
    bp(['Returning from example_multi_bar(4).', Ct.BMAGENTA], veb=3)
    bp(['Calling example_progress_bar(symbol="═", empty="═", symbol_color'
        '=Ct.BROWN, prog_width=66) next', Ct.BMAGENTA], veb=2)
    example_progress_bar(symbol="═", empty="═", symbol_color=Ct.BROWN,
                         prog_width=66)
    bp(['Returning from  example_progress_bar(symbol="═", empty="═", '
        'symbol_color=Ct.BROWN, prog_width=66) next', Ct.BMAGENTA], veb=3)
    bp(['The next line is an empty line', Ct.A])
    bp(['', Ct.A])
    bp(['This shows numbers with default color: 19 00 ', Ct.A, 'and this with'
        ' text and numbers in green: 19 00 -67-', Ct.GREEN], num=0)
    bp(['Calling example_progress_bar().', Ct.BMAGENTA], veb=2)
    example_progress_bar()
    bp(['Returning from example_progress_bar().', Ct.BMAGENTA], veb=3)
    bp(['The next 3 lines demonstrates error handling with the text within '
       'the "" the only part typed. The rest is added by "bp" using "erl=2".',
        Ct.A])
    bp(['"This is error #423 with verbosity set to 1. This should show even'
        f' without verbosity at runtime (args.verbose={args.verbose}) because '
        'erl overwrites veb', Ct.RED], veb=1, erl=2)
    bp(['"This is error #4244 with no number color"', Ct.RED], num=0, erl=2)
    bp(['"This is error 55, with default color"', Ct.A], erl=2)
    bp(['Calling example_progress_bar(symbol="∞", empty="∞", symbol_color='
        'Ct.BLACK, prog_width=47) next', Ct.BMAGENTA], veb=2)
    example_progress_bar(symbol="∞", empty="∞", symbol_color=Ct.BLACK,
                         prog_width=47)
    bp(['Returning from example_progress_bar(symbol="∞", empty="∞", '
        'symbol_color=Ct.BLACK, prog_width=47) next', Ct.BMAGENTA], veb=3)
    bp(['This is Warning #17171 in yellow using "erl=1".', Ct.YELLOW], erl=1)
    bp(['This is warning #15 with no number color', Ct.YELLOW], num=0, erl=1)
    bp(['Calling example_percent_complete(loops=100).', Ct.BMAGENTA], veb=2)
    example_percent_complete(loops=100)
    bp(['Returning from example_percent_complete(loops=100).', Ct.BMAGENTA],
       veb=3)
    bp(['This next step will fail. It is commented out. Uncomment individually'
        ' to view the failures.', Ct.BMAGENTA], veb=1)
    # bp(['Raise exception with only 3 entries.', Ct.Z, 'This causes error'])
    # bp([example_percent_complete, Ct.BMAGENTA])
    bp(['Finished with "examples", in Yellow.', Ct.YELLOW], veb=2)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def main():

    bp(['Entered main().', Ct.BMAGENTA], veb=3)
    bp(['Print args in 2 different forms:', Ct.BMAGENTA], veb=1)
    bp([f'Args from argparse in dict form using vars(args): {vars(args)}',
        Ct.A])
    bp(['CLI Args split: ', Ct.A], inl=1)
    for k, v in vars(args).items():
        bp([f'  {k}: {v}  |', Ct.A], inl=1, log=0)
    bp(['', Ct.A], log=0)
    bp(['Calling examples().', Ct.BMAGENTA], veb=2)
    examples()
    bp(['Returning from examples().', Ct.BMAGENTA], veb=3)
    bp(['End of main().', Ct.BMAGENTA], veb=1)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if __name__ == '__main__':

    bp([f'{ver}\n', Ct.BBLUE])
    bp(['Print before args showing args bypass. Since no args verbosity '
        'specified, the veb=2 applies so "INFO-L2" is pre-pended. This will '
        'not go to any file output since no file output request has yet been '
        'processed.', Ct.BMAGENTA], veb=2)
    args = get_args()
    bp(['Retrieved args from get_args().', Ct.BMAGENTA], veb=3)
    bp(['Calling validate_args():', Ct.BMAGENTA], veb=2)
    validate_args()
    bp(['Returned from validate_args().', Ct.BMAGENTA], veb=3)
    bp(['Calling main():', Ct.BMAGENTA], veb=2)
    main()
