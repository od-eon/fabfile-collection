python fabric collection
==========================

This is a loose collection of set up bash scripts and fabric scripts that will get increasingly organized over time.

## Goals

The purpose is to automate the provisioning of a new server instance in a vendor-agnostic manner. So whether you are using Amazon EC2, Linode.com, Rackspace.com or Voxel.net, this set of fabric scripts should work exactly as advertised.

The immediate goals are: 

1.  Automated selection of the optimal open source library mirror from the distro's mirror list	

2.  Automated installation of common base packages, such as sudo, git-core, vim, tmux and htop

3.  Automated configuration of the root user's `.bash_profile` and the `.bash` configuration files in /etc/skel so new users subsequently created will inherit the configuration templates

4.  Optional creation of linux users so other developers in the team each has a corresponding linux user account with sudo rights

5.  Automated set up of python virtualenv, python (2.7), django and postgresql environment. 

6.  Support for deployment and rollback for a staging server ('development')

7.  Support for deployment and rollback for a production server ('production')

Secondary goals for webserver set up support

1.  Cherokee

2.  Nginx

3.  Apache2

The longer term goal is to support the automated set-up of various linux distros in a vagrant vm or in a remote; beginning with arch linux and hopefully debian, ubuntu and gentoo soon.

## Usage

Once you have launched your new server instance(s) with your server provider, add in the following settings in django's settings.py:

	import os

	PROJECT_ROOT = os.path.dirname(__file__)
	PROJECT_NAME = os.path.dirname(PROJECT_ROOT).split('/').pop()
	PROJECT_SITES = {
    	'production': {
        	'NAME': 'www.myserver.com',
        	'IP': 'whateveryourprodserverip',
    	},
    'development': {
        	'NAME': 'dev.myserver.com',
        	'IP': 'whateveryourdevserverip',
    	}
	}

Placing the fabfile.py in your django project root, you can now run a command such as:

	fab server_setup:root,dev

And when you are ready to deploy your django site, run:

    fab deploy:dev
