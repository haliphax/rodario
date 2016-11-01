""" setuptools installer for rodario framework """

from setuptools import setup, find_packages

setup(
    name='rodario',
    version='1.0.0a7',
    description='Simple, redis-backed Python actor framework',
    url='https://github.com/haliphax/rodario',
    author='haliphax',
    author_email='haliphax@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='actor framework',
    packages=find_packages(),
    install_requires=[
        'redis==2.10.3',
    ],
)
