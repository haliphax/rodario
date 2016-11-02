""" setuptools installer for rodario framework """

from os.path import realpath, dirname, join
from setuptools import setup, find_packages

if __name__ == '__main__':
    reqs = []

    with open(join(realpath(dirname(__file__)), 'requirements.txt')) as reqfile:
        reqs = reqfile.readlines()

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
        install_requires=reqs,
    )
