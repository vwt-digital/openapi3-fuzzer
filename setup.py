import os

from setuptools import setup, find_packages

with open('requirements.txt') as f:
    install_requires = f.read().splitlines()

setup(
    name='openapi3-fuzzer',
    packages=find_packages(),
    package_data={'': ['openapi3-fuzzer/openapi3_fuzzer/fuzz/*.txt']},
    include_package_data=True,
    version=os.getenv('TAG_NAME', '0.0.0'),
    license='gpl-3.0',
    description='Openapi3 fuzzer',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    test_suite='test.load_test_suite',
    author='VWT Digital',
    author_email='support@vwt.digital',
    url='https://github.com/vwt-digital/openapi3-fuzzer/tree/master',
    keywords=['Openapi3', 'fuzzer', 'vwt'],
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        'Intended Audience :: Developers',
        'Natural Language :: English',
    ],
    install_requires=install_requires,
    python_requires='>=3.6',
)
