"""
A helper module that can work with paths 
that can refer to data inside a zipfile
"""
import os as _os
import zipfile as _zipfile
import errno as _errno
import time

try:
    from  StringIO import StringIO as StringIO
    from  StringIO import StringIO as BytesIO


except ImportError:
    from io import StringIO, BytesIO

def _locate(path):
    full_path = path
    if _os.path.exists(path):
        return path, None

    else:
        rest = []
        root = _os.path.splitdrive(path)
        while path != root:
            path, bn = _os.path.split(path)
            rest.append(bn)
            if _os.path.exists(path):
                break

        if path == root:
            raise IOError(
                _errno.ENOENT, full_path, 
                "No such file or directory")

        if not _os.path.isfile(path):
            raise IOError(
                _errno.ENOENT, full_path, 
                "No such file or directory")

        rest.reverse()
        return path, '/'.join(rest)

_open = open
def open(path, mode='r'):
    if 'w' in mode or 'a' in mode:
        raise IOError(
            _errno.EINVAL, path, "Write access not supported")
    elif 'r+' in mode:
        raise IOError(
            _errno.EINVAL, path, "Write access not supported")

    path, rest = _locate(path)
    if not rest:
        return _open(path, mode)

    else:
        try:
            zf = _zipfile.ZipFile(path, 'r')

        except _zipfile.error:
            raise IOError(
                _errno.ENOENT, full_path, 
                "No such file or directory")

        try:
            data = zf.read(rest)
        except (_zipfile.error, KeyError):
            zf.close()
            raise IOError(
                _errno.ENOENT, full_path, 
                "No such file or directory")
        zf.close()

        if mode == 'rb':
            return BytesIO(data)

        else:
            if sys.version_info[0] == 3:
                data = data.decode('ascii')

            return StringIO(data)

def listdir(path):
    path, rest = _locate(path)
    if not rest:
        return _os.listdir(path)

    else:
        try:
            zf = _zipfile.ZipFile(path, 'r')

        except _zipfile.error:
            raise IOError(
                _errno.ENOENT, full_path, 
                "No such file or directory")

        result = set()
        try:
            for nm in zf.namelist():
                if nm.startswith(rest):
                    value = nm[len(rest):].split('/')[0]
                    if value: 
                        result.add(value)
        except _zipfile.error:
            zf.close()
            raise IOError(
                _errno.ENOENT, full_path, 
                "No such file or directory")

        zf.close()

        if len(result) == 0:
            raise IOError(
                _errno.ENOENT, full_path, 
                "No such file or directory")

        return list(result)

def isfile(path):
    path, rest = _locate(path)
    if not rest:
        return _os.path.isfile(path)

    zf = None
    try:
        zf = _zipfile.ZipFile(path, 'r')
        info = zf.getinfo(rest)
        zf.close()
        return True
    except (KeyError, _zipfile.error):
        if zf is not None:
            zf.close()
        return False
        

def isdir(path):
    path, rest = _locate(path)
    if not rest:
        return _os.path.isdir(path)

    zf = None
    try:
        zf = _zipfile.ZipFile(zf)
        try:
            info = zip.getinfo(rest)
        except KeyError:
            zf.close()
            return True

        
        zf.close()

        # Not quite true, you can store information 
        # about directories in zipfiles, but those 
        # have a lash at the end of the filename
        return False
    except (KeyError, _zipfile.error):
        if zf is not None:
            zf.close()
        return False

def islink(path):
    path, rest = _locate(path)
    if rest:
        # No symlinks inside zipfiles
        return False

    return _os.path.islink(path)

def readlink(path):
    path, rest = _locate(path)
    if rest:
        # No symlinks inside zipfiles
        raise IOError(
            _errno.ENOENT, full_path, 
            "No such file or directory")

    return _os.readlink(path)

def getmtime(path):
    path, rest = _locate(path)
    if not rest:
        return _os.getmtime(path)

    zf = None
    try:
        zf = _zipfile.ZipFile(path)
        info = zf.getinfo(rest)
        zf.close()

        return _time.mktime(info.date_time + (0, 0, 0))

    except KeyError:
        if zf is not None:
            zf.close()
        raise IOError(
            _errno.ENOENT, full_path, 
            "No such file or directory")
