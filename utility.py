def enum(*sequential, **named):
    """"Used for enumeration of variables. Usage is, e.g.: Numbers = enum('ZERO', 'ONE', 'TWO')"""
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)


def classes_to_dict(current_module):
    import inspect

    # this listcomp does the following:
    # 1. get all classes in this modules, including imported ones
    # so all_classes is a list of (name, value) tuples
    # 2. get only those classes defined in this module
    # 3. dict() that list of tuples to get a dictionary of "Class":Class key/value pairs

    return dict([
        c for c
        in inspect.getmembers(current_module, inspect.isclass)
        if inspect.getmodule(c[1]) == current_module
    ])
