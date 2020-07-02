from setuptools import setup, find_packages
from os import path

# Read the README into a variable
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    readme = f.read()

setup(
    name='openapi3-fuzzer',
    packages=find_packages(),
    package_data={'': ['openapi3-fuzzer/openapi3_fuzzer/fuzz/*.txt']},
    include_package_data=True,
    version='1.2.1',
    license='gpl-3.0',
    description='Openapi3 fuzzer',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='VolkerWessels Telecom',
    author_email='opensource@vwt.digital',
    url='https://github.com/vwt-digital/openapi3-fuzzer/tree/master',
    keywords=['Openapi3', 'fuzzer', 'vwt'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'prance==0.17.0'
    ],
    python_requires='>=3.6',
)
