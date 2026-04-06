from Cython.Build import cythonize
from setuptools import Extension, setup

setup(
    ext_modules=cythonize(
        [Extension("showoff_perf.cykernels", ["src/showoff_perf/cykernels.pyx"])],
        compiler_directives={"language_level": "3"},
    ),
)
