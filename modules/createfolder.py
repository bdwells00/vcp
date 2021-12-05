

from collections import defaultdict as dd
import os
from modules.ct import Ct
from modules.bp import bp
from modules.monotimer import mono_timer


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
def create_folder(folder_source: str, args):
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


@mono_timer
def folder_logic(folder_list: list, args):
    folder_dict, folder_success, folder_failure = dd(int), 0, 0
    for folder in folder_list:
        # create each folder and get back 0 for success and 1 for error
        folder_return = create_folder(folder, args)
        # populate dict to track success or failure
        folder_dict[folder] = folder_return[0]
        if folder_return[0] == 0:
            folder_success += 1
            bp([f'Created: {folder_return[1]}', Ct.A], num=0)
        else:
            folder_failure += 1
            bp([f'Failed!: {folder_return[1]}', Ct.RED], erl=2, num=0)
    return folder_success, folder_failure
