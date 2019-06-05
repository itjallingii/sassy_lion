from distutils.core import setup
from Cython.Build import cythonize
import numpy

setup(
    name = "SundayTest",
    #ext_modules = cythonize("dike_model_function.pyx", "funs_hydrostat.pyx","funs_economy.pyx", "funs_dikes.pyx", annotate = True),
    ext_modules = cythonize("dike_model_function_time_series.pyx", annotate = True),
    include_dirs=[numpy.get_include()]
)