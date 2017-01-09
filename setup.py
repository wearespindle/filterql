from setuptools import find_packages, setup

import filterql


try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except:
    long_description = ''

install_requires = [
    'python_dateutil',
    'simplejson>=2.2.0',
]

tests_require = [
    'pytest>=3.0.5',
    'pytest-cov>=2.4.0',
    'pytest-flake8>=0.8.1',
    'django>=1.8.0',
]

setup(
    name=filterql.__title__,
    version=filterql.__version__,
    description='Filter queries to json and back',
    long_description=long_description,
    url='https://github.com/wearespindle/filterql',
    author=filterql.__author__,
    author_email=filterql.__email__,
    license=filterql.__license__,
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={
        'test': tests_require,
    },
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    keyword='filter filterql query language',
    classifiers=[
        # Status.
        'Development Status :: 3 - Alpha',

        # Audience.
        'Intended Audience :: Developers',

        # License.
        'License :: OSI Approved :: MIT License',

        # Programming languages.
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
