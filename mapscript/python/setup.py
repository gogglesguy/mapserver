# $Id$
#
# setup.py file for MapScript
#
# BUILD
#   python setup.py build
#
# INSTALL (usually as root)
#   python setup.py install
# 
# DEVELOP (build and run in place)
#   python setup.py develop

import sys, os

try:
    from setuptools import setup
    from setuptools import Extension
    HAVE_SETUPTOOLS = True
except ImportError:
    from distutils.core import setup, Extension


from distutils import sysconfig
from distutils.command.build_ext import build_ext
from distutils.ccompiler import get_default_compiler
from distutils.sysconfig import get_python_inc
import popen2

# 
# # Function needed to make unique lists.
def unique(list):
    dict = {}
    for item in list:
        dict[item] = ''
    return dict.keys()

# ---------------------------------------------------------------------------
# Default build options
# (may be overriden with setup.cfg or command line switches).
# ---------------------------------------------------------------------------

include_dirs = ['../..']
library_dirs = ['../../']
libraries = ['mapserver']

extra_link_args = []
extra_compile_args = []
# might need to tweak for Python 2.4 on OSX to be these
#extra_compile_args = ['-g', '-arch', 'i386', '-isysroot','/']


def get_config(option, config='../../mapserver-config'):
    command = config + " --%s" % option
    p = popen2.popen3(command)
    r = p[0].readline().strip()
    if not r:
        raise Warning(p[2].readline())
    return r
    

class ms_ext(build_ext):

    MAPSERVER_CONFIG = '../../mapserver-config'
    user_options = build_ext.user_options[:]
    user_options.extend([
        ('mapserver-config=', None,
        "The name of the mapserver-config binary and/or a full path to it"),
    ])

    def initialize_options(self):
        build_ext.initialize_options(self)
        self.gdaldir = None
        self.mapserver_config = self.MAPSERVER_CONFIG

    def get_compiler(self):
        return self.compiler or get_default_compiler()
    
    def get_mapserver_config(self, option):
        return get_config(option, config =self.mapserver_config)
    
    def finalize_options(self):
        if self.include_dirs is None:
            self.include_dirs = include_dirs
        
        includes =  self.get_mapserver_config('includes')
        includes = includes.split()
        for item in includes:
            if item[:2] == '-I' or item[:2] == '/I':
                if item[2:] not in include_dirs:
                    self.include_dirs.append( item[2:] )

        if self.library_dirs is None:
            self.library_dirs = library_dirs

        libs =  self.get_mapserver_config('libs')
        self.library_dirs = self.library_dirs + [x[2:] for x in libs.split() if x[:2] == "-L"]

        ex_next = False
        libs = libs.split()
        for x in libs:
            if ex_next:
                extra_link_args.append(x)
                ex_next = False
            elif x[:2] == '-l':
                libraries.append( x[2:] )
            elif x[-4:] == '.lib' or x[-4:] == '.LIB':
                dir, lib = os.path.split(x)
                libraries.append( lib[:-4] )
                if len(dir) > 0:
                    lib_dirs.append( dir )
            elif x[-2:] == '.a':
                extra_link_args.append(x)
            elif x[:10] == '-framework':
                extra_link_args.append(x)
                ex_next = True
            elif x[:2] == '-F':
                extra_link_args.append(x)
                
        # don't forget to add mapserver lib
        self.libraries = unique(libraries) + ['mapserver',]

        if self.libraries is None:
            if self.get_compiler() == 'msvc':
                libraries.remove('mapserver')
                libraries.append('mapserver_i')
                libraries.append('gd')
            self.libraries = libraries

        build_ext.finalize_options(self)
        
        if self.get_compiler() == 'msvc':
            return True
        try:
            self.dir = os.path.abspath('..')
            self.library_dirs.append(self.dir)
            self.include_dirs.append(self.dir)
        except:
            print 'Could not run mapserver-config!!!!'


    
mapserver_module = Extension('_mapscript',
                        sources=["mapscript_wrap.c", "pygdioctx/pygdioctx.c"],
#                        define_macros = define_macros,
                        extra_compile_args = extra_compile_args,
                        extra_link_args = extra_link_args)


mapserver_version = get_config('version')
author = "Steve Lime"
author_email = "steve.lime@dnr.state.mn.us"
maintainer = "Howard Butler"
maintainer_email = "hobu.inc@gmail.com"
description = "MapServer Python MapScript bindings"
license = "MIT"
url="http://www.mapserver.org"
name = "MapScript"
ext_modules = [mapserver_module,]
py_modules = ['mapscript',]

readme = file('README','rb').read()

if not os.path.exists('mapscript_wrap.c') :
	os.system('swig -python -shadow -modern %s -o mapscript_wrap.c ../mapscript.i' % " ".get_config('defines'))

classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: C',
        'Programming Language :: C++',
        'Topic :: Scientific/Engineering :: GIS',
        'Topic :: Scientific/Engineering :: Information Analysis',
        
]

if HAVE_SETUPTOOLS:
    setup( name = name,
           version = mapserver_version,
           author = author,
           author_email = author_email,
           maintainer = maintainer,
           maintainer_email = maintainer_email,
           long_description = readme,
           description = description,
           license = license,
           classifiers = classifiers,
           py_modules = py_modules,
           url=url,
           zip_safe = False,
           cmdclass={'build_ext':ms_ext},
           ext_modules = ext_modules )
else:
    setup( name = name,
           version = mapserver_version,
           author = author,
           author_email = author_email,
           maintainer = maintainer,
           maintainer_email = maintainer_email,
           long_description = readme,
           description = description,
           license = license,
           classifiers = classifiers,
           py_modules = py_modules,
           url=url,
           cmdclass={'build_ext':ms_ext},
           ext_modules = ext_modules )    