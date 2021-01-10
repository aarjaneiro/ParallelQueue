from os import path

from Cython.Build import cythonize
from setuptools import Extension, setup

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

ext_modules = [
    Extension("parallelqueue",
              ["parallelqueue/*.pyx"])]
ext_options = {"language_level": 3}

setup(name='ParallelQueue', version='0.2', packages=['parallelqueue'],
      ext_modules=cythonize(ext_modules, **ext_options),
      url='https://github.com/aarjaneiro/ParallelQueue', license='MIT', author='Aaron Janeiro Stone',
      author_email='ajstone@uwaterloo.ca', description='Parallel queueing models for SimPy',
      long_description=long_description, long_description_content_type='text/markdown')
