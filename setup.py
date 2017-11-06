from setuptools import setup, find_packages

with open('README.md') as f:
    long_description = ''.join(f.readlines())

setup(
    name='labelord_IgorRosocha',
    version='0.3',
    description='Management of GitHub labels.',
    long_description=long_description,
    author='Igor Rosocha',
    author_email='rosocigo@fit.cvut.cz',
    keywords='github,labels,management',
    license='MIT',
    url='https://github.com/IgorRosocha/labelord_IgorRosocha',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries'
    ],
    install_requires=['Flask', 'click>=6', 'requests'],
    setup_requires=['pytest-runner', 'pytest'],
    tests_require=['pytest', 'betamax', 'configparser'],
    zip_safe=False,
    entry_points={
        'console_scripts': [
         'labelord = labelord.labelord:main',
        ],
    },
)
