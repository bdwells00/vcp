

import modules.arguments as arguments
import modules.version as version
# ~~~ #        multiplied against args.blocksize to get file read chunk size
BLOCK_SIZE_FACTOR = 1000


# ~~~ #        variables
# used by bp to keep count of all cli statements
print_tracker = 0
# some versioning args
ver = version.ver
purpose = version.__purpose__
copyright = f'Copyright ©️ 2021, {version.__author__}'
license_info = version.__license__
# used to hold bytes copied so far
bytes_done = 0
# global args
args = arguments.get_args()
