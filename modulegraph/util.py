import os
import imp
import sys

def imp_find_module(name, path=None):
    """same as imp.find_module, but handles dotted names"""
    names = name.split('.')
    if path is not None:
        path = [os.path.realpath(path)]
    for name in names:
        result = imp.find_module(name, path)
        path = [result[1]]
    return result

def _check_importer_for_path(name, path_item):
    try:
        importer = sys.path_importer_cache[path_item]
    except KeyError:
        for path_hook in sys.path_hooks:
            try:
                importer = path_hook(path_item)
                break
            except ImportError:
                pass
        else:
            importer = None
        sys.path_importer_cache.setdefault(path_item, importer)

    if importer is None:
        try:
            return imp.find_module(name, path_item)
        except ImportError:
            return None
    return importer.find_module(name)

def imp_find_module_or_importer(name):
    if name in sys.builtin_module_names:
        return (None, None, ("", "", imp.C_BUILTIN))
    paths = sys.path
    names = name.split('.')
    res = None
    while names:
        namepart = names.pop(0)
        for path_item in paths:
            res = _check_importer_for_path(namepart, path_item)
            if res is not None:
                break
        else:
            break
        if not names:
            return res
        paths = [os.path.join(path_item, namepart)]
    raise ImportError('No module named %s' % (name,))


def test_imp_find_module():
    import encodings.aliases
    fn = imp_find_module('encodings.aliases')[1]
    assert encodings.aliases.__file__.startswith(fn)

if __name__ == '__main__':
    test_imp_find_module()
