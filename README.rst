labelord
=========

**Labelord** is a management application for GitHub repositories, created as a part of **MI-PYT** course at **CTU in Prague**.

-------

It allows to:
	- List all repositories and repository labels of GitHub user
	- ADD/DELETE/UPDATE multiple repositories labels, using CLI or web server with GitHub webhooks technology
	(note that personal token and webhook secret verification is required!)

Labels, repositories, personal token and webhook secret are defined in **configuration file**, see included **config.cfg** as an example for more details.

Installation
-------------

There are two ways how to install **labelord**:

1. Installation directly from TestPyPI, using the following command: 

``python -m pip install --extra-index-url https://test.pypi.org/pypi IgorRosocha``

2. If any problem occurred, please follow these steps:
	
- Download **labelord** directly from TestPyPI `here <https://testpypi.python.org/pypi/labelord-IgorRosocha>`_.
- Unpack the download .tar.gz file.
- Use the following command in the labelord directory: ``python setup.py install``


Please note that **labelord** requires at least Python 3 to be installed to run properly!

Documentation
--------------

For the full documentation, please visit `Readthedocs.io <http://labelord-igorrosocha.readthedocs.io/en/latest/>`__.

You can also build the documentation locally. Just follow these steps:

1. Download **labelord**
2. Navigate to **docs** directory
3. Run ``python python -m pip install -r requirements.txt``
4. Run ``make html`` and ``make doctest``
5. You can find all of the .html files in _build/html directory
	

License
-------------

This project is licensed under the **MIT License**.
