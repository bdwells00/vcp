"""freespace.py v0.0.1"""

from collections import defaultdict as dd
import shutil


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
def free_space(folder):

    vol_bytes = dd(int)
    vol_bytes['total_bytes'], vol_bytes['used_bytes'], vol_bytes['free_bytes']\
        = shutil.disk_usage(folder)
    return vol_bytes
