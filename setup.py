#!/usr/bin/env python

try:
    import setuptools

except ImportError:
    import distribute_setup
    distribute_setup.use_setuptools()

from setuptools import setup
from setuptools.command import test
from distutils.errors  import DistutilsError
from distutils import log
try:
    from distutils.core import PyPIRCCommand
except ImportError:
    PyPIRCCommand = None # Ancient python version
    from distutils.core import Command

import sys
import os

VERSION = '0.8.2'
DESCRIPTION = "Python module dependency analysis tool"
LONG_DESCRIPTION = """
modulegraph determines a dependency graph between Python modules primarily
by bytecode analysis for import statements.

modulegraph uses similar methods to modulefinder from the standard library,
but uses a more flexible internal representation, has more extensive 
knowledge of special cases, and is extensible.

"""

LONG_DESCRIPTION += open('doc/changelog.rst', 'rU').read()


CLASSIFIERS = filter(None, map(str.strip,
"""                 
Intended Audience :: Developers
License :: OSI Approved :: MIT License
Programming Language :: Python
Programming Language :: Python :: 2
Programming Language :: Python :: 3
Topic :: Software Development :: Libraries :: Python Modules
Topic :: Software Development :: Build Tools
""".splitlines()))

if sys.version_info[0] == 3:
    extra_args = dict(use_2to3=True)
else:
    extra_args = dict()

def test_loader():
    import unittest

    topdir = os.path.dirname(os.path.abspath(__file__))
    testModules = [ fn[:-3] for fn in os.listdir(os.path.join(topdir, 'modulegraph_tests')) if fn.endswith('.py')]
    sys.path.insert(0, os.path.join(topdir, 'modulegraph_tests'))

    suites = []
    for modName in testModules:
        try:
            module = __import__(modName)
        except ImportError:
            print ("SKIP %s: %s"%(modName, sys.exc_info()[1]))
            continue

        s = unittest.defaultTestLoader.loadTestsFromModule(module)
        suites.append(s)

    return unittest.TestSuite(suites)

class modulegraph_test (test.test):
    def run(self):
        p = list(self.distribution.packages)
        try:
            cmd = self.get_finalized_command('build_py')
            test.test.run(self)
        finally:
            self.distribution.packages[:] = p

    def run_tests(self):
        import sys, os

        if sys.version_info[0] == 3:
            rootdir =  os.path.dirname(os.path.abspath(__file__))
            if rootdir in sys.path:
                sys.path.remove(rootdir)

        ei_cmd = self.get_finalized_command('egg_info')
        egg_name = ei_cmd.egg_name.replace('-', '_')

        to_remove = []
        for dirname in sys.path:
            bn = os.path.basename(dirname)
            if bn.startswith(egg_name + "-"):
                to_remove.append(dirname)

        for dirname in to_remove:
            log.info("removing installed %r from sys.path before testing"%(dirname,))
            sys.path.remove(dirname)

        test.test.run_tests(self)


if PyPIRCCommand is None:
    class upload_docs (Command):
        description = "upload sphinx documentation"
        user_options = []

        def initialize_options(self):
            pass

        def finalize_options(self):
            pass

        def run(self):
            raise DistutilsError("not supported on this version of python")

else:
    class upload_docs (PyPIRCCommand):
        description = "upload sphinx documentation"
        user_options = PyPIRCCommand.user_options

        def initialize_options(self):
            PyPIRCCommand.initialize_options(self)
            self.username = ''
            self.password = ''


        def finalize_options(self):
            PyPIRCCommand.finalize_options(self)
            config = self._read_pypirc()
            if config != {}:
                self.username = config['username']
                self.password = config['password']


        def run(self):
            import subprocess
            import shutil
            import zipfile
            import os
            import urllib
            import StringIO
            from base64 import standard_b64encode
            import httplib
            import urlparse

            # Extract the package name from distutils metadata
            meta = self.distribution.metadata
            name = meta.get_name()

            # Run sphinx
            if os.path.exists('doc/_build'):
                shutil.rmtree('doc/_build')
            os.mkdir('doc/_build')

            p = subprocess.Popen(['make', 'html'],
                cwd='doc')
            exit = p.wait()
            if exit != 0:
                raise DistutilsError("sphinx-build failed")

            # Collect sphinx output
            if not os.path.exists('dist'):
                os.mkdir('dist')
            zf = zipfile.ZipFile('dist/%s-docs.zip'%(name,), 'w', 
                    compression=zipfile.ZIP_DEFLATED)

            for toplevel, dirs, files in os.walk('doc/_build/html'):
                for fn in files:
                    fullname = os.path.join(toplevel, fn)
                    relname = os.path.relpath(fullname, 'doc/_build/html')

                    print ("%s -> %s"%(fullname, relname))

                    zf.write(fullname, relname)

            zf.close()

            # Upload the results, this code is based on the distutils
            # 'upload' command.
            content = open('dist/%s-docs.zip'%(name,), 'rb').read()
            
            data = {
                ':action': 'doc_upload',
                'name': name,
                'content': ('%s-docs.zip'%(name,), content),
            }
            auth = "Basic " + standard_b64encode(self.username + ":" +
                 self.password)


            boundary = '--------------GHSKFJDLGDS7543FJKLFHRE75642756743254'
            sep_boundary = '\n--' + boundary
            end_boundary = sep_boundary + '--'
            body = StringIO.StringIO()
            for key, value in data.items():
                if not isinstance(value, list):
                    value = [value]

                for value in value:
                    if isinstance(value, tuple):
                        fn = ';filename="%s"'%(value[0])
                        value = value[1]
                    else:
                        fn = ''

                    body.write(sep_boundary)
                    body.write('\nContent-Disposition: form-data; name="%s"'%key)
                    body.write(fn)
                    body.write("\n\n")
                    body.write(value)

            body.write(end_boundary)
            body.write('\n')
            body = body.getvalue()

            self.announce("Uploading documentation to %s"%(self.repository,), log.INFO)

            schema, netloc, url, params, query, fragments = \
                    urlparse.urlparse(self.repository)


            if schema == 'http':
                http = httplib.HTTPConnection(netloc)
            elif schema == 'https':
                http = httplib.HTTPSConnection(netloc)
            else:
                raise AssertionError("unsupported schema "+schema)

            data = ''
            loglevel = log.INFO
            try:
                http.connect()
                http.putrequest("POST", url)
                http.putheader('Content-type',
                    'multipart/form-data; boundary=%s'%boundary)
                http.putheader('Content-length', str(len(body)))
                http.putheader('Authorization', auth)
                http.endheaders()
                http.send(body)
            except socket.error:
                e = socket.exc_info()[1]
                self.announce(str(e), log.ERROR)
                return

            r = http.getresponse()
            if r.status in (200, 301):
                self.announce('Upload succeeded (%s): %s' % (r.status, r.reason),
                    log.INFO)
            else:
                self.announce('Upload failed (%s): %s' % (r.status, r.reason),
                    log.ERROR)

                print ('-'*75) 
                print (r.read())
                print ('-'*75)

setup(
    name="modulegraph",
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    classifiers=CLASSIFIERS,
    author="Bob Ippolito",
    author_email="bob@redivi.com",
    maintainer="Ronald Oussoren",
    maintainer_email="ronaldoussoren@mac.com",
    url="http://bitbucket.org/ronaldoussoren/modulegraph",
    download_url="http://pypi.python.org/pypi/modulegraph",
    license="MIT License",
    packages=['modulegraph'],
    platforms=['any'],
    install_requires=["altgraph>=0.7"],
    zip_safe=True,
    test_suite='__main__.test_loader',
    cmdclass=dict(
        upload_docs=upload_docs,
        test=modulegraph_test,
    ),
    **extra_args
)
