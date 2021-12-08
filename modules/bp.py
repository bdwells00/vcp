#!/usr/bin/python3-64 -X utf8
'''bp version 0.2.2'''


from datetime import datetime
import os
import sys
from modules.ct import Ct
import modules.options as options


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
def bp(txt: list, con=1, erl=0, fil=1, fls=0, inl=0, log=1, num=1, veb=0):
    """Better Print: send output commands here instead of using print command.
    Txt must be sent in the form of pairs of strings in a list. The even
    strings ("0", "2", "4", etc.) contain the output text while the odd strings
    ("1", "3", "5", etc.) contain the color companion that defines the color
    to be applied to the preceding string. There are pre-defined defaults that
    can be overwritten but not required.

    Example:
        - bp(['Hello', Ct.RED, 'world', Ct.A, '!', Ct.GREEN], veb=2)
            - This prints "Hello world!" with the Hello in red, world in
            terminal default color, and the bang in green. This will also only
            print if args.verbose is set to "2" via "-vv".

    Args:
        - txt (list): (required) must be pairs with the even entries a string
                      and odd sections the Ct.color to apply to that string.
        - con  (int): (optional) 0 = no console output, 1 = console output.
                      (default)
        - erl  (int): (optional) 0 = none (default), 1 = WARNING, 2 = ERROR:
                      auto pre-pends ERROR: or WARNING:, colors line Red, and
                      allows routing of only these to error log if requested.
        - fil  (int): (optional) 0 = off, 1 (default)= on: setting zero skips
                      file output even if args requested.
        - fls  (int): (optional) 0 = off (default), 1 = on: flush the text
                      instead of holding on to it. Usually required for in-
                      line text (inl=1) to force output without an end-of-line.
        - inl  (int): (optional) 0 = off (default); 1 = on: text written in-
                      line with no end-of-line character. Make sure to invoke
                      eol with a final bp before moving on.
        - log  (int): (optional) 0 = off; 1 = on (default): allow pre-pend of
                      each print statement with the date. Can be turned off for
                      things like progress bars and % updates.
        - num  (int): (optional) 0 = off; 1 = on (default): print blue numbers
        - veb  (int): (optional) 0-3: value is used to print only as much as
                      requested.

    Return:
        - None
    """
    # ~~~ #     variables section
    # local variables - txt_tmp gets colored, file_tmp does not
    txt_out, file_out = '', ''
    # if bp added to script, use script vars, else use ga module vars
    if __name__ == '__main__':
        global args
        global print_tracker
    else:
        args = options.args
        print_tracker = options.print_tracker
    # this provides an empty dict of args in case no args
    args_dict = vars(options.args) if 'args' in globals() else {}

    # print(args_dict)
    # ~~~ #     validate verbosity
    # if verbose not implemented, print everything
    if 'verbose' in args_dict:
        # if error logging set, veb ignored and will be printed
        if args_dict['verbose'] < veb and erl == 0:
            con = 0      # skip console output but allow file output if desired

    # ~~~ #     validate txt list - verify it is in pairs
    txt_l = len(txt)
    if txt_l % 2 != 0:
        raise Exception(f'{Ct.RED}"Better Print" function (bp) -> "txt: (list)'
                        f'": must be in pairs (txt length = {txt_l}){Ct.A}')

    # ~~~ #     veb section - prepend INFO-L(x) to each output with verbose
    if veb > 0 and erl == 0 and log == 0:
        txt_out = f'INFO-L{veb}: '
        file_out = f'INFO-L{veb}: '

    # ~~~ #     error section - pre-pend Error or Warning
    # this overwrites veb section as errors and warnings take precedence
    if erl == 1:
        txt_out = f'{Ct.YELLOW}WARNING: {Ct.A}'
        file_out = 'WARNING: '
    elif erl == 2:
        txt_out = f'{Ct.RED}ERROR: {Ct.A}'
        file_out = 'ERROR: '

    # ~~~ #     colorize and assemble section
    # need enumerate to identify even entries that contain strings
    for idx, val in enumerate(txt):
        if idx % 2 == 0:
            if type(val) != str:
                raise Exception(f'{Ct.RED}"Better Print" function (bp) -> "txt'
                                f' list even entries must be str. txt type = '
                                f'{type(val)}{Ct.A}')
            ent = ''
            j = txt[idx + 1]
            # colorize numbers and reset to default
            if num == 1 and j == Ct.A:
                for i in val[:]:
                    ent += f'{Ct.BBLUE}{i}{Ct.A}' if i.isdigit() else i
            # colorize numbers and reset to requested color for that part
            elif num == 1:
                for i in val[:]:
                    ent += f'{Ct.BBLUE}{i}{j}' if i.isdigit() else i
            # don't colorize numbers
            else:
                ent = val
            # now wrap the color numbered string with the requested color
            txt_out += f'{j}{ent}{Ct.A}'
            # file output is the original value with no console coloration
            file_out += val[:]

    # ~~~ #     log section - prepend time to each output
    # skip if log is not implemented in args
    if 'log' in args_dict:
        if args.log and log == 1:
            dt_now = datetime.now().strftime('[%H:%M:%S]')
            txt_out = f'{dt_now}-{print_tracker}-{txt_out}'
            file_out = f'{dt_now}-{print_tracker}-{file_out}'

    # ~~~ #     no color check
    # skip if no_color not implemented in args
    if 'no_color' in args_dict:
        if args.no_color:
            txt_out = file_out[:]

    # ~~~ #     console output section
    if inl == 0 and con == 1:    # default with new line appended
        sys.stdout.write(f'{txt_out}\n')
        print_tracker += 1
    elif inl == 1 and fls == 0 and con == 1:     # in-line with no flush
        sys.stdout.write(txt_out)
    elif inl == 1 and fls == 1 and con == 1:     # in-line with flush
        sys.stdout.write(txt_out)
        sys.stdout.flush()

    # ~~~ #     file output section
    # skip if file log output not implemented in args
    if 'log_file' in args_dict or 'error_log_file' in args_dict:
        try:
            if args.log_file and fil == 1:
                with open(args.log_file, 'a') as f:
                    f.write(file_out + '\n')
            if args.error_log_file and erl > 0 and fil == 1:
                with open(args.error_log_file, 'a') as f:
                    f.write(file_out + '\n')
        except OSError as e:
            bp([f'exception caught trying to write to {args.log_file} or '
                f'{args.error_log_file}\n\t{e}', Ct.RED], erl=1, fil=0)

    return


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
def validate_args():
    """Validate the cli args before executing main()."""
    def file_check(f_to_c):
        """Check log file or error log file if it exists and if it should be
        appended.

        Args:
            - f_to_c (string): the file to check
        """
        bp([f'Starting validate_args()->file_check({f_to_c}).',
            Ct.BMAGENTA], fil=0, veb=3)
        if os.path.isfile(f_to_c):
            check_append = input(f'{Ct.YELLOW}({f_to_c}) exists. Append? '
                                 f'[Y/N]: {Ct.A}')
            # abort on no
            if check_append[:1].lower() == 'n':
                bp(['Exiting', Ct.YELLOW], fil=0, erl=1)
                sys.exit(1)
            # call file_check again if anything other than y (since n checked)
            elif check_append[:1].lower() != 'y':
                bp([f'{check_append} is not "Y" or "N".', Ct.YELLOW], erl=1,
                   fil=0)
                file_check(f_to_c)
    bp(['Checking if log_file exists and ask if it should be appended.',
        Ct.BMAGENTA], fil=0, veb=2)
    if options.args.log_file:
        file_check(options.args.log_file)
    bp(['Checking error_log_file exists and ask if it should be appended.',
        Ct.BMAGENTA], fil=0, veb=2)
    if options.args.error_log_file:
        file_check(options.args.error_log_file)
    if options.args.verbose > 3:
        bp([f'Verbosity level {options.args.verbose} requested. Using the'
            ' maximum of 3.', Ct.YELLOW], erl=1)

    return


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
def main():

    bp(['Entered main().', Ct.BMAGENTA], veb=3)
    bp(['Print args in 2 different forms:', Ct.BMAGENTA], veb=1)
    bp(['Args from argparse in dict form using vars(args): ',
        f'{vars(options.args)}', Ct.A])
    bp(['CLI Args split: ', Ct.A], inl=1)
    for k, v in vars(options.args).items():
        bp([f'  {k}: {v}  |', Ct.A], inl=1, log=0)
    bp(['', Ct.A], log=0)
    bp(['End of main().', Ct.BMAGENTA], veb=1)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
if __name__ == '__main__':

    print_tracker = options.print_tracker
    bp([f'{options.ver}\n', Ct.BBLUE])
    bp(['Print before args showing args bypass. Since no args verbosity '
        'specified. This will not go to any file output since no file output '
        'request has yet been processed.', Ct.BMAGENTA], veb=2)
    args = options.args
    bp(['Retrieved args from get_args().', Ct.BMAGENTA], veb=3)
    bp(['Calling validate_args():', Ct.BMAGENTA], veb=2)
    validate_args()
    bp(['Returned from validate_args().', Ct.BMAGENTA], veb=3)
    bp(['Calling main():', Ct.BMAGENTA], veb=2)
    main()
