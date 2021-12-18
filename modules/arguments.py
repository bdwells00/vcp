

import argparse
import hashlib
from pathlib import Path
import sys
from betterprint.betterprint import bp
from betterprint.colortext import Ct
import modules.version as version


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
def overwrite_check(f: str, operation: str):
    """Check if file or folder exists and ask if it should be appended or
    overwritten.

    - Args:
        - f (str): the file or folder from argparse input
        - operation (str): check if file or folder
    """
    f_path = Path(f)
    if operation == 'file':
        question = f'{Ct.YELLOW}({f}) exists. Append? [Y/N]: {Ct.A}'
        if f_path.is_file():
            check_append = input(question)
            if check_append.lower() == 'n':
                bp(['Exiting', Ct.YELLOW], err=1)
                sys.exit(1)
            elif check_append.lower() != 'y':
                bp([f'{check_append} is not "Y" or "N".', Ct.YELLOW], err=1,
                   fil=0)
                overwrite_check(f, operation)
    elif operation == 'folder':
        question = (f'{Ct.YELLOW}Target folder is not empty. Overwrite?'
                    f'[Y/N]: {Ct.A}')
        if any(f_path.iterdir()):
            check_overwrite = input(question)
            if check_overwrite.lower() == 'n':
                bp(['Exiting', Ct.YELLOW], err=1)
                sys.exit(1)
            elif check_overwrite.lower() != 'y':
                bp([f'{check_overwrite} is not "Y" or "N".', Ct.YELLOW], err=1,
                   fil=0)
                overwrite_check(f, operation)
    return


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
def folder_validation(f: str, location: str):
    """Check if the folder exists. Exit if it does not.

    - Args:
        - f (string): folder name in string format
        - location (string): 'source' or 'target' being checked to provide
                             proper error output.
    """
    file = Path(f)
    if not file.is_dir():
        bp([f'"--{location} {f}" does not exist.', Ct.RED], err=2)
        sys.exit(1)
    return


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
def get_args():
    """Get CLI arguments from argparse and validate them.

    Returns:
        - class 'argparse.ArgumentParser': Command Line Arguments
    """
    # ~~~ #                 -argparse-
    parser = argparse.ArgumentParser(
        prog=version.__prog__,
        description=f'{Ct.BBLUE}{version.ver}: {version.__purpose__}{Ct.A}',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog='This program has no warranty. Please use with caution.',
        add_help=True)
    parser.add_argument('-s',
                        '--source',
                        help='source path folder',
                        metavar=f'{Ct.RED}<path>{Ct.A}',
                        type=str)
    parser.add_argument('-t',
                        '--target',
                        help='target path folder',
                        metavar=f'{Ct.RED}<path>{Ct.A}',
                        type=str)
    parser.add_argument('--hash',
                        help='hash type to use',
                        metavar=f'{Ct.GREEN}<hash>{Ct.A}',
                        type=str,
                        default='sha256')
    parser.add_argument('--length',
                        help='"shake" hash requires a digest length value; '
                             'ignored for all other hashes',
                        metavar=f'{Ct.GREEN}<number>{Ct.A}',
                        type=int,
                        default=32)
    parser.add_argument('--blocksize',
                        help='specify number of 1kB read blocks (1-1000000);'
                             'consumes more ram for minimally faster'
                             ' processing',
                        metavar=f'{Ct.GREEN}<number>{Ct.A}',
                        type=int,
                        default=16)
    parser.add_argument('--date-log',
                        help='add timestamp logging to output',
                        action='store_true')
    parser.add_argument('--exdir',
                        help='comma separated directories to exclude (no '
                             'spaces between directories)',
                        metavar=f'{Ct.GREEN}<dir>,<dir>{Ct.A}',
                        type=str)
    parser.add_argument('--exfile',
                        help='comma separated files to exclude (no spaces '
                             'between files)',
                        metavar=f'{Ct.GREEN}<file>,<file>{Ct.A}',
                        type=str)
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
    parser.add_argument('--quiet',
                        help='quiet mode surpresses most output including '
                             'errors but keeps final summary',
                        action='store_true')
    parser.add_argument('--available',
                        help='print available hashes and exit',
                        action='store_true')
    parser.add_argument('-v',
                        '--verbose',
                        help='3 lvl incremental verbosity (-v, -vv, or -vvv)',
                        action='count',
                        default=0)
    parser.add_argument('--version',
                        help='print program version and exit',
                        action='version',
                        version=f'{Ct.BBLUE}{version.ver}')

    # ~~~ #                 -variables-
    args = parser.parse_args()

    # ~~~ #                 -length and blocksize-
    if args.length < 1 or args.length > 128:
        bp([f'"--length {args.length}" invalid. Length must be between (and '
            'including) 1 and 128.', Ct.RED], err=2)
        sys.exit(1)
    if args.blocksize < 1 or args.blocksize > 1000000:
        bp([f'"--blocksize {args.blocksize}" invalid. Length must be between'
            ' (and including) 1 and 1000000.', Ct.RED], err=2)
        sys.exit(1)

    # ~~~ #                 -hash-
    # create list of available hash algorithms
    hash_list = [i for i in sorted(hashlib.algorithms_guaranteed)]
    if args.available:
        avail_str = ('Available:\nHash:\t\tBlock size:\tDigest Length:\tHex '
                     'Length:\n')
        for i in hash_list:
            if 'shake' not in i:
                avail_str += (f'{Ct.RED}{i:<16s}{Ct.A}'
                              f'{getattr(hashlib, i)().block_size:<16}'
                              f'{getattr(hashlib, i)().digest_size:<16}'
                              f'{2 * getattr(hashlib, i)().digest_size:<16}\n')
            else:
                avail_str += (f'{Ct.RED}{i:<16s}{Ct.A}'
                              f'{getattr(hashlib, i)().block_size:<16}'
                              f'{args.length:<16}{2 * args.length:<16}\n')
        bp([avail_str, Ct.BBLUE], num=0)
        sys.exit(0)

    # ~~~ #                 -folder validation-
    if args.source:
        folder_validation(args.source, 'source')
    else:
        bp(['source path not provided.', Ct.RED], err=2)
        sys.exit(1)
    if args.target:
        folder_validation(args.source, 'target')
    else:
        bp(['target path not provided.', Ct.RED], err=2)
        sys.exit(1)
    if args.source == args.target:
        bp(['source and target cannot be the same.', Ct.RED], err=2)
        sys.exit(1)
    # check if target is empty and confirm overwrite
    overwrite_check(args.target, 'folder')

    # ~~~ #                 -log-
    if args.log_file:
        overwrite_check(args.log_file, 'file')
    if args.error_log_file:
        overwrite_check(args.error_log_file, 'file')

    return args
