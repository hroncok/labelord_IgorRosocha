Configuration
=================

To initialize the configuration of **labelord** properly, you first need to initialize your personal access **GitHub token** and **webhook secret** (only required if using the web application), in order to successfully communicate with GitHub API.

GitHub token
-------------

**GitHub personal access token** is a unique string, which user can generate in order to authenticate himself during the communication with GitHub API. For **labelord** to work properly, the GitHub token is required. You can generate your own following these steps:

	- navigate to your **GitHub** profile and choose **Settings**,
	- in the left sidebar, click **Developer settings**,
	- in the left sidebar, click **Personal access tokens**,
	- click **Generate new token** (give your token a descriptive name),
	- select the scopes, or permissions, you'd like to grant this token (if you want **labelord** to be able to manage also your private repositories, you need to choose **“Full control of private repositories** permission),
	- when you're finished, click on **Generate token**.



Now you are able to copy your newly created **GitHub token** and specify it. There are two ways of specifying the **GitHub token**:

	- specify it in your `Configuration file`_
	- using the ``-t/--token`` option when running from CLI.

Webhook
--------

**Webhooks** provide a way for notifications to be delivered to an external web server whenever certain actions occur on a repository. **Labelord** uses GitHub webhooks to propagate the changes to GitHub repositories in it's web application. So if you make changes in one of your repositories attached with webhook, the changes will propagate to other repositories automatically. To setup a webhook, please follow these steps:

	- head over to the **Settings** page of your repository and click on **Webhooks & services**,
	- click on **Add webhook**,
	- fill the **Payload URL** (the server endpoint that will receive the webhook payload),
	- select **Content type** (we will be working with Application/json),
	- specify your **Webhook secret** (you will need to use this one in the configuration file),
	- choose **Let me select individual events** and **Label** option,
	- when you're finished, click on **Add webhook**.

Now that you're all set up, let's get to the specification of **Configuration file**.


Configuration file
-------------------

The configuration file, which is used to specify the repositories and labels, has to be located in the labelord directory (by default) with the name provided ``./config.cfg``.

There are also other options how to specify the configuration file:

    - using the ``-c/--config`` option when running from CLI
    - specifying the ``LABELORD_CONFIG`` environment variable when running as a web application

Configuration files has to contain these fields:

	- ``[github]``
		- ``token``: your GitHub personal access token.
		- ``webhook_secret``: your webhook secret key to validate all the incoming GitHub webhooks (only required if using the web application).
		.. warning:: **Don't forget to keep your token and webhook secret safe and never publish them!**

	- ``[labels]``
		- here, you can specify all of the labels you want to create / edit, in the form of ``LABEL_NAME = LABEL_COLOR``. The label color is specified in the hexadecimal RGB format. One label per line!

	- ``[repos]``
		- here, you can specify all of the repositories you want to manage, in the form of ``GITHUB_NICKNAME/REPOSITORY_NAME = on/off``.
		- the ``on/off`` option specifies if you want to perfom changes in the specified repository or not (can be altered by ``1/0``).

	- ``[others]``
		- here, you can specify the "template" repository, which labels will be used as a source of labels instead of the labels specified in ``[labels]`` section.
		- form: ``TEMPLATE_REPO = GITHUB_NICKNAME/REPOSITORY_NAME``

Example configuration file
---------------------------

::

   [github]
   token = ENTER_YOUR_TOKEN_HERE
   webhook_secret = ENTER_YOUR_WEBHOOK_SECRET_HERE

   [labels]
   Bug = E00F1A
   Enhancement = 84B6EB
   Help wanted = EF5171

   [repos]
   IgorRosocha/labelord_IgorRosocha = on
   username/github_repository = off

Environment variables
----------------------

Some configuration can be also set up specifying these **environment variables**:

    - ``LABELORD_CONFIG`` : config path when running **labelord** as a web application,
    - ``GITHUB_TOKEN`` : GitHub token,
    - ``FLASK_DEBUG`` : debug mode for web application (true/false)

Please proceed to `Usage <usage.html#section>`__.