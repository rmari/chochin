# Cython compile instructions

from distutils.core import setup
from Cython.Build import cythonize

# Use python setup.py build --inplace
# to compile

setup(
  name="chochinFile",
  ext_modules=cythonize('*.pyx'),
  # extra_compile_args=["-std=c++11"]
)
