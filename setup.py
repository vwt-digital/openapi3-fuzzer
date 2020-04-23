from setuptools import setup, find_packages

setup(
    name='openapi3-fuzzer',
    packages=find_packages(),
    package_data={'': ['openapi3-fuzzer/openapi3_fuzzer/fuzz/*.txt']},
    include_package_data=True,
    version='1.1.2',
    license='gpl-3.0',
    description='Openapi3 fuzzer',
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
