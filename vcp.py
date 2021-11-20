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
__version__ = '0.0.2'
__version_date__ = '2021-11-19'
__version_info__ = tuple(int(i) for i in __version__.split('.') if i.isdigit())
ver = f'{__prog__} v{__version__} ({__version_date__})'


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Col:
    """A simple class for minimal usage-length to add colorized text print
    using ANSI ESC sequences.

    # This will print a Blue text Hello on the terminal default background
      color, then reset the text color to terminal default.
    Example: print(f'{Col.B}Hello{Col.RES})"""

    R = '\033[31m'      # red
    G = '\033[32m'      # green
    Y = '\033[33m'      # yellow
    B = '\033[94m'      # bright blue
    RES = '\033[0m'     # reset to terminal defaults


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def args_from_argparse():
    """Get CLI arguments from argparse and perform basic checks to ensure they
    are valid.

    Returns:
        class 'argparse.ArgumentParser': Command Line Arguments
    """
    # TODO source and target are "optional" but should be required
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
    parser.add_argument('--available',
                        help='print available hashes and exit',
                        action='store_true')
    parser.add_argument('--blocksize',
                        help='specify number of 1K read blocks between 1 and '
                             '131072 (consumes more ram for min. speed gains)',
                        metavar=f'{Col.Y}<number>{Col.RES}',
                        type=int,
                        default=16)
    parser.add_argument('--log',
                        help='log output to file specified',
                        metavar=f'{Col.Y}<path/filename>{Col.RES}',
                        type=str)
    parser.add_argument('--elog',
                        help='error log output to file specified',
                        metavar=f'{Col.Y}<path/filename>{Col.RES}',
                        type=str)
    parser.add_argument('--length',
                        help='"shake" hash requires a digest length value; '
                             'ignored for all other hashes',
                        metavar=f'{Col.Y}<number>{Col.RES}',
                        type=int,
                        default=32)
    parser.add_argument('-q',
                        '--quiet',
                        help='quiet mode surpresses all output except errors'
                             ' and final summary',
                        action='store_true')
    parser.add_argument('--threads',
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

    args_f = parser.parse_args()

    # perform arg checks prior to returning the argparse class
    # shake requires length of 1 or greater, before available to show properly
    if args_f.length < 1 or args_f > 128:
        print(f'{Col.R}Error: "--length {args_f.length}" invalid. Length must'
              f' be from 1 to 128.{Col.RES}')
        sys.exit(1)
    # if --available, print all available hashes and exit
    if args_f.available:
        h_list = [i for i in sorted(hashlib.algorithms_guaranteed)]
        print(f'{Col.B}{ver}{Col.RES}\n\nAvailable:\nHash:\t\tBlock size:'
              '\tDigest Length:')
        for i in h_list:
            if 'shake' not in i:
                print(f'{Col.R}{i:<15s}{Col.RES} '
                      f'{getattr(hashlib, i)().block_size:<16}{Col.B}'
                      f'{getattr(hashlib, i)().digest_size}{Col.RES}')
            else:
                print(f'{Col.R}{i:<15s}{Col.RES} '
                      f'{getattr(hashlib, i)().block_size:<16}{Col.B}'
                      f'{args_f.length}{Col.RES}')
        sys.exit(0)
    # validate source and target paths
    if args_f.source:
        if not os.path.isdir(args_f.source):
            print(f'{Col.R}Error: "--source {args_f.source}" does not exist.'
                  f'{Col.RES}')
            sys.exit(1)
    else:
        print(f'{Col.R}Error: source path not provided.{Col.RES}')
        sys.exit(1)
    if args_f.target:
        if not os.path.isdir(args_f.target):
            print(f'{Col.R}Error: "--target {args_f.target}" does not exist.'
                  f'{Col.RES}')
            sys.exit(1)
    else:
        print(f'{Col.R}Error: target path not provided.{Col.RES}')
        sys.exit(1)
    if args_f.source == args_f.target:
        print(f'{Col.R}Error: source and target cannot be the same.{Col.RES}')
        sys.exit(1)
    # TODO when program is mature, allow overwriting. For now, deny it.
    if os.listdir(args_f.target):
        print(f'{Col.R}Error: "--target {args_f.target}" not empty.{Col.RES}')
    # confirm blocksize is 1k to 128mb, and threads 1-128
    if args_f.blocksize < 1 or args_f.blocksize > 131072:
        print(f'{Col.R}Error: "--blocksize {args_f.blocksize}" invalid. Length'
              f' must be from 1 to 131072.{Col.RES}')
        sys.exit(1)
    if args_f.threads < 1 or args_f.threads > 128:
        print(f'{Col.R}Error: "--threads {args_f.threads}" invalid. Threads '
              f'must be from 1 to 128.{Col.RES}')

    return args_f


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def con_output(c_out: str):
    """All console output goes through this function. Adds support for logging.

    Args:
        c_out (str): The data to print to the console
    """
    print(f'{datetime.now()}\t|\t{c_out}') if args.verbose else print(c_out)

    return


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def file_output(f_out: str, ft: str):
    """Append to the log or error file. Called any time logging is required.
    If errors are encountered, print to the console even if quite mode.

    Args:
        f_out (str): The data to write to the log or elog file
        ft (str): Either args.log or args.elog
    """
    try:
        with open(ft, 'a') as f:
            f.write(f'{datetime.now()}\t|\t{f_out}')
    except OSError as e:
        con_output(f'{Col.R}Error: cannot open {ft} to output.\n{e}\nTried to '
                   f'write:{f_out}{Col.RES}')

    return


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def tree_walk():

    try:
        time_data, source_path = dd(int), dd(int)
    except OSError as e:
        e_var = (f'Error durring the tree walk of source: {args.source}\n'
                 f'Error:\n{e}')
        if args.elog:
            file_output(e_var, args.elog)
        con_output(e_var)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def main():
    pass


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if __name__ == '__main__':

    # get args to make it global
    args = args_from_argparse()

    main()
