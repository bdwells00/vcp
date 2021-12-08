
import hashlib
import os
import sys
from modules.bp import bp
from modules.ct import Ct
from modules.options import args


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
def overwrite_check(f, operation):

    if operation == 'file':
        question = f'{Ct.YELLOW}({f}) exists. Append? [Y/N]: {Ct.A}'
        if os.path.isfile(f):
            check_append = input(question)
            if check_append[:1].lower() == 'n':
                bp(['Exiting', Ct.YELLOW], erl=1)
                sys.exit(1)
            elif check_append[:1].lower() != 'y':
                bp([f'{check_append} is not "Y" or "N".', Ct.YELLOW], erl=1,
                   fil=0)
                overwrite_check(f, operation)
    elif operation == 'folder':
        question = (f'{Ct.YELLOW}Target folder is not empty. Overwrite?'
                    f'[Y/N]: {Ct.A}')
        if len(os.listdir(f)) > 0:
            check_append = input(question)
            if check_append[:1].lower() == 'n':
                bp(['Exiting', Ct.YELLOW], erl=1)
                sys.exit(1)
            elif check_append[:1].lower() != 'y':
                bp([f'{check_append} is not "Y" or "N".', Ct.YELLOW], erl=1,
                   fil=0)
                overwrite_check(f, operation)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
def folder_validation(f, location):
    """Check if the folder exists. Exit if it does not.

    Args:
        f (string): folder name in string format
        location (string): 'source' or 'target' being checked to provide 
                           proper error output.
    """    
    if not os.path.isdir(f):
        bp([f'"--{location} {f}" does not exist.', Ct.RED], erl=2)
        sys.exit(1)
    return


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
def validate_and_process_args():
    """Validate the arparse args"""
    # ~~~ #         length and blocksize section
    if args.length < 1 or args.length > 128:
        bp([f'"--length {args.length}" invalid. Length must be between (and '
            'including) 1 and 128.', Ct.RED], erl=2)
        sys.exit(1)
    if args.blocksize < 1 or args.blocksize > 1000000:
        bp([f'"--blocksize {args.blocksize}" invalid. Length must be between'
            ' (and including) 1 and 1000000.', Ct.RED], erl=2)
        sys.exit(1)
    # ~~~ #         hash section
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
    # ~~~ #         folder validation section
    if args.source:
        folder_validation(args.source, 'source')
    else:
        bp(['source path not provided.', Ct.RED], erl=2)
        sys.exit(1)
    if args.target:
        folder_validation(args.source, 'target')
    else:
        bp(['target path not provided.', Ct.RED], erl=2)
        sys.exit(1)
    if args.source == args.target:
        bp(['source and target cannot be the same.', Ct.RED], erl=2)
        sys.exit(1)
    # check if target is empty and confirm overwrite
    overwrite_check(args.target, 'folder')
    # ~~~ #         log file validation
    if args.log_file:
        overwrite_check(args.log_file, 'file')
    if args.error_log_file:
        overwrite_check(args.error_log_file, 'file')

    return
