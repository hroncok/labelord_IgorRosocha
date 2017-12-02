Examples
=========

If you wonder how certain methods work, here you can see some examples, tested thanks to **doctest** just for you.

Parsing the labels from GitHub JSON
------------------------------------

All of the received GitHub JSONs are being parsed, thanks to the method **parse_labels** to filter the labels names and colors for further work. Here you can see the example of GitHub JSON received:

::

	[
	 {
	   "id": 208045946,
	   "url": "https://api.github.com/repos/octocat/Hello-World/labels/bug",
	   "name": "bug",
	   "color": "f29513",
	   "default": "true"
	  },
	  {
	   "id": 208045947,
	   "url": "https://api.github.com/repos/octocat/Hello-World/labels/enhancement",
	   "name": "enhancement",
	   "color": "84b6eb",
	   "default": "true"
	  },
	  {
	   "id": 208045948,
	   "url": "https://api.github.com/repos/octocat/Hello-World/labels/question",
	   "name": "question",
	   "color": "cc317c", 
           "default": "true"
          }
	]	



.. testsetup::
	
	from labelord.cli import parse_labels

	json = [{"id": 208045946, "url": "https://api.github.com/repos/octocat/Hello-World/labels/bug", "name": "bug", "color": "f29513", "default": "true"}, {"id": 208045947, "url": "https://api.github.com/repos/octocat/Hello-World/labels/enhancement", "name": "enhancement", "color": "84b6eb", "default": "true"}, {"id": 208045948, "url": "https://api.github.com/repos/octocat/Hello-World/labels/question", "name": "question", "color": "cc317c", "default": "true"}]

And here's the result of using **parse_labels** on our example JSON:

.. testcode::

    parsed_labels = parse_labels(json)
    print(parsed_labels)


.. testoutput::

    {'bug': 'f29513', 'enhancement': '84b6eb', 'question': 'cc317c'}


Reading repositories from config
---------------------------------

.. testsetup::

	import configparser
	from labelord.web import get_repos_from_config
	
	config = '_static/config.cfg'
	config_file = configparser.ConfigParser()
	config_file.optionxform = str
	config_file.read(config)

One of the crucial functionalities of **labelord** is reading data from configuration file. This is the responsibility of **get_repos_from_list** method. Here, you can see example of reading repositories names from configuration file.

Example configuration file:

::

	[github]
	token = ENTER_YOUR_TOKEN_HERE
	webhook_secret = ENTER_YOUR_WEBHOOK_SECRET_HERE

	[labels]
	Bug = FFAA00
	Enhancement = CCAAFF
	Help wanted = CCAAFF

	[repos]
	ExampleUser/labelord = on
	ExampleUser/drolebal = off
	ExampleUser/quantumcomputer = on


And here’s the result of using **get_repos_from_config** on our example configuration file:

.. testcode::

	print(get_repos_from_config(config_file))

.. testoutput::

	['ExampleUser/labelord', 'ExampleUser/quantumcomputer']

.. note:: Only repositories with value on/off (1/0) are listed!


Finding the labels to delete
-----------------------------

When updating your labels, method **diff** computes the difference between labels in your specified repository and labels specified in your configuration file to find out which labels to delete (if any).

.. testsetup::

	from labelord.cli import diff

Let's assume that your repository contains these labels:
	- bug
	- duplicate
	- enhancement
	- good first issue
	- help wanted
	- invalid
	- question
	- wontfix

But the labels specified in your configuration file are:
	- bug
	- duplicate
	- invalid
	- wontfix

.. note:: Label colors doesn't matter in this case.

Because you are updating your repositories, **diff** will find out which labels in your repository are not specified in your configuration file, and **labelord** deletes them.

.. testcode::

	repository_labels = ['bug', 'duplicate', 'enhancement', 'good first issue', 'help wanted', 'invalid', 'question', 'wontfix']
	config_labels = ['bug', 'duplicate', 'invalid', 'wontfix']
	print(diff(repository_labels, config_labels))

.. testoutput::

	['enhancement', 'good first issue', 'help wanted', 'question']


If you wish, you can proceed to the full `API documentation <labelord.html#section>`__.

	










