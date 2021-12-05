#!/usr/bin/python3-64 -X utf8


from datetime import datetime
import hashlib
import sys
import time
from modules.bp import bp
from modules.bytenote import byte_notation
from modules.createfolder import folder_logic
from modules.ct import Ct
from modules.multifile import file_multifunction
import modules.options as options
import modules.treewalk
START_PROG_TIME = time.monotonic()


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
def main():

    try:
        start_time = datetime.fromtimestamp(START_PROG_TIME)
        bp([f'{options.ver}', Ct.BBLUE, f'\nProgram start: {start_time}\n'
            'Source: ', Ct.A, f'{args.source}', Ct.GREEN, '\nTarget: ', Ct.A,
            f'{args.target}', Ct.GREEN])
        bp(['Args: ', Ct.A], inl=1)
        for k, v in vars(args).items():
            if k != 'source' and k != 'target':
                bp([f' {k}: {v} |', Ct.A], inl=1, log=0)
        bp(['', Ct.A], log=0)
        # execute the tree walk
        tw_timer = modules.treewalk.tree_walk()
        tw_tup = tw_timer[2]
        folder_total = f'{tw_tup[4]:,}'
        file_total = f'{tw_tup[5]:,}'
        file_size_total = byte_notation(tw_tup[3])
        # print out the tree walk data
        bp([f'Folders: {folder_total} | Files: {file_total} | Size: '
            f'{file_size_total[1]}', Ct.A])

        folder_return = folder_logic(tw_tup[1], args)
        print(folder_return)

        f_time = folder_return[1]
        folder_time = f'{f_time:,.4f}'
        folder_success = folder_return[2][0]
        folder_failure = folder_return[2][1]
        # variables for file processing
        fc_rtime, fc_wtime, hc_time, fr_rtime, hr_time = 0, 0, 0, 0, 0
        file_success, file_failure, file_size_copied = 0, 0, 0
        val_success, val_failure = 0, 0
        # copy each file and validate it with stats
        # TODO add confirmation for file copy and read
        for file in tw_tup[2]:
            # execute file creation and hashing, and gather stats
            c_stat = file_multifunction(file, 'copy')
            if c_stat[0] == 0:
                file_success += 1
                fc_rtime += c_stat[1]
                fc_wtime += c_stat[2]
                hc_time += c_stat[3]
                f_target = c_stat[5]
                file_size_copied += c_stat[6]
                bp([f'Copied: {c_stat[5]}', Ct.GREEN], num=0)
            else:
                file_failure += 1
                bp([f'Failed Copy!: {c_stat[1]}', Ct.RED], erl=2)
            # execute target file read and hashing, and gather stats
            r_stat = file_multifunction(f_target, 'read')
            if c_stat[0] == 0 and r_stat[0] == 0:
                fr_rtime += r_stat[1]
                hr_time += r_stat[2]
                if c_stat[4] == r_stat[4]:
                    val_success += 1
                    bp([f'Validated: source & target hex match.\n\t{c_stat[4]}'
                        f'\n\t{r_stat[4]}', Ct.GREEN], num=0)
                else:
                    val_failure += 1
                    bp([f'Source & target hex DO NOT MATCH!\n\t{c_stat[4]}\n\t'
                        f'{r_stat[4]}', Ct.RED], erl=2, num=0)
            else:
                bp([f'Failed reading copied file!: {c_stat[1]}', Ct.RED],
                   erl=2)

        # print out final copy stats
        file_size_success = byte_notation(file_size_copied)
        file_size_failure = byte_notation((tw_tup[3] - file_size_copied))
        hex_tot = hc_time + hr_time
        file_tot = int(fc_rtime + fc_wtime)
        bp([f'\n{" " * 16}Source    Target    FAILED         TIME', Ct.A])
        bp([f'      Dirs: {folder_total:>10}{folder_success:>10}'
            f'{folder_failure:>10,}{folder_time:>12s}s', Ct.A])
        bp([f'     Files: {file_total:>10}{file_success:>10}'
           f'{file_failure:>10,}{file_tot:>12,.4f}s', Ct.A])
        bp([f'     Bytes: {file_size_total[1]:>10}{file_size_success[1]:>10}'
           f'{file_size_failure[1]:>10}', Ct.A])
        bp([f'Validation: {file_total:>10}{val_success:>10}'
           f'{val_failure:>10,}{hex_tot:>12,.4f}s (+{fr_rtime:,.4f}s)', Ct.A])
        end_time = time.monotonic()
        total_time = end_time - START_PROG_TIME
        tft = (tw_timer[1] + f_time + fc_rtime + hc_time + fc_wtime +
               fr_rtime + hr_time)
        bp([f'\n{total_time:,.4f}s - Total Time\n{tw_timer[1]:,.4f}s - Tree Wa'
            f'lk Time\n{folder_time:}s - FolderCreation Time\n{fc_rtime:,.4f}s'
            f' - Source Read Time\n{hc_time:,.4f}s - Source Hash Validation '
            f'Time\n{fc_wtime:,.4f}s - Target Write Time\n{fr_rtime:,.4f}s - '
            f'Target Read Time\n{hr_time:,.4f}s - Target Hash Validation '
            f'Time\n{tft:,.4f}s - Total Function Time\n{"-" * 40}\n'
            f'{total_time - tft:,.4f}s - Program Overhead Time', Ct.A])

    except KeyboardInterrupt:
        bp(['Ctrl+C pressed...\n', Ct.RED], erl=2)
        sys.exit(1)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
if __name__ == '__main__':

    # ~~~ #         title section
    bp([f'{options.ver}: {options.purpose}\n', Ct.BBLUE])
    # ~~~ #         args section
    args = options.args
    # create list of available hash algorithms
    hash_list = [i for i in sorted(hashlib.algorithms_guaranteed)]
    bp([f'calling options.execute_args_validation({hash_list}).', Ct.BMAGENTA],
        veb=2, num=0)
    arg_val = options.execute_args_validation(hash_list)
    if arg_val[0] != 2:
        bp([f'{arg_val[1]}', arg_val[2]], num=arg_val[3], erl=[arg_val[4]])
        sys.exit(arg_val[0])
    # ~~~ #         main section
    bp([f'calling main({hash_list}).', Ct.BMAGENTA], veb=2, num=0)
    main()
