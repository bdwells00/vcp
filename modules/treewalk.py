

from collections import defaultdict as dd
from pathlib import Path
from betterprint.betterprint import bp
from betterprint.colortext import Ct
from modules.timer import perf_timer
from modules.options import args


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
@perf_timer
def tree_walk():
    """Walk the source folder using pathlib. Populate 3 dicts, a folder dict,
    a file dict, and a stats dict.

    - Returns:
        - [dict]: k: folders; v: size
        - [dict]: k: files; v: size
        - [dict]:
            'file_size'
            'num_dirs'
            'num_files'
    """
    try:
        # ~~~ #             -variables-
        walk_dirs_dict, walk_files_dict = dd(list), dd(list)
        stat_dict = {'file_size': 0, 'num_dirs': 0, 'num_files': 0}
        # create exdir and exfile lists
        if args.exdir:
            exdir = args.exdir.split(',')
        if args.exfile:
            exfile = args.exfile.split(',')
        p = Path(args.source)

        # ~~~ #             -rglob-
        for item in p.rglob('*'):
            if item.is_dir():
                # add folders if no folder exclusions
                if not args.exdir:
                    walk_dirs_dict[item] = item.stat().st_size
                    stat_dict['num_dirs'] += 1
                else:
                    # add folders if the exclusion is not in the folder path
                    for z in exdir:
                        if z not in item:
                            walk_dirs_dict[item] = item.stat().st_size
                            stat_dict['num_dirs'] += 1
            else:
                # add files if no file exclusions
                if not args.exfile:
                    walk_files_dict[item] = item.stat().st_size
                    stat_dict['num_files'] += 1
                    stat_dict['file_size'] += item.stat().st_size
                else:
                    # add files if the exclusion is not in the folder path
                    for z in exfile:
                        if z not in item:
                            walk_files_dict[item] = item.stat().st_size
                            stat_dict['num_files'] += 1
                            stat_dict['file_size'] += item.stat().st_size
    except OSError as e:
        bp([f'tree walk failure: {args.source}\n{e}', Ct.RED], erl=2)

    return walk_dirs_dict, walk_files_dict, stat_dict
