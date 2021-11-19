#!/usr/bin/python3-64 -X utf8


import argparse
from collections import defaultdict as dd
from datetime import datetime
import hashlib
import os
import sys
import threading
import time


__author__ = 'Brandon Wells <wellsb.prog@gmail.com>'
__license__ = 'MIT'
__origin_date__ = '2021-11-18'
__prog__ = 'vcp.py'
__purpose__ = 'Copy contents of one folder to another with hash validation'
__version__ = '0.0.1'
__version_date__ = '2021-11-18'
__version_info__ = tuple(int(i) for i in __version__.split('.') if i.isdigit())
ver = f'{__prog__} v{__version__} ({__version_date__})'
# create list of available hash algorithms
h_list = [i for i in sorted(hashlib.algorithms_guaranteed)]


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Col:
    """A simple class for minimal command length to add colorized text print
    using ANSI ESC sequences."""

    R = '\033[31m'      # red
    G = '\033[32m'      # green
    Y = '\033[33m'      # yellow
    B = '\033[94m'      # bright blue
    RES = '\033[0m'     # reset to terminal defaults


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def con_output(output: str):
    """All console output goes through this function. Adds support for logging.

    Args:
        output (str): The data to print
    """
    print(f'{datetime.now()}\t|\t{output}') if args.verbose else print(output)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def log_output(output: str):
    """Append to the log file. Called any time logging is required. If errors
       are encountered, print to the console even if quite mode is requested.

    Args:
        output (str): The data to write to the log file
    """
    try:
        with open(args.log, 'a') as f:
            f.write(f'{datetime.now()}\t|\t{output}')
    except OSError as e:
        con_output(f'Error, cannot open log file to output error: {e}\nTried '
                   f'to write:\n{output}')


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def tree_walk():

    try:
        time_data, source_path = dd(int), dd(int)
    except OSError as e:
        e_var = (f'Error durring the tree walk of source: {args.source}\n'
                 f'Error:\n{e}')
        if args.log:
            log_output(e_var)
        con_output(e_var)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def main():
    pass


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if __name__ == '__main__':

    # Use argparse to capture cli parameters
    parser = argparse.ArgumentParser(
        prog=__prog__,
        description=f'{Col.B}{ver}: {__purpose__}{Col.RES}',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog='This program has no warranty. Please use with caution. ',
        add_help=True)
    parser.add_argument('-s',
                        '--source',
                        help='source path folder',
                        metavar=f'{Col.R}<path>{Col.RES}',
                        type=str)
    parser.add_argument('-t',
                        '--target',
                        help='target path folder',
                        metavar=f'{Col.R}<path>{Col.RES}',
                        type=str)
    parser.add_argument('--hash',
                        help='hash type to use',
                        metavar=f'{Col.Y}<hash>{Col.RES}',
                        type=str,
                        default='blake2b')
    parser.add_argument('-b',
                        '--blocksize',
                        help='specify number of 1K read blocks between 1 and '
                             '131072 (consumes more ram for min. speed gains)',
                        metavar=f'{Col.Y}<number>{Col.RES}',
                        type=int,
                        default=16)
    parser.add_argument('-l',
                        '--log',
                        help='log output to file specified',
                        metavar=f'{Col.Y}<path/filename>{Col.RES}',
                        type=str)
    parser.add_argument('-q',
                        '--quiet',
                        help='quiet mode surpresses all output except errors'
                             ' and final summary',
                        action='store_true')
    parser.add_argument('-t',
                        '--threads',
                        help='number of copy and validation threads',
                        metavar=f'{Col.Y}<num>{Col.RES}',
                        type=int,
                        default=1)
    parser.add_argument('-v',
                        '--verbose',
                        help='provide additional details',
                        action='store_true')
    parser.add_argument('--version',
                        help='print program version and exit',
                        action='version',
                        version=f'{ver}')

    # define args to process and make it globally available
    args = parser.parse_args()

    # args checking
    if not os.path.isdir(args.source):
        print(f'Error: source path ({args.source}) does not exist.')
        sys.exit(1)
    if not os.path.isdir(args.target):
        print(f'Error: source path ({args.target}) does not exist.')
        sys.exit(1)
    if args.blocksize < 1 or args.blocksize > 131072:
        print(f'{Col.R}Error: {args.blocksize} invalid. Length must be between'
              f' 1 and 131072.{Col.RES}')
        sys.exit(1)

    main()
