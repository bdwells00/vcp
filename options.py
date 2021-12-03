
__author__ = 'Brandon Wells <wellsb.prog@gmail.com>'
__license__ = 'MIT'
__origin_date__ = '2021-11-18'
__prog__ = 'vcp.py'
__purpose__ = 'Copy contents of one folder to another with hash validation'
__version__ = '0.7.1'
__version_date__ = '2021-12-02'
__version_info__ = tuple(int(i) for i in __version__.split('.') if i.isdigit())


import argparse
BLOCK_SIZE_FACTOR = 1024


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def get_args():
    """Get CLI arguments from argparse.

    Returns:
        - class 'argparse.ArgumentParser': Command Line Arguments
    """
    # Use argparse to capture cli parameters
    parser = argparse.ArgumentParser(
        prog=__prog__,
        description=f'{ver}: {__purpose__}',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog='This program has no warranty. Please use with caution.',
        add_help=True)
    parser.add_argument('-s',
                        '--source',
                        help='source path folder',
                        metavar='<path>',
                        type=str)
    parser.add_argument('-t',
                        '--target',
                        help='target path folder',
                        metavar='<path>',
                        type=str)
    parser.add_argument('--hash',
                        help='hash type to use',
                        metavar='<hash>',
                        type=str,
                        default='sha256')
    parser.add_argument('--length',
                        help='"shake" hash requires a digest length value; '
                             'ignored for all other hashes',
                        metavar='<number>',
                        type=int,
                        default=32)
    parser.add_argument('-b',
                        '--blocksize',
                        help='specify number of 1kB read blocks (1-100000000);'
                             'consumes more ram for minimally faster'
                             ' processing',
                        metavar='<number>',
                        type=int,
                        default=16)
    parser.add_argument('--exdir',
                        help='comma separated directories to exclude (no '
                             'spaces between directories)',
                        metavar='<dir>,<dir>',
                        type=str)
    parser.add_argument('--exfile',
                        help='comma separated files to exclude (no spaces '
                             'between files)',
                        metavar='<file>,<file>',
                        type=str)
    parser.add_argument('--log',
                        help='add timestamp logging to output',
                        action='store_true')
    parser.add_argument('--log-file',
                        help='file to save output',
                        metavar='<filename>',
                        type=str)
    parser.add_argument('--error-log-file',
                        help='file to save output',
                        metavar='<filename>',
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


print_tracker = 0
ver = f'{__prog__} v{__version__} ({__version_date__})'
args = get_args()
