

import argparse
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

    return parser.parse_args()
