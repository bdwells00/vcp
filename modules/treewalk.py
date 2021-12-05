

import os
from modules.bp import bp
from modules.ct import Ct
from modules.monotimer import mono_timer
from modules.options import args


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
def tree_walk_error_output(os_error: str):
    """Receive errors from tree_walk function, color red, then send to output
    either just log file or both log and elog files.

    Args:
        - os_error (str): os.walk onerror output
    """
    bp([os_error, Ct.RED], erl=2)

    return


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
@mono_timer
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
        walk_fol, walk_files, data_size = [], [], 0
        num_folders, num_files = 0, 0
        # create exdir and exfile lists
        if args.exdir:
            exdir = args.exdir.split(',')
        if args.exfile:
            exfile = args.exfile.split(',')
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
    except OSError as e:
        e_var = f'tree walk failure: {args.source}\n{e}'
        bp([e_var, Ct.RED], erl=2)

    return 101, walk_fol, walk_files, data_size, num_folders, num_files
