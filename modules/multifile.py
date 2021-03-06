

from datetime import timedelta
import hashlib
from math import ceil
from pathlib import Path
import shutil
from betterprint.betterprint import bp
from betterprint.colortext import Ct
from modules.notations import byte_notation
from modules.timer import perf_timer
from modules.options import args, BLOCK_SIZE_FACTOR


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
@perf_timer
def file_read(file_handle, file_blocks):
    """A simple function to read a part of a file in chunks. It is decorated
    with a timer to track duration.

    - Args:
        - file_handle (file): the open file to read
        - file_blocks (file): the size in bytes to read

    - Returns:
        - [file]: returns the read blocks
    """
    return file_handle.read(file_blocks)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
@perf_timer
def file_write(file_handle, file_blocks):
    """A simple function to write a part of a file in chunks. It is decorated
    with a timer to track duration.

    - Args:
        - file_handle (file): the open file to write
        - file_blocks (file): the data to write

    - Returns:
        - [file]: returns the written blocks
    """
    return file_handle.write(file_blocks)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
@perf_timer
def hash_processing(hash_action, hlib, file_blocks=0):
    """This hashes a block of a file (or whole file if small enough). The
    hashlib must be passed back and forth to maintain a single, consistant
    hashlib to update for files bigger than the block size. This will also
    generate a hexadecimal output of a hashlib.

    - Args:
        - hlib (hashlib): the hashlib to update
        - hash_action (str): either 'update' to runs hashlib.update or 'hex' to
                             run hashlib.hexdigest.
        - file_blocks (int, optional): required for hash_action of 'update';
                                       the data to hash. Defaults to 0.

    - Returns:
        - [hashlib]: for 'update' hash action, returns an updated hashlib
                     object,for 'hex' hash action, returns a hexadecimal
                     string.
    """
    # ~~~ #                 -update-
    if hash_action == 'update':
        hash_upd = hlib.update(file_blocks)
        return hash_upd

    # ~~~ #                 -hex-
    elif hash_action == 'hex':
        if 'shake' in args.hash:
            return hlib.hexdigest(args.length)
        else:
            return hlib.hexdigest()


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
@perf_timer
def stat_copy(f_source: str, f_target: str):
    """Copies the file details (time, permissions) from source to target.

    - Args:
        - f_source (str): source file
        - f_target (str): target file
    """
    shutil.copystat(f_source, f_target, follow_symlinks=False)
    return


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
def file_multi(file_action: str, file_source: Path):
    """The main file read, write, and validation actions run from here.

    - Args:
        - file_action (str): either 'copy' or 'read'
        - file_source (str): the file to copy or read
    - Returns:
        - [tuple]: 12 k/v pair dict of actions taken, status, and output
    """
    # ~~~ #         variable section
    # this var must be passed to other functions and back to maintain integrity
    hlib_var = (getattr(hashlib, args.hash)())
    # need to convert to string to use replace, then back to Path
    f_source = str(file_source)
    f_target = f_source.replace(args.source, args.target)
    # dict to hold various updates for single return var
    fm_dict = {
        'failure': 0,
        'file_action': file_action,
        'file_source': file_source,
        'short_source': (f_source if len(f_source) < 63 else
                         f'...{f_source[(len(f_source) - 60):]}'),
        'file_target': Path(f_target),
        'read_blocks': args.blocksize * BLOCK_SIZE_FACTOR,
        'file_info': file_source.stat(follow_symlinks=False),
        'file_size': file_source.stat(follow_symlinks=False).st_size,
        'file_read_time': 0.0,
        'file_write_time': 0.0,
        'hash_time': 0.0,
        'hash_hex': ''
    }
    file_loop = 0
    # number of loops to execute
    file_loops = ceil(fm_dict['file_size'] / fm_dict['read_blocks'])
    # limit cli output to max of 100 loops to prevent slowdown
    update_loop = 1 if file_loops < 100 else int(file_loops / 100)
    # target open variable prevents overwriting target on read actions
    target_open = 'wb' if file_action == 'copy' else 'rb'
    # ~~~ #         file manipulation section
    try:
        # fr is file read, fw is file write; fw is opened but ignored on 'read'
        with open(fm_dict['file_source'], 'rb') as fr,\
             open(fm_dict['file_target'], target_open) as fw:
            while True:
                # read source in blocks to prevent potential memory overload
                f_chunk = file_read(fr, fm_dict['read_blocks'])
                fm_dict['file_read_time'] += f_chunk[1]
                # this breaks the while loop when file chunk is empty
                if not f_chunk[2]:
                    # bp([f'Source: {fm_dict["file_source"]}\nTarget: '
                    #     f'{fm_dict["file_target"]}', Ct.A], con=0)
                    break
                # update the hash on each chunk
                hash_return = hash_processing('update', hlib_var, f_chunk[2])
                fm_dict['hash_time'] += hash_return[1]
                # skip this section on read hashing, otherwise copy the file
                if file_action == 'copy':
                    write_return = file_write(fw, f_chunk[2])
                    fm_dict['file_write_time'] += write_return[1]
                # loop and stdout print a status of the current file processing
                file_loop += 1
                if file_loop % update_loop == 0:
                    bp([f'\u001b[1000D{(file_loop / file_loops) * 100:.0f}%',
                        Ct.BBLUE, ' | ', Ct.A, f'{fm_dict["short_source"]}',
                        Ct.GREEN], log=0, inl=1, num=0, fls=1, fil=0, veb=1)
            bp(['', Ct.A], fil=0, veb=1)
            hash_return = hash_processing('hex', hlib_var)
            fm_dict['hash_time'] += hash_return[1]
            fm_dict['hash_hex'] = hash_return[2]
        return fm_dict

    except OSError as e:
        bp([f'with file {file_action}: {file_source}\n{e}', Ct.RED], err=2)
        fm_dict['failure'] = 1
        return fm_dict


def file_logic(file_dict: dict, stats_dict: dict):
    """The controller for the file_multi section. This initiates copies and
    validates the returns.

    Args:
        file_dict (dict): dict of files as keys and os.stat list as values

    Returns:
        [dict]: 18 k/v pairs on the results of all actions taken
    """
    # ~~~ #             variables section
    num_files = stats_dict["num_files"]
    size_files = stats_dict["file_size"]
    # sets console output variable according to requested quiet variable
    c_tmp = 0 if args.quiet else 1
    # total duration var only used here
    t_var = 0
    fr_dict = {
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
    # ~~~ #             file processing section
    # set initial space if verbose = 0
    if args.verbose == 0:
        bp(['Copy files...\n'
            '  Processed: ', Ct.A, '0', Ct.BBLUE, '/', Ct.A,
            f'{num_files}\n', Ct.BBLUE, '    Success: ', Ct.A, '0', Ct.BBLUE,
            '/', Ct.A, f'{num_files}\n', Ct.BBLUE, '    Failure: ', Ct.A,
            '0', Ct.BBLUE, '/', Ct.A, f'{num_files}\n', Ct.BBLUE,
            ' Val. Files: ', Ct.A, '0', Ct.BBLUE, '/', Ct.A, f'{num_files}',
            Ct.BBLUE, '\n     Size: ', Ct.A, '0', Ct.BBLUE, '/', Ct.A,
            f'{size_files}', Ct.BBLUE, '\n   Duration: ', Ct.A, '00:00:00',
            Ct.BBLUE, '\n Total Time: ', Ct.A, '00:00:00\n', Ct.BBLUE,
            'Total Speed: ', Ct.A, '0\n', Ct.BBLUE], log=0, inl=1, num=0,
            fil=0)
    for file in file_dict:
        # ~~~ #         file copy section
        # set 6 row status since file copies hidden
        copy_return = file_multi('copy', file)
        if copy_return['failure'] == 0:
            fr_dict['success'] += 1
            fr_dict['success_source_list'].append(file)
            fr_dict['read_time'] += copy_return['file_read_time']
            fr_dict['write_time'] += copy_return['file_write_time']
            fr_dict['hash_time'] += copy_return['hash_time']
            fr_dict['hash_source_list'].append(copy_return['hash_hex'])
            fr_dict['success_target_list'].append(copy_return['file_target'])
            fr_dict['read_size'] += copy_return['file_size']
            bp([f'Copied: {file}', Ct.GREEN], num=0, veb=1)
        elif copy_return['failure'] == 1:
            fr_dict['failure'] += 1
            fr_dict['failure_list'].append(file)
            bp([f'Failed Copy!: {file}', Ct.RED], err=2, con=c_tmp)
        else:
            bp([f'Unknown return: {copy_return["failure"]}.\n'
                f'{copy_return}', Ct.RED], err=2, num=0, con=c_tmp)
        # interim update for processed, success, and failure
        if args.verbose == 0:
            bp(['\u001b[100D\u001b[8A', Ct.A], log=0, inl=1, num=0, fil=0)
            # bp(['', Ct.A], log=0, inl=1, num=0, fil=0)
            bp(['  Processed: ', Ct.A,
                f'{fr_dict["success"] + fr_dict["failure"]}', Ct.BBLUE, '/',
                Ct.A, f'{num_files}', Ct.BBLUE], inl=0, log=0, num=0, fil=0)
            bp(['    Success: ', Ct.A, f'{fr_dict["success"]}', Ct.BBLUE, '/',
                Ct.A, f'{num_files}', Ct.BBLUE], inl=0, log=0, num=0, fil=0)
            bp(['    Failure: ', Ct.A, f'{fr_dict["failure"]}', Ct.BBLUE, '/',
                Ct.A, f'{num_files}', Ct.BBLUE], inl=0, log=0, num=0, fil=0)
        # ~~~ #         file stat section
        stat_return = stat_copy(file, copy_return['file_target'])
        fr_dict['write_time'] += stat_return[1]
        # ~~~ #         file validation section
        val_return = file_multi('read', copy_return['file_target'])
        if copy_return['failure'] == 0 and val_return['failure'] == 0:
            fr_dict['val_read_time'] += val_return['file_read_time']
            fr_dict['val_hash_time'] += val_return['hash_time']
            fr_dict['val_hash_list'].append(val_return['hash_hex'])
            if copy_return['hash_hex'] == val_return['hash_hex'] and\
                    copy_return['file_size'] == val_return['file_size']:
                fr_dict['val_success'] += 1
                fr_dict['val_success_list'].append(val_return['hash_hex'])
                fr_dict['val_size'] += val_return['file_size']
                bp(['Validated: source & target hex match.\n\t', Ct.GREEN,
                    f'{copy_return["hash_hex"]}\n\t{val_return["hash_hex"]}',
                    Ct.A], num=0, veb=1)
            else:
                fr_dict['val_failure'] += 1
                fr_dict['val_failure_list'].append(val_return["file_target"])
                bp([f'Source & target hex DO NOT MATCH!\n\t'
                    f'{copy_return["hash_hex"]}\n\t{val_return["hash_hex"]}',
                    Ct.RED], err=2, num=0, con=c_tmp)
        else:
            fr_dict['val_failure'] += 1
            fr_dict['val_failure_list'].append(copy_return['file_target'])
            bp(['Failed reading copied file!: ',
                f'{copy_return["file_target"]}', Ct.RED], err=2, con=c_tmp)
        # interim update for alidated, size, and duration
        t_var = (fr_dict['read_time'] + fr_dict['write_time'] +
                 fr_dict['hash_time'] + fr_dict['val_read_time'] +
                 fr_dict['val_hash_time'])
        sp_var = fr_dict["val_size"] / t_var
        tot_var = size_files / sp_var
        td_t_var = timedelta(seconds=ceil(t_var))
        td_tot_var = timedelta(seconds=ceil(tot_var))
        if args.verbose == 0:
            bp([' Val. Files: ', Ct.A, f'{fr_dict["val_success"]}', Ct.BBLUE,
                '/', Ct.A, f'{num_files}', Ct.BBLUE], inl=0, log=0, num=0,
                fil=0)
            bp(['\u001b[100D  Val. Size: ', Ct.A,
                f'{byte_notation(fr_dict["val_size"], ntn=1)[1]}', Ct.BBLUE,
                '/', Ct.A, f'{byte_notation(size_files, ntn=1)[1]}        ',
                Ct.BBLUE], inl=0, log=0, num=0, fil=0)
            bp(['\u001b[100D   Duration: ', Ct.A, f'{td_t_var}      ',
                Ct.BBLUE], inl=0, log=0, num=0, fil=0)
            bp(['\u001b[100D Total Time: ', Ct.A, f'{td_tot_var}      ',
                Ct.BBLUE], inl=0, log=0, num=0, fil=0)
            bp(['\u001b[100DTotal Speed: ', Ct.A,
                f'{byte_notation(int(sp_var), ntn=1)[1]}',
                Ct.BBLUE, '/s      ', Ct.A], inl=0, log=0, num=0, fil=0, fls=1)
    if args.verbose == 0:
        bp(['', Ct.A], fil=0)
    return fr_dict
