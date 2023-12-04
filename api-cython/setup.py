# setup.py
from setuptools import setup
from Cython.Build import cythonize

setup(
  ext_modules = cythonize([
      "tradinghaven.pyx",
      "routers/*.pyx"
    ],
    build_dir="build",
    annotate=True,
  )
)
