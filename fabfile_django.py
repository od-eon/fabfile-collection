from fabric.api import local, env, run
from fabric.context_managers import prefix

# we need to do this to ensure that mkvirtualenv and other bash commands are available
# this is because fabric uses /bin/sh by default and hence have no access to virtualenv cmds.
env.activate = 'source ~/.bash_profile; source `which virtualenvwrapper.sh`;'

def start(name="project"):
    print("Creating a new django project named `{0}`.".format(name))
    print("Creating virtualenv `{0}` for this project.".format(name))
    local(env.activate + "mkvirtualenv --python=python2.7 --no-site-packages {0}".format(name))
    with prefix(env.activate + "workon {0}".format(name)):
        local("pip install django")


# TODO: include arch_setup commands and mac_setup commands in fabfile. 
