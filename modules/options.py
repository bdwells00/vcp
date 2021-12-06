

import modules.arguments
import modules.version
# ~~~ #        multilied against args.blocksize to get file read chunk size
BLOCK_SIZE_FACTOR = 1000


# ~~~ #        variables
# used by bp to keep count of all cli statements
print_tracker = 0
# some versioning args
ver = modules.version.ver
purpose = modules.version.__purpose__
# args used by other modules
args = modules.arguments.args


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
def execute_args_validation():
    """Placing in a function so validation only happens when called from
    the main program."""

    return modules.arguments.validate_and_process_args()
