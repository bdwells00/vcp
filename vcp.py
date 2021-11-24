#!/usr/bin/python3-64 -X utf8


import argparse
from collections import defaultdict as dd
from datetime import datetime
import hashlib
from math import ceil
import os
import sys
import time
BLOCK_SIZE_FACTOR = 1024
START_PROG_TIME = datetime.now()


__author__ = 'Brandon Wells <wellsb.prog@gmail.com>'
__license__ = 'MIT'
__origin_date__ = '2021-11-18'
__prog__ = 'vcp.py'
__purpose__ = 'Copy contents of one folder to another with hash validation'
__version__ = '0.3.0'
__version_date__ = '2021-11-23'
__version_info__ = tuple(int(i) for i in __version__.split('.') if i.isdigit())
ver = f'{__prog__} v{__version__} ({__version_date__})'


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def ct(text_in: str, text_color: str):
    """Colorize text using Unicode escape sequences stored in a dictionary.
    Thisprepends the text with the requested color escape sequence, then
    appends the text with the reset escape sequence so follow-on text is not
    colored.

    Args:
        text_in (str): The text to be colored
        text_color (str): The color to apply to the text

    Returns:
        text_out (str): colorized text
    """
    colors = {
        'r': '\u001b[31m',    # red
        'g': '\u001b[32m',    # green
        'y': '\u001b[33m',    # yellow
        'b': '\u001b[94m',    # bright blue
        'reset': '\u001b[0m'  # reset terminal color
    }
    text_out = f'{colors[text_color]}{text_in}{colors["reset"]}'

    return text_out


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def lp(output_txt: str, verbose_level: int):
    """All console printing except native argparse goes through this function.
    Allows verbose styling levels.

    Args:
        output_text (str): the text to print
        verbose_level (int): used to match args.verbose for correct type
            0: default (always print)
            1: Error level logging
            2: Warning level logging
            3: Info level logging
    """
    dt_now = datetime.now().strftime('%y%m%d-%H:%M:%S')
    if verbose_level == 0:
        print(output_txt)
    elif args.verbose == 0 and verbose_level == 1:
        print(f'{ct("ERROR: ", "r")}{output_txt}')
    elif args.verbose == 1 and verbose_level == 0:
        print(f'{dt_now} : {ct("OUTPUT: ", "g")} : '
              f'{output_txt}')
    elif args.verbose == 1 and verbose_level == 1:
        print(f'{dt_now} : {ct("ERROR: ", "r")} : '
              f'{output_txt}')
    elif args.verbose == 2 and verbose_level == 2:
        print(f'{dt_now} : {ct("WARNING: ", "y")} : '
              f'{output_txt}')
    elif args.verbose == 3 and verbose_level == 3:
        print(f'{dt_now} : {ct("INFO: ", "b")} : '
              f'{output_txt}')

    return


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
        description=ct(f'{ver}: {__purpose__}', 'b'),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog='This program has no warranty. Please use with caution. ',
        add_help=True)
    parser.add_argument('-s',
                        '--source',
                        help='source path folder',
                        metavar=ct('<path>', 'r'),
                        type=str)
    parser.add_argument('-t',
                        '--target',
                        help='target path folder',
                        metavar=ct('<path>', 'r'),
                        type=str)
    parser.add_argument('--hash',
                        help='hash type to use',
                        metavar=ct('<hash>', 'g'),
                        type=str,
                        default='blake2b')
    parser.add_argument('--blocksize',
                        help='specify number of 1K read blocks between 1 and '
                             '131072 (consumes more ram for min. speed gains)',
                        metavar=ct('<number>', 'g'),
                        type=int,
                        default=16)
    parser.add_argument('--exdir',
                        help='comma separated directories to exclude (no '
                             'spaces between directories)',
                        metavar=ct('<dir>,<dir>', 'g'),
                        type=str)
    parser.add_argument('--exfile',
                        help='comma separated files to exclude (no spaces '
                             'between files)',
                        metavar=ct('<file>,<file>', 'g'),
                        type=str)
    parser.add_argument('--log',
                        help='log output to file specified',
                        metavar=ct('<path/filename>', 'g'),
                        type=str)
    parser.add_argument('--elog',
                        help='error log output to file specified',
                        metavar=ct('<path/filename>', 'g'),
                        type=str)
    parser.add_argument('--length',
                        help='"shake" hash requires a digest length value; '
                             'ignored for all other hashes',
                        metavar=ct('<number>', 'g'),
                        type=int,
                        default=32)
    # parser.add_argument('--threads',
    #                     help='number of copy and validation threads',
    #                     metavar=f'{Col.Y}<num>{Col.RES}',
    #                     type=int,
    #                     default=1)
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
                        version=ct(ver, 'b'))

    return parser.parse_args()


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def args_checker():
    # perform arg checks prior to returning the argparse class
    # shake requires length of 1 or greater, before available to show properly
    if args.length < 1 or args.length > 128:
        lp(ct(f'"--length {args.length}" invalid. Length must be from 1 to '
              f'128.', 'r'), 1)
        sys.exit(1)
    # if --available, print all available hashes and exit
    if args.available:
        h_list = [i for i in sorted(hashlib.algorithms_guaranteed)]
        lp(f'{ct(ver, "b")}\n\nAvailable:\nHash:\t\tBlock size:\tDigest '
            'Length:', 0)
        for i in h_list:
            if 'shake' not in i:
                lp(f'{ct(f"{i:<15s}", "r")} '
                   f'{getattr(hashlib, i)().block_size:<16}'
                   f'{ct(f"{getattr(hashlib, i)().digest_size}", "b")}', 0)
            else:
                lp(f'{ct(f"{i:<15s}", "r")} '
                   f'{getattr(hashlib, i)().block_size:<16}'
                   f'{ct(args.length, "b")}', 0)
        sys.exit(0)
    # validate source and target paths
    if args.source:
        if not os.path.isdir(args.source):
            lp(ct(f'"--source {args.source}" does not exist.', 'r'), 1)
            sys.exit(1)
    else:
        lp(ct('source path not provided.', 'r'), 0)
        sys.exit(1)
    if args.target:
        if not os.path.isdir(args.target):
            lp(ct(f'"--target {args.target}" does not exist.', 'r'), 1)
            sys.exit(1)
    else:
        lp(ct('target path not provided.', 'r'), 1)
        sys.exit(1)
    if args.source == args.target:
        lp(ct('source and target cannot be the same.', 'r'), 1)
        sys.exit(1)
    # TODO when program is mature, allow overwriting. For now, deny it.
    if os.listdir(args.target):
        lp(ct(f'"--target {args.target}" not empty.', 'r'), 1)
        sys.exit(1)
    # confirm blocksize is 1k to 128mb, and threads 1-128
    if args.blocksize < 1 or args.blocksize > 131072:
        lp(ct(f'"--blocksize {args.blocksize}" invalid. Length must be from '
              f'1 to 131072.', 'r'), 1)
        sys.exit(1)
    # if args_f.threads < 1 or args_f.threads > 128:
    #     lp(ct(f'"--threads {args_f.threads}" invalid. Threads must be from 1'
    #           f' to 128.', 'r'), 1)

    return


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def file_output(out_text: str, out_file: str):
    """Append to the log or error file. Called by the log_logic function for
    all output to files.

    Args:
        out_text (str): the data to write to the log or elog file
        out_file (str): either args.log or args.elog
    """
    try:
        with open(out_file, 'a') as f:
            f.write(f'{datetime.now()} | {out_text}')
    except OSError as e:
        lp(ct(f'cannot open {args.elog}.\n{e}\nTried to write:{out_text}',
           'r'), 1)

    return


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def log_logic(log_text: str, log_mode: int):
    """Intermediary that will call file_outputs if logging or error logging is
    enabled.

    Args:
        log_text (str): the text to output to file
        log_mode (int):
            0 : output standard logging      (everything)
            1 : output error logging         (errors only)
    """
    # add error info if mode 1, else leave as is
    log_text = f'Error: {log_text}' if log_mode == 1 else log_text

    if args.log:
        file_output(log_text, args.log)
    if args.elog and log_mode == 1:
        file_output(log_text, args.elog)

    return


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def tree_walk_error_output(os_error: str):
    """Receive errors from tree_walk function, color red, then send to output
    either just log file or both log and elog files.

    Args:
        os_error (str): os.walk onerror output
    """
    lp(ct(os_error, 'r'), 1)
    log_logic(os_error, 1)

    return


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def tree_walk():
    """Tree walks the source folder and populates several variables

    Returns:
        tuple:
            walk_time:      float of time it took to tree walk
            walk_folders:   list of folders from the tree walk
            walk_files:     list of files from the tree walk
            data_size:      total size of all files
    """
    try:
        walk_time, walk_folders, walk_files, data_size = '', [], [], 0
        # create exdir and exfile lists
        if args.exdir:
            exdir = args.exdir.split(',')
        if args.exfile:
            exfile = args.exfile.split(',')
        walk_start = time.monotonic()
        for root, dirs, files, in os.walk(args.source,
                                          topdown=True,
                                          onerror=tree_walk_error_output):
            # strip excluded directories and files
            if args.exdir:
                dirs[:] = [d for d in dirs if d not in exdir]
            if args.exfile:
                files[:] = [f for f in files if f not in exfile]
            # populate the directory list
            for d in dirs:
                dir_fp = f'{root}/{d}' if root != '/' else f'{root}{d}'
                walk_folders.append(dir_fp)
            # poopulate the file list
            for f in files:
                file_fp = f'{root}/{f}' if root != '/' else f'{root}{f}'
                walk_files.append(file_fp)
                # get cumulative file size
                try:
                    f_info = os.stat(file_fp, follow_symlinks=False)
                    data_size += f_info.st_size
                except OSError as e:
                    e_var = (f'Tree walk of source: {args.source}\n{e}')
                    lp(ct(e_var, 'r'), 1)
                    log_logic(e_var, 1)
        walk_stop = time.monotonic()
        # calculate total tree walk time
        walk_time = (walk_stop - walk_start)
    except OSError as e:
        e_var = f'tree walk failure: {args.source}\n{e}'
        lp(ct(e_var, 'r'), 1)
        log_logic(e_var, 1)

    return walk_time, walk_folders, walk_files, data_size


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def create_folder(folder_source: str):
    """Create a folder on each call.

    Args:
        folder_source (str): the folder to create

    Returns:
        int: 0 is success; 1 is failure
    """
    # swap the target for the source in the string
    folder_target = folder_source.replace(args.source, args.target)
    try:
        # create the folder
        os.mkdir(folder_target)
        # TODO adjust the folder date to match the source
        # TODO adjust the folder permissions to match the source

        return 0, folder_target

    except OSError as e:
        lp(f'{ct("Error: ", "r")}{folder_target}\n\t{e}', 1)
        log_logic(f'Error: {folder_target}\n\t{e}', 1)

        return 1, folder_target


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def file_multifunction(file_source: str, file_action: str):
    """Copy or read the file with hashing.

    Args:
        file_source (str): the file to copy or read
        file_action (str): either 'copy' or 'read'

    Returns:
        tuple:
            file_rtime      read file timer
            file_wtime      write file timer
            hash_time       hash timer
            hash_hex        the hash hexadecimal
            file_target     the target file name
            file_size       the size of the source file
    """
    # swap the target for the source in the string
    file_target = file_source.replace(args.source, args.target)
    # hashlib function variable
    hlib_var = (getattr(hashlib, args.hash)())
    file_rtime, file_wtime, file_size, hash_time, hash_hex = 0, 0, 0, 0, ''
    try:
        # get the size of the file copied or read
        f_info = os.stat(file_source, follow_symlinks=False)
        file_size = f_info.st_size
        file_loop = 0
        f_loops = ceil(file_size / (args.blocksize * BLOCK_SIZE_FACTOR))
        # target output variable
        t_o = 'wb' if file_action == 'copy' else 'rb'
        # fr is file read, fw is file write, fw open but ignored on read
        with open(file_source, 'rb') as fr, open(file_target, t_o) as fw:
            while True:
                fr_start = time.monotonic()
                # read source in blocks to prevent potential memory overload
                f_chunk = fr.read(args.blocksize * BLOCK_SIZE_FACTOR)
                fr_stop = time.monotonic()
                # calculate time to read the file
                file_rtime += (fr_stop - fr_start)
                # this breaks the while loop when no more file chunks to read
                if not f_chunk:
                    if args.verbose == 3:
                        print()
                    break
                h_start = time.monotonic()
                # update the hash on each chunk
                hlib_var.update(f_chunk)
                h_stop = time.monotonic()
                # calculate the time to hash the file
                hash_time += (h_stop - h_start)
                # skip this section on read hashing, otherwise copy the file
                if file_action == 'copy':
                    fw_start = time.monotonic()
                    fw.write(f_chunk)
                    fw_stop = time.monotonic()
                    # calculate the time to write the file
                    file_wtime += (fw_stop - fw_start)
                # loop and stdout print a status of the current file processing
                file_loop += 1
                if args.verbose == 3:
                    sys.stdout.write(f'\u001b[1000D'
                                     f'{(file_loop / f_loops) * 100:.0f}% | '
                                     f'{file_source}')
        # convert the hash to hexadecimal
        hh_start = time.monotonic()
        if 'shake' in args.hash:
            hash_hex = hlib_var.hexdigest(args.length)
        else:
            hash_hex = hlib_var.hexdigest()
        hh_stop = time.monotonic()
        # add the hex conversion to the has timer
        hash_time += (hh_stop - hh_start)

        return (0, file_rtime, file_wtime, hash_time, hash_hex, file_target,
                file_size)

    except OSError as e:
        e_var = (f'with file {file_action}: {file_source}\n{e}')
        lp(ct(e_var, 'r'), 1)
        log_logic(f'Error: {e_var}', 1)

        return 1


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def main():

    try:
        lp(f'{ct(ver, "b")}\nProgram start: {ct(START_PROG_TIME, "b")}\nSource'
           f': {ct(args.source, "g")}\nTarget: {ct(args.target, "g")}', 0)
        # TODO print the cli arguments
        # execute the tree walk
        tw_tup = tree_walk()
        # print out the tree walk data
        lp(f'Folders: {ct(len(tw_tup[1]), "b")} | Files: '
           f'{ct(len(tw_tup[2]), "b")} | Size: {ct(tw_tup[3], "b")}', 0)
        # execute folder creation and time it
        fo_time_start = time.monotonic()
        folder_dict, folder_success, folder_failure = dd(int), 0, 0
        for folder in tw_tup[1]:
            # create each folder and get back 0 for success and 0 for error
            folder_return = create_folder(folder)
            # populate dict to track success or failure
            folder_dict[folder] = folder_return[0]
            if folder_return[0] == 0:
                folder_success += 1
                lp(f'Created: {ct(folder_return[1], "g")}', 3)
                log_logic(f'Created: {folder_return[1]}', 0)
            else:
                folder_failure += 1
                lp(ct(f'Failed!: {folder_return[1]}', "r"), 1)
                log_logic(f'Failed!: {folder_return[1]}', 1)
        fo_time_stop = time.monotonic()
        # calculate folder creation time
        folder_time = f'{(fo_time_stop - fo_time_start):.4f}s'
        # variables for file processing
        fc_rtime, fc_wtime, hc_time, fr_rtime, hr_time = 0, 0, 0, 0, 0
        file_success, file_failure, file_size_copied = 0, 0, 0
        val_success, val_failure = 0, 0
        # copy each file and validate it with stats
        # TODO add confirmation for file copy and read
        for file in tw_tup[2]:
            # execute file creation and hashing, and gather stats
            c_stat = file_multifunction(file, 'copy')
            if c_stat[0] == 0:
                file_success += 1
                fc_rtime += c_stat[1]
                fc_wtime += c_stat[2]
                hc_time += c_stat[3]
                f_target = c_stat[5]
                file_size_copied += c_stat[6]
                lp(f'Copied: {ct(c_stat[5], "g")}', 3)
                log_logic(f'Copied: {c_stat[5]}', 0)
            else:
                file_failure += 1
                lp(f'Failed Copy!: {ct(c_stat[5], "g")}', 1)
                log_logic(f'Failed!: {c_stat[5]}', 1)
            # execute target file read and hashing, and gather stats
            r_stat = file_multifunction(f_target, 'read')
            if r_stat[0] == 0:
                fr_rtime += r_stat[1]
                hr_time += r_stat[2]
                if c_stat[4] == r_stat[4]:
                    val_success += 1
                    lp(f'{ct("Validated: source & target hex match.", "g")}'
                       f'\n\t{c_stat[4]}\n\t{r_stat[4]}', 3)
                    log_logic('Validated: source & target hex match.\n'
                              f'{c_stat[4]}\n{r_stat[4]}', 0)
                else:
                    val_failure += 1
                    lp(f'{ct("Source & target hex DO NOT MATCH!", "r")}'
                       f'\n\t{c_stat[4]}\n\t{r_stat[4]}', 1)
                    log_logic('Source & target hex DO NOT MATCH!\n'
                              f'{c_stat[4]}\n{r_stat[4]}', 1)
            else:
                lp(f'Failed reading copied file!: {ct(c_stat[4], "g")}', 1)
                log_logic(f'Failed reading copied file!: {c_stat[4]}', 1)
        # get program end time and calculate overhead
        # prog_end = datetime.now()
        # prog_overhead = pro
        # print out final copy stats
        lp(f'\n{" " * 16}Source    Target    FAILED        TIME', 0)
        log_logic(f'\n{" " * 16}Source    Target    FAILED        TIME', 0)
        lp(f'      Dirs: {len(tw_tup[1]):>10}{folder_success:>10}'
           f'{folder_failure:>10}{folder_time:>12}', 0)
        log_logic(f'      Dirs: {len(tw_tup[1]):>10}{folder_success:>10}'
                  f'{folder_failure:>10}{folder_time:>10}', 0)
        lp(f'     Files: {len(tw_tup[2]):>10}{file_success:>10}'
           f'{file_failure:>10}{fc_rtime + fc_wtime:>11.4f}s', 0)
        log_logic(f'     Files: {len(tw_tup[2]):>9}{file_success:>9}'
                  f'{file_failure:>10}{fc_rtime + fc_wtime:>11.4f}', 0)
        lp(f'Validation: {len(tw_tup[2]):>10}{val_success:>10}'
           f'{val_failure:>10}{hc_time + hr_time:>11.4f}s (+{fr_rtime:.4f})s',
            0)
        log_logic(f'Validation: {len(tw_tup[2]):>10}{val_success:>10}'
                  f'{val_failure:>10}{hc_time + hr_time:>11.4f}s '
                  f'(+{fr_rtime:.4f}s)', 0)

    except KeyboardInterrupt:
        lp(ct('Ctrl+C pressed...\n', "r"), 1)
        log_logic('Ctrl+C pressed...\n', 1)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if __name__ == '__main__':

    # get args to make it global
    args = args_from_argparse()
    # perform arg checking
    args_checker()

    main()
