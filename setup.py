import os
from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))

version_ns = {}
with open(os.path.join(here, "quadbin", "_version.py")) as f:
    exec(f.read(), {}, version_ns)

setup(
    name="quadbin",
    version=version_ns["__version__"],
    description=(
        "Hierarchical geospatial indexing system "
        "for square cells in Web Mercator projection"
    ),
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    keywords=[
        "quadbin",
        "hierarchical",
        "geospatial",
        "index",
        "visualization",
        "maps",
        "carto",
    ],
    author="CARTO",
    author_email="contact@carto.com",
    url="https://github.com/cartodb/quadbin-py",
    license="BSD 3-Clause",
    packages=find_packages(include=["quadbin"]),
    python_requires=">=2.7",
    install_requires=[],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Topic :: Scientific/Engineering :: GIS",
    ],
    zip_safe=False,
)
