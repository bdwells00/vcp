

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
def hex_processing(hash_action, file_blocks=0):
    # hashlib function variable
    hlib_var = (getattr(hashlib, args.hash)())
    if hash_action == 'update':
        hlib_var.update(file_blocks)
        return
    elif hash_action == 'hex':
        # convert the hash to hexadecimal
        if 'shake' in args.hash:
            return hlib_var.hexdigest(args.length)
        else:
            return hlib_var.hexdigest()


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
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
                hash_temp = hex_processing('update', f_chunk[2])
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
            hash_temp = hex_processing('hex')
            hash_time += hash_temp[1]

        return (0, file_rtime, file_wtime, hash_time, hash_temp[2],
                file_target, file_size)

    except OSError as e:
        e_var = (f'with file {file_action}: {file_source}\n{e}')
        bp([f'{e_var}', Ct.RED], erl=2)

        return 1, file_source
