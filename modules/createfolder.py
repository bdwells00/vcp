

import os
from modules.ct import Ct
from modules.bp import bp
from modules.timer import perf_timer
from modules.options import args


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
def create_folder(folder_source: str):
    """Create a folder on each call.

    Args:
        - folder_source (str): the folder to create

    Returns:
        - int: 0 is success; 1 is failure
    """
    # ~~~ #         variable section
    folder_target = folder_source.replace(args.source, args.target)
    try:
        # ~~~ #     folder creation section
        if not os.path.isdir(folder_target):
            os.makedirs(folder_target)

        return 0, folder_target

    except OSError as e:
        bp([f'create folder - {folder_target}\n\t{e}', Ct.RED], erl=2)

        return 1, folder_target


@perf_timer
def folder_logic(dir_dict: dict):
    """Controller logic for multiple folder creations.

    Args:
        dir_dict (dict): a dictionary of all folders to create. The key is the
                         folder, the value is the os.stat of the folder.

    Returns:
        dict: return the success and failure stats along with lists of each.
    """
    # ~~~ #         variable section
    return_dict = {
        'success': 0,
        'success_list': [],
        'failure': 0,
        'failure_list': []
    }
    # ~~~ #         dictionary iteration section
    for k, v in dir_dict.items():
        # create each folder and get back 0 for success or 1 for failure
        folder_return = create_folder(k)
        # populate dict to track success or failure
        if folder_return[0] == 0:
            return_dict['success'] += 1
            return_dict['success_list'].append(folder_return[1])
            bp([f'Created: {folder_return[1]}', Ct.A], num=0, veb=1)
        else:
            return_dict['failure'] += 1
            return_dict['failure_list'].append(folder_return[1])
            bp([f'Failed!: {folder_return[1]}', Ct.RED], erl=2, num=0)

    return return_dict
