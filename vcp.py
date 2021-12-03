#!/usr/bin/python3-64 -X utf8


from collections import defaultdict as dd
from datetime import datetime
import hashlib
from math import ceil
import os
import sys
import time
from bp import bp, Ct
import options
START_PROG_TIME = time.monotonic()


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def validate_and_process_args(h_list: list):
    """Validate and process the cli args before executing main()."""
    bp([f'entered validate_and_process_args({h_list})', Ct.BMAGENTA], veb=3)
    bp(['confirm the length and blocksize variables are within set limits',
        Ct.BMAGENTA], veb=3)
    if args.length < 1 or args.length > 128:
        bp([f'"--length {args.length}" invalid. Length must be between (and '
            'including) 1 and 128.', Ct.RED], erl=2)
        sys.exit(1)
    if args.blocksize < 1 or args.blocksize > 100000000:
        bp([f'"--blocksize {args.blocksize}" invalid. Length must between (and'
            ' including) 1 and 100000000.', Ct.RED], erl=2)
        sys.exit(1)
    bp(['print available hashes and exit if requested', Ct.BMAGENTA], veb=3)
    if args.available:
        bp(['Available:\nHash:\t\tBlock size:\tDigest Length:\tHex Length:',
            Ct.A])
        for i in h_list:
            if 'shake' not in i:
                bp([f'{i:<16s}', Ct.RED,
                    f'{getattr(hashlib, i)().block_size:<16}'
                    f'{getattr(hashlib, i)().digest_size:<16}'
                    f'{2 * getattr(hashlib, i)().digest_size:<16}', Ct.BBLUE],
                    num=0)
            else:
                bp([f'{i:<16s}', Ct.RED,
                    f'{getattr(hashlib, i)().block_size:<16}{args.length:<16}'
                    f'{2 * args.length:<16}', Ct.BBLUE], num=0)
        sys.exit(0)
    # validate source and target paths
    if args.source:
        if not os.path.isdir(args.source):
            bp([f'"--source {args.source}" does not exist.', Ct.RED], erl=2)
            sys.exit(1)
    else:
        bp(['source path not provided.', Ct.RED], erl=2)
        sys.exit(1)
    if args.target:
        if not os.path.isdir(args.target):
            bp([f'"--target {args.target}" does not exist.', Ct.RED], erl=2)
            sys.exit(1)
    else:
        bp(['target path not provided.', Ct.RED], erl=2)
        sys.exit(1)
    if args.source == args.target:
        bp(['source and target cannot be the same.', Ct.RED], erl=2)
        sys.exit(1)

    return


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def decimal_notation(size: int, accuracy=2, notation=0):
    """Decimal Notation: take an integer, convert it to a string with the
    requested decimal accuracy, and append either single (default), double,
    or full word character notation.

    Args:
        - size (int): the size to convert
        - accuracy (int): how many decimal places to keep (default=2)
        - precision (int): how many characters to return denoting multiplier

    Returns:
        - [tuple]: 0 = original size int unmodified; 1 = string for printing
    """
    size_dict = {
        1: ['B', 'B', 'bytes'],
        1000: ['k', 'kB', 'kilobytes'],
        1000000: ['M', 'MB', 'megabytes'],
        1000000000: ['G', 'GB', 'gigabytes'],
        1000000000000: ['T', 'TB', 'terabytes']
    }
    return_size_str = ''
    for key, value in size_dict.items():
        if (size / key) < 1000:
            return_size_str = f'{size / key:,.{accuracy}f} {value[notation]}'
            break

    return size, return_size_str


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def tree_walk_error_output(os_error: str):
    """Receive errors from tree_walk function, color red, then send to output
    either just log file or both log and elog files.

    Args:
        - os_error (str): os.walk onerror output
    """
    bp([os_error, Ct.RED], erl=2)

    return


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def tree_walk():
    """Tree walks the source folder and populates several variables

    Returns:
        - tuple:
            - walk_time:      float of time it took to tree walk
            - walk_folders:   list of folders from the tree walk
            - walk_files:     list of files from the tree walk
            - data_size:      total size of all files
    """
    try:
        walk_time, walk_fol, walk_files, data_size = '', [], [], 0
        num_folders, num_files = 0, 0
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
                dir_fp = f'{root}/{d}'
                walk_fol.append(dir_fp)
                num_folders += 1
            # poopulate the file list
            for f in files:
                file_fp = f'{root}/{f}'
                walk_files.append(file_fp)
                # get cumulative file size
                try:
                    f_info = os.stat(file_fp, follow_symlinks=False)
                    data_size += f_info.st_size
                    num_files += 1
                except OSError as e:
                    e_var = (f'Tree walk of source: {args.source}\n{e}')
                    bp([e_var, Ct.RED], erl=2)
        walk_stop = time.monotonic()
        # calculate total tree walk time
        walk_time = (walk_stop - walk_start)
    except OSError as e:
        e_var = f'tree walk failure: {args.source}\n{e}'
        bp([e_var, Ct.RED], erl=2)

    return walk_time, walk_fol, walk_files, data_size, num_folders, num_files


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def create_folder(folder_source: str):
    """Create a folder on each call.

    Args:
        - folder_source (str): the folder to create

    Returns:
        - int: 0 is success; 1 is failure
    """
    # swap the target for the source in the string
    folder_target = folder_source.replace(args.source, args.target)
    try:
        # create the folder
        if not os.path.isdir(folder_target):
            os.makedirs(folder_target)
            # TODO adjust the folder date to match the source
            # TODO adjust the folder permissions to match the source

        return 0, folder_target

    except OSError as e:
        bp([f'create folder - {folder_target}\n\t{e}', Ct.RED], erl=2)

        return 1, folder_target


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def file_multifunction(file_source: str, file_action: str):
    """Copy or read the file with hashing.

    Args:
        - file_source (str): the file to copy or read
        - file_action (str): either 'copy' or 'read'

    Returns:
        - tuple:
            - file_rtime      read file timer
            - file_wtime      write file timer
            - hash_time       hash timer
            - hash_hex        the hash hexadecimal
            - file_target     the target file name
            - file_size       the size of the source file
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
        read_blocks = args.blocksize * options.BLOCK_SIZE_FACTOR
        f_loops = ceil(file_size / read_blocks)
        # target output variable
        t_o = 'wb' if file_action == 'copy' else 'rb'
        # fr is file read, fw is file write, fw open but ignored on read
        with open(file_source, 'rb') as fr, open(file_target, t_o) as fw:
            while True:
                fr_start = time.monotonic()
                # read source in blocks to prevent potential memory overload
                f_chunk = fr.read(read_blocks)
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
        bp([f'{e_var}', Ct.RED], erl=2)

        return 1, file_source


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def main():

    try:
        start_time = datetime.fromtimestamp(START_PROG_TIME)
        bp([f'{options.ver}', Ct.BBLUE, f'\nProgram start: {start_time}\n'
            'Source: ', Ct.A, f'{args.source}', Ct.GREEN, '\nTarget: ', Ct.A,
            f'{args.target}', Ct.GREEN])
        bp(['Args: ', Ct.A], inl=1)
        for k, v in vars(args).items():
            if k != 'source' and k != 'target':
                bp([f' {k}: {v} |', Ct.A], inl=1, log=0)
        bp(['', Ct.A], log=0)
        # execute the tree walk
        tw_tup = tree_walk()
        folder_total = f'{tw_tup[4]:,}'
        file_total = f'{tw_tup[5]:,}'
        file_size_total = decimal_notation(tw_tup[3])
        # print out the tree walk data
        bp([f'Folders: {folder_total} | Files: {file_total} | Size: '
            f'{file_size_total[1]}', Ct.A])
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
                bp([f'Created: {folder_return[1]}', Ct.A], num=0)
            else:
                folder_failure += 1
                bp([f'Failed!: {folder_return[1]}', Ct.RED], erl=2, num=0)
        fo_time_stop = time.monotonic()
        # calculate folder creation time
        folder_time = f'{(fo_time_stop - fo_time_start):,.4f}'
        f_time = fo_time_stop - fo_time_start
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
                bp([f'Copied: {c_stat[5]}', Ct.GREEN], num=0)
            else:
                file_failure += 1
                bp([f'Failed Copy!: {c_stat[1]}', Ct.RED], erl=2)
            # execute target file read and hashing, and gather stats
            r_stat = file_multifunction(f_target, 'read')
            if c_stat[0] == 0 and r_stat[0] == 0:
                fr_rtime += r_stat[1]
                hr_time += r_stat[2]
                if c_stat[4] == r_stat[4]:
                    val_success += 1
                    bp([f'Validated: source & target hex match.\n\t{c_stat[4]}'
                        f'\n\t{r_stat[4]}', Ct.GREEN], num=0)
                else:
                    val_failure += 1
                    bp([f'Source & target hex DO NOT MATCH!\n\t{c_stat[4]}\n\t'
                        f'{r_stat[4]}', Ct.RED], erl=2, num=0)
            else:
                bp([f'Failed reading copied file!: {c_stat[1]}', Ct.RED],
                   erl=2)

        # print out final copy stats
        file_size_success = decimal_notation(file_size_copied)
        file_size_failure = decimal_notation((tw_tup[3] - file_size_copied))
        hex_tot = hc_time + hr_time
        file_tot = int(fc_rtime + fc_wtime)
        bp([f'\n{" " * 16}Source    Target    FAILED         TIME', Ct.A])
        bp([f'      Dirs: {folder_total:>10}{folder_success:>10}'
            f'{folder_failure:>10,}{folder_time:>12s}s', Ct.A])
        bp([f'     Files: {file_total:>10}{file_success:>10}'
           f'{file_failure:>10,}{file_tot:>12,.4f}s', Ct.A])
        bp([f'     Bytes: {file_size_total[1]:>10}{file_size_success[1]:>10}'
           f'{file_size_failure[1]:>10}', Ct.A])
        bp([f'Validation: {file_total:>10}{val_success:>10}'
           f'{val_failure:>10,}{hex_tot:>12,.4f}s (+{fr_rtime:,.4f}s)', Ct.A])
        end_time = time.monotonic()
        total_time = end_time - START_PROG_TIME
        tft = (tw_tup[0] + f_time + fc_rtime + hc_time + fc_wtime +
               fr_rtime + hr_time)
        bp([f'\n{total_time:,.4f}s - Total Time\n{tw_tup[0]:,.4f}s - Tree Walk'
            f' Time\n{folder_time:}s - FolderCreation Time\n{fc_rtime:,.4f}s'
            f' - Source Read Time\n{hc_time:,.4f}s - Source Hash Validation '
            f'Time\n{fc_wtime:,.4f}s - Target Write Time\n{fr_rtime:,.4f}s - '
            f'Target Read Time\n{hr_time:,.4f}s - Target Hash Validation '
            f'Time\n{tft:,.4f}s - Total Function Time\n{"-" * 40}\n'
            f'{total_time - tft:,.4f}s - Program Overhead Time', Ct.A])

    except KeyboardInterrupt:
        bp(['Ctrl+C pressed...\n', Ct.RED], erl=2)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if __name__ == '__main__':

    # create list of available hash algorithms
    hash_list = [i for i in sorted(hashlib.algorithms_guaranteed)]
    # make args global
    args = options.args
    bp([f'{options.ver}: {options.__purpose__}\n', Ct.BBLUE])
    bp([f'calling validate_and_process_args({hash_list}) and assigning back to'
        ' hash_list. Allows for all or just one hash.', Ct.BMAGENTA], veb=2,
        num=0)
    hash_list = validate_and_process_args(hash_list)
    bp([f'calling main({hash_list}).', Ct.BMAGENTA], veb=2, num=0)
    main()
