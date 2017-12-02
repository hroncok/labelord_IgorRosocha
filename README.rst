## Labelord

**Labelord** is a management application for GitHub repositories, created as a part of **MI-PYT** course at **CTU in Prague**.

-------

It allows to:
1. List all repositories and repository labels of GitHub user
2. ADD/DELETE/UPDATE multiple repositories labels, using CLI or web server with GitHub webhooks technology
(note that personal token and webhook secret verification is required!)

Labels, repositories, personal token and webhook secret are defined in **configuration file**, see included **config.cfg** as an example for more details.

Installation
-------------

There are two ways how to install **labelord**:

1. Installation directly from TestPyPI, using the following command:

.. code:: python

    python -m pip install --extra-index-url \
    https://test.pypi.org/pypi IgorRosocha

2. If any problem occurred, please follow these steps:
	- Download **labelord** directly from TestPyPI `here <https://testpypi.python.org/pypi/labelord-IgorRosocha>`_.
	- Unpack the download .tar.gz file.
	- Use the following command in the labelord directory:
	
.. code:: python

    python setup.py install

Please note that **labelord** requires at least Python 3 to be installed to run properly!

Documentation
--------------



License
-------------

This project is licensed under the **MIT License**.

You can also download this project as a package from TestPyPI [here](https://testpypi.python.org/pypi/labelord-IgorRosocha).
