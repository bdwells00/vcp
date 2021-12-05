

import hashlib
from math import ceil
import os
from modules.ct import Ct
from modules.bp import bp
from modules.monotimer import mono_timer
from modules.options import args, BLOCK_SIZE_FACTOR


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
@mono_timer
def file_read(file_handle, file_blocks):
    return file_handle.read(file_blocks)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
@mono_timer
def file_write(file_handle, file_blocks):
    return file_handle.write(file_blocks)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
@mono_timer
def hash_processing(hlib, hash_action, file_blocks=0):
    if hash_action == 'update':
        hash_upd = hlib.update(file_blocks)
        return hash_upd
    elif hash_action == 'hex':
        # convert the hash to hexadecimal
        if 'shake' in args.hash:
            return hlib.hexdigest(args.length)
        else:
            return hlib.hexdigest()


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
def file_multi(file_action: str, file_source: str):
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
    # hashlib function variable
    hlib_var = (getattr(hashlib, args.hash)())
    # swap the target for the source in the string
    file_target = file_source.replace(args.source, args.target)
    file_rtime, file_wtime, file_size, hash_time = 0, 0, 0, 0
    try:
        read_blocks = args.blocksize * BLOCK_SIZE_FACTOR
        # get the size of the file copied or read
        f_info = os.stat(file_source, follow_symlinks=False)
        file_size = f_info.st_size
        file_loop = 0
        f_loops = ceil(file_size / read_blocks)
        update_loop = 1 if f_loops < 100 else int(f_loops / 100)
        # target output variable
        t_o = 'wb' if file_action == 'copy' else 'rb'
        # fr is file read, fw is file write, fw open but ignored on read
        with open(file_source, 'rb') as fr, open(file_target, t_o) as fw:
            while True:
                # read source in blocks to prevent potential memory overload
                f_chunk = file_read(fr, read_blocks)
                file_rtime += f_chunk[1]
                # this breaks the while loop when no more file chunks to read
                if not f_chunk[2]:
                    if args.verbose == 3:
                        print()
                    break
                # update the hash on each chunk
                hash_temp = hash_processing(hlib_var, 'update', f_chunk[2])
                hash_time += hash_temp[1]
                # skip this section on read hashing, otherwise copy the file
                if file_action == 'copy':
                    f_write_return = file_write(fw, f_chunk[2])
                    file_wtime += f_write_return[1]
                # loop and stdout print a status of the current file processing
                file_loop += 1
                if file_loop % update_loop == 0:
                    bp([f'\u001b[1000D{(file_loop / f_loops) * 100:.0f}%',
                        Ct.BBLUE, ' | ', Ct.A, f'{file_source}', Ct.GREEN],
                        inl=1, num=0, fls=1)
            bp(['', Ct.A])
            hash_temp = hash_processing(hlib_var, 'hex')
            hash_time += hash_temp[1]

        return (0, file_rtime, file_wtime, hash_time, hash_temp[2],
                file_target, file_size)

    except OSError as e:
        e_var = (f'with file {file_action}: {file_source}\n{e}')
        bp([f'{e_var}', Ct.RED], erl=2)

        return 1, file_source


def file_logic(file_list):
    # variables for file processing
    file_dict = {
        'success': 0,
        'success_source_list': [],
        'success_target_list': [],
        'failure': 0,
        'failure_list': [],
        'read_time': 0.0,
        'write_time': 0.0,
        'hash_time': 0.0,
        'hash_source_list': [],
        'read_size': 0,
        'val_success': 0,
        'val_success_list': [],
        'val_failure': 0,
        'val_failure_list': [],
        'val_read_time': 0.0,
        'val_hash_time': 0.0,
        'val_hash_list': [],
        'val_size': 0
    }
    # copy each file and validate it with stats
    for file in file_list:
        # execute file creation and hashing, and gather stats
        copy_return = file_multi('copy', file)
        if copy_return[0] == 0:
            file_dict['success'] += 1
            file_dict['success_source_list'].append(file)
            file_dict['read_time'] += copy_return[1]
            file_dict['write_time'] += copy_return[2]
            file_dict['hash_time'] += copy_return[3]
            file_dict['hash_source_list'].append(copy_return[4])
            file_dict['success_target_list'].append(copy_return[5])
            file_dict['read_size'] += copy_return[6]
            bp([f'Copied: {file_dict["success_source_list"][-1]}', Ct.GREEN],
                num=0, veb=1)
        else:
            file_dict['failure'] += 1
            file_dict['failure_list'].append(file)
            bp([f'Failed Copy!: {file_dict["failure_list"][-1]}', Ct.RED],
                erl=2)
        # execute target file read and hashing, and gather stats
        val_return = file_multi('read', copy_return[5])
        if copy_return[0] == 0 and val_return[0] == 0:
            file_dict['val_read_time'] += val_return[1]
            file_dict['val_hash_time'] += val_return[3]
            file_dict['val_hash_list'].append(val_return[4])
            if copy_return[4] == val_return[4]:
                file_dict['val_success'] += 1
                file_dict['val_success_list'].append(val_return[5])
                file_dict['val_size'] += val_return[6]
                bp([f'Validated: source & target hex match.\n\t'
                    f'{copy_return[4]}\n\t{val_return[4]}', Ct.GREEN], num=0,
                    veb=1)
            else:
                file_dict['val_failure'] += 1
                file_dict['val_failure_list'].append(val_return[5])
                bp([f'Source & target hex DO NOT MATCH!\n\t{copy_return[4]}'
                    f'\n\t{val_return[4]}', Ct.RED], erl=2, num=0)
        else:
            file_dict['val_failure'] += 1
            file_dict['val_failure_list'].append(copy_return[5])
            bp([f'Failed reading copied file!: {copy_return[5]}', Ct.RED],
                erl=2)
    return file_dict
