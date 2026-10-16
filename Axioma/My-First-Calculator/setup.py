"""
setup.py
--------
Build the C++ evaluator extension module via pybind11.

Usage:
    pip install pybind11
    python setup.py build_ext --inplace
"""

from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup

ext_modules = [
    Pybind11Extension(
        "core._evaluator_cpp",
        ["core/evaluator.cpp"],
        cxx_std=17,
        define_macros=[("M_PI", "3.14159265358979323846")],
    ),
]

setup(
    name="my-first-calculator",
    version="1.0.0",
    description="My First Calculator with C++ evaluator backend",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
    python_requires=">=3.10",
)
