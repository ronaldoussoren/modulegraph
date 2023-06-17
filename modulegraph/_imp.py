try:
    from imp import find_module, PY_SOURCE, PY_COMPILED, C_EXTENSION, PKG_DIRECTORY, C_BUILTIN, PY_FROZEN, get_magic, get_suffixes

except ImportError:
    # Compatibility stub for Python 3.12 or later.
    # 
    # The code below was copied from the Python 3.10 standard library with
    # some minor edits.
    #
    # As such the license for this code is the Python license:
    #   https://docs.python.org/3/license.html

    import sys
    import os
    import importlib.util
    import importlib.machinery
    from importlib._bootstrap import _ERR_MSG
    from _imp import is_builtin, is_frozen
    import tokenize

    SEARCH_ERROR = 0
    PY_SOURCE = 1
    PY_COMPILED = 2
    C_EXTENSION = 3
    PY_RESOURCE = 4
    PKG_DIRECTORY = 5
    C_BUILTIN = 6
    PY_FROZEN = 7
    PY_CODERESOURCE = 8
    IMP_HOOK = 9

    def get_magic():
        return importlib.util.MAGIC_NUMBER


    def get_suffixes():
        extensions = [(s, 'rb', C_EXTENSION) for s in importlib.machinery.EXTENSION_SUFFIXES]
        source = [(s, 'r', PY_SOURCE) for s in importlib.machinery.SOURCE_SUFFIXES]
        bytecode = [(s, 'rb', PY_COMPILED) for s in importlib.machinery.BYTECODE_SUFFIXES]
                
        return extensions + source + bytecode

    def find_module(name, path=None):
        if path is None:
            if is_builtin(name):
                return (None, None, ('', '', C_BUILTIN))
            elif is_frozen(name):
                return (None, None, ('', '', PY_FROZEN))
            else:
                path = sys.path

        for entry in path:
            package_directory = os.path.join(entry, name)
            for suffix in ['.py', importlib.machinery.BYTECODE_SUFFIXES[0]]:
                package_file_name = '__init__' + suffix
                file_path = os.path.join(package_directory, package_file_name)
                if os.path.isfile(file_path):
                    return None, package_directory, ('', '', PKG_DIRECTORY)

            for suffix, mode, type_ in get_suffixes():
                file_name = name + suffix
                file_path = os.path.join(entry, file_name)
                if os.path.isfile(file_path): 
                    break
            else:
                continue
            break  # Break out of outer loop when breaking out of inner loop.
        else:
             raise ImportError(_ERR_MSG.format(name), name=name)

        encoding = None
        if 'b' not in mode:
            with open(file_path, 'rb') as file:
                encoding = tokenize.detect_encoding(file.readline)[0]
        file = open(file_path, mode, encoding=encoding)
        return file, file_path, (suffix, mode, type_) 
