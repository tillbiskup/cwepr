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
    author='Mirjam Schröder, Pascal Kirchner, Till Biskup',
    author_email='till@till-biskup.de',
    url='https://www.cwepr.de/',
    project_urls={
        "Documentation": "https://docs.cwepr.de/",
        "Source": "https://github.com/tillbiskup/cwepr",
    },
    packages=setuptools.find_packages(exclude=('tests', 'docs')),
    include_package_data=True,
    license='BSD',
    keywords=[
        'EPR spectroscopy',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Development Status :: 4 - Beta",
        "Topic :: Scientific/Engineering",
    ],
    install_requires=[
        'aspecd>=0.6.0',
        'numpy',
        'scipy',
        'matplotlib',
    ],
    python_requires='>=3.5',
)
