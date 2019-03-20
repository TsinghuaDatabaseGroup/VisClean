from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

setup(
    cmdclass={'build_ext': build_ext},
    ext_modules=[Extension("util", ["util.py"]),
                 Extension("program", ["program.py"]),
                 Extension("golden_record_py", ["golden_record_py.py"]),
                 Extension("kmp", ["kmp.py"])]
)
