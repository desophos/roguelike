def enum(*sequential, **named):
    """Used for enumeration of variables.
    Usage is, e.g.: Numbers = enum('ZERO', 'ONE', 'TWO')"""

    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)


def classes_to_dict(current_module):
    """Does the following:
    1. get all classes (a list of (name, value) tuples)
        in current_module, including imported ones
    2. get only those classes defined in current_module
    3. dict() that list of tuples to get
        a dictionary of "Class":Class key/value pairs"""

    import inspect

    return dict([
        c for c
        in inspect.getmembers(current_module, inspect.isclass)
        if inspect.getmodule(c[1]) == current_module
    ])
