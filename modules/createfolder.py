

from collections import defaultdict as dd
from pathlib import Path
import shutil
from betterprint.betterprint import bp
from betterprint.colortext import Ct
from modules.timer import perf_timer
from modules.options import args


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
def create_folder(folder_source: str):
    """Create a folder on each call.

    - Args:
        - folder_source (str): the folder to create

    - Returns:
        - int: 0 is success; 1 is failure
        - Path: folder_target
    """
    # ~~~ #                 -variables-
    # need to convert to string to use replace, then back to Path
    f_target = str(folder_source).replace(args.source, args.target)
    folder_target = Path(f_target)

    try:
        # ~~~ #             -folder creation-
        folder_target.mkdir(parents=True, exist_ok=True)
        return 0, folder_target

    except OSError as e:
        bp([f'create folder - {folder_target}\n\t{e}', Ct.RED], err=2)

        return 1, folder_target


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
def stat_copy(f_source: str, f_target: str):
    """Copies the folder details (time, permissions) from source to target.

    - Args:
        - f_source (str): source folder
        - f_target (str): target folder
    """
    shutil.copystat(f_source, f_target, follow_symlinks=False)
    return


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
@perf_timer
def folder_stat_reset(success_dict: dict):
    """After file copies, rerun the stat_copy because on Linux, a file write
    updates the folder time. This will reset it to the source time.

    - Args:
        - success_dict (dict): a dictionary of all folders created
    """
    for k, v in success_dict.items():
        stat_copy(k, v)
    return


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
@perf_timer
def folder_logic(dir_dict: dict):
    """Controller logic for multiple folder creations.

    - Args:
        - dir_dict (dict): a dictionary of all folders to create. The key is
                        the folder, the value is the os.stat of the folder.

    - Returns:
        - dict: return the success and failure stats along with lists of each.
    """
    # ~~~ #         variable section
    return_dict = {
        'success': 0,
        'success_dict': dd(str),
        'failure': 0,
        'failure_dict': dd(str)
    }
    # ~~~ #         dictionary iteration section
    for k, _ in dir_dict.items():
        # create each folder and get back 0 for success or 1 for failure
        folder_return = create_folder(k)
        # populate dict to track success or failure
        if folder_return[0] == 0:
            return_dict['success'] += 1
            return_dict['success_dict'][k] = folder_return[1]
            stat_copy(k, folder_return[1])
            bp([f'Created: {folder_return[1]}', Ct.A], num=0, veb=1)
        else:
            return_dict['failure'] += 1
            return_dict['failure_dict'][k] = folder_return[1]
            bp([f'Failed!: {folder_return[1]}', Ct.RED], err=2, num=0)

    return return_dict
