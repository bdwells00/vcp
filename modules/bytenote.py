"""bytenote v0.0.1"""


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
def byte_notation(size: int, accuracy=2, notation=0):
    """Decimal Notation: take an integer, convert it to a string with the
    requested decimal accuracy, and append either single (default), double,
    or full word character notation.

    Args:
        - size (int): the size to convert
        - accuracy (int): how many decimal places to keep (default=2)
        - precision (int): how many characters to return denoting multiplier

    Returns:
        - [tuple]: 0 = original size int unmodified; 1 = string for printing
    """
    size_dict = {
        1: ['B', 'B', 'bytes'],
        1000: ['k', 'kB', 'kilobytes'],
        1000000: ['M', 'MB', 'megabytes'],
        1000000000: ['G', 'GB', 'gigabytes'],
        1000000000000: ['T', 'TB', 'terabytes']
    }
    return_size_str = ''
    for key, value in size_dict.items():
        if (size / key) < 1000:
            return_size_str = f'{size / key:,.{accuracy}f} {value[notation]}'
            break

    return size, return_size_str
