

import argparse
import hashlib
import os
from modules.ct import Ct
import modules.version as version


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
def get_args():
    """Get CLI arguments from argparse.

    Returns:
        - class 'argparse.ArgumentParser': Command Line Arguments
    """
    # Use argparse to capture cli parameters
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
    parser.add_argument('--quiet',
                        help='quiet mode surpresses all output except errors'
                             ' and final summary',
                        action='store_true')
    parser.add_argument('--available',
                        help='print available hashes and exit',
                        action='store_true')
    parser.add_argument('--verbose',
                        help='3 lvl incremental verbosity (-v, -vv, or -vvv)',
                        action='count',
                        default=0)
    parser.add_argument('--version',
                        help='print program version and exit',
                        action='version',
                        version=f'{Ct.BBLUE}{version.ver}')

    return parser.parse_args()


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
def validate_and_process_args():
    """Validate args

    - Args:
        - h_list (list): a list of all hashes available to python on the
                         platform

    - Returns:
        - various [tuple]: positions within the tuple
            - 0:    0 to exit w/ 0; 1 to exit w/ 1; 2 continue with program
            - 1:    string to print on failure
            - 2:    string color
            - 3:    bp num level
            - 4:    bp erl level

    """
    # ~~~ #         length and blocksize section
    if args.length < 1 or args.length > 128:
        return_str = (f'"--length {args.length}" invalid. Length must be '
                      'between (and including) 1 and 128.')
        return 1, return_str, Ct.RED, 1, 2
    if args.blocksize < 1 or args.blocksize > 1000000:
        return_str = (f'"--blocksize {args.blocksize}" invalid. Length must '
                      'be between (and including) 1 and 1000000.')
        return 1, return_str, Ct.RED, 1, 2
    # ~~~ #         hash section
    # create list of available hash algorithms
    hash_list = [i for i in sorted(hashlib.algorithms_guaranteed)]
    if args.available:
        return_str = ('Available:\nHash:\t\tBlock size:\tDigest Length:\tHex '
                      'Length:\n')
        for i in hash_list:
            if 'shake' not in i:
                return_str += (f'{Ct.RED}{i:<16s}{Ct.A}'
                               f'{getattr(hashlib, i)().block_size:<16}'
                               f'{getattr(hashlib, i)().digest_size:<16}'
                               f'{2 * getattr(hashlib, i)().digest_size:<16}\n'
                               )
            else:
                return_str += (f'{Ct.RED}{i:<16s}{Ct.A}'
                               f'{getattr(hashlib, i)().block_size:<16}'
                               f'{args.length:<16}{2 * args.length:<16}\n')
        return 0, return_str, Ct.BBLUE, 0, 0
    # ~~~ #         folder validation section
    if args.source:
        if not os.path.isdir(args.source):
            return_str = f'"--source {args.source}" does not exist.'
            return 1, return_str, Ct.RED, 1, 2
    else:
        return_str = 'source path not provided.'
        return 1, return_str, Ct.RED, 1, 2
    if args.target:
        if not os.path.isdir(args.target):
            return_str = f'"--target {args.target}" does not exist.'
            return 1, return_str, Ct.RED, 1, 2
    else:
        return_str = 'target path not provided.'
        return 1, return_str, Ct.RED, 1, 2
    if args.source == args.target:
        return_str = 'source and target cannot be the same.'
        return 1, return_str, Ct.RED, 1, 2

    return 2, 'Success', Ct.A, 1, 0


args = get_args()
