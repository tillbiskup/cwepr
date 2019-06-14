import os
import setuptools

with open(os.path.join(os.path.dirname(__file__), 'VERSION')) as version_file:
    version = version_file.read().strip()

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as f:
    readme = f.read()


setuptools.setup(
    name='cwepr',
    version=version,
    description='Package for handling cw-EPR data.',
    long_description=readme,
    long_description_content_type='text/x-rst',
    author='Pascal Kirchner, Till Biskup',
    author_email='',
    url='',
    packages=setuptools.find_packages(exclude=('tests', 'docs')),
    keywords=[
        'EPR spectroscopy',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Development Status :: 3 - Alpha",
        "Topic :: Scientific/Engineering",
    ],
    install_requires=[
        'numpy',
        'scipy',
        'matplotlib',
    ],
    python_requires='>=3.5',
)
