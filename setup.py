# Cython compile instructions

from distutils.core import setup, Extension
from Cython.Build import cythonize

chochinFile_module = Extension('chochinFile',
                               sources=['chochinFile.pyx'],
                               language="c++",
                               extra_compile_args=["-std=c++11"])

setup(
  ext_modules=cythonize(chochinFile_module),
)
