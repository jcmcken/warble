from setuptools import setup

setup(
    name='warble',
    version='0.0.1',
    description='A MIDI adapter for FFXIV',
    author='Jon McKenzie',
    url='https://github.com/jcmcken/warble',
    packages=['warble'],
    entry_points = {
        'console_scripts': ['warble=warble:main']
    },
    install_requires=open('requirements.txt').read().splitlines(),
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 2 :: Only",
        "Environment :: Win32 (MS Windows)",
    ]
)