#!/usr/bin/python3-64 -X utf8


from datetime import datetime
import sys
from time import perf_counter
from modules.bp import bp
from modules.bytenote import byte_notation
from modules.createfolder import folder_logic
from modules.ct import Ct
from modules.freespace import free_space
from modules.multifile import file_logic
import modules.options as options
import modules.treewalk
START_PROG_TIME = perf_counter()


start_time = datetime.now()


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
def main():

    try:
        # ~~~ #         initial display section
        bp([f'\t{options.copyright}\n\t{options.license_info}\n{"━" * 40}',
            Ct.A], veb=2)
        bp([f'Program start: {start_time}\nSource: ', Ct.A, f'{args.source}',
            Ct.GREEN, '\nTarget: ', Ct.A, f'{args.target}\n', Ct.GREEN,
            'Excluded Folders: ', Ct.A, f'{args.exdir}\n', Ct.GREEN, 'Excluded'
            ' Files: ', Ct.A, f'{args.exfile}', Ct.GREEN])
        bp(['Args: ', Ct.A], inl=1)
        for k, v in vars(args).items():
            if k != 'source' and k != 'target' and k != 'exdir' and k != \
                    'exfile' and k != 'available':
                if k == 'hash':
                    bp([f' {k}: ', Ct.A, f'{v}', Ct.RED, ' |', Ct.A], num=0,
                        inl=1, log=0)
                else:
                    bp([f' {k}: {v} |', Ct.A], inl=1, log=0)
        bp([f'\n\n{"━" * 40}\n', Ct.A], log=0)
        # ~~~ #         tree walk section
        tree_return = modules.treewalk.tree_walk()
        tw_tup = tree_return[2]
        folder_total = f'{tw_tup[4]:,}'
        file_total = f'{tw_tup[3]:,}'
        file_size_total = byte_notation(tw_tup[2], ntn=1)
        # ~~~ #         free space section
        target_space = free_space(args.target)
        target_space_bytenote = byte_notation(target_space['free_bytes'],
                                              ntn=1)
        # print out the tree walk data
        bp([f'Source - Size: {file_size_total[1]} | Folders: '
            f'{folder_total} | Files: {file_total}\nTarget - Free: '
            f'{target_space_bytenote[1]}', Ct.A])
        if tw_tup[2] >= target_space['free_bytes']:
            bp(['not enough free space to copy all the data.', Ct.RED], erl=2)
            sys.exit(1)
        bp([f'\n{"━" * 40}\n', Ct.A], log=0)
        # ~~~ #         folder creation section
        folder_return = folder_logic(tw_tup[0])

        f_time = folder_return[1]
        folder_time = f'{f_time:,.4f}'
        folder_success = folder_return[2]['success']
        folder_failure = folder_return[2]['failure']
        # ~~~ #         file creation section
        file_return = file_logic(tw_tup[1])

        file_size_success = byte_notation(file_return["val_size"], ntn=1)
        file_size_failure = byte_notation(tw_tup[2] - file_return["val_size"],
                                          ntn=1)
        hex_tot = file_return["hash_time"] + file_return["val_hash_time"]
        file_tot = int(file_return['read_time'] + file_return["write_time"])
        # ~~~ #         final display section
        bp([f'\n{" " * 16}Source    Target    FAILED         TIME', Ct.A])
        bp([f'      Dirs: {folder_total:>10}{folder_success:>10,}'
            f'{folder_failure:>10,}{folder_time:>12s}s', Ct.A])
        bp([f'     Files: {file_total:>10}{file_return["success"]:>10,}'
           f'{file_return["failure"]:>10,}{file_tot:>12,.4f}s', Ct.A])
        bp([f'     Bytes: {file_size_total[1]:>10}{file_size_success[1]:>10}'
           f'{file_size_failure[1]:>10}', Ct.A])
        bp([f'Validation: {file_total:>10}{file_return["val_success"]:>10,}'
            f'{file_return["val_failure"]:>10,}{hex_tot:>12,.4f}s (+'
            f'{file_return["val_read_time"]:,.4f}s)', Ct.A])
        end_time = perf_counter()
        total_time = end_time - START_PROG_TIME
        tft = (tree_return[1] + f_time + file_return["read_time"] +
               file_return["hash_time"] + file_return["write_time"] +
               file_return["val_read_time"] + file_return["val_hash_time"])
        bp([f'\n{total_time:,.4f}s - Total Time\n{tree_return[1]:,.4f}s - Tree'
            f' Walk Time\n{folder_time:}s - FolderCreation Time\n'
            f'{file_return["read_time"]:,.4f}s - Source Read Time\n'
            f'{file_return["hash_time"]:,.4f}s - Source Hash Validation Time\n'
            f'{file_return["write_time"]:,.4f}s - Target Write Time\n'
            f'{file_return["val_read_time"]:,.4f}s - Target Read Time\n'
            f'{file_return["val_hash_time"]:,.4f}s - Target Hash Validation '
            f'Time\n{tft:,.4f}s - Total Function Time\n{"━" * 40}\n'
            f'{total_time - tft:,.4f}s - Program Overhead Time', Ct.A])

    except KeyboardInterrupt:
        bp(['Ctrl+C pressed...\n', Ct.RED], erl=2)
        sys.exit(1)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
if __name__ == '__main__':

    # ~~~ #         title section
    bp([f'{options.ver} - {options.purpose}\n', Ct.BBLUE])
    # ~~~ #         args section
    args = options.args
    bp(['calling options.execute_args_validation().', Ct.BMAGENTA],
        veb=2, num=0)
    arg_val = options.execute_args_validation()
    if arg_val['exit'] != 10:
        bp(arg_val['bp_list'], num=arg_val['bp_num'], erl=arg_val['bp_erl'])
        sys.exit(arg_val['exit'])
    # ~~~ #         main section
    bp(['calling main().', Ct.BMAGENTA], veb=2, num=0)
    main()
