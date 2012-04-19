# Beginnings of our fabfile utilities

# The following commented out code needs to go into django's settings.py
#import os

#PROJECT_ROOT = os.path.dirname(__file__)
#PROJECT_NAME = os.path.dirname(PROJECT_ROOT).split('/').pop()
#PROJECT_SITES = {
    #'production': {
        #'NAME': 'www.myserver.com',
        #'IP': 'whateveryourprodserverip',
    #},
    #'development': {
        #'NAME': 'dev.myserver.com',
        #'IP': 'whateveryourdevserverip',
    #}
#}

# Clean local setup
# After a git clone to grab the repository, we should have this fabfile to run a local setup.
# mkvirtualenv -p python2.7 --no-site-packages [projectname]
# cd $PROJECT_HOME/[projectname]
# pip install -r requirements.txt
# run and install any c/c++ packages that need to be inside virtualenv (like haystack/xapian-core/xapian-bindings --with-python for example)
# DONE:  create database name and user with password from settings.py
# DONE:  run syncdb/migration


import os
import subprocess

from fabric.api import local, env, sudo, require, run, put
from fabric.context_managers import prefix
from fabric.contrib import django

# Global Environment Variables
django.settings_module('proj.settings')
from django.conf import settings
env.project_name = settings.PROJECT_NAME
env.project_sites = settings.PROJECT_SITES
env.activate = 'source ~/.bash_profile; source `which virtualenvwrapper.sh`; workon {0}'.format(settings.PROJECT_NAME)
db = settings.DATABASES


##########################
# Environments
##########################


def env_localhost():
    "All the environment variables relating to your localhost"
    # PROJECT_HOME: a virtualenvwrapper var specifying where all the projects are kept
    env.project_home = os.getenv("PROJECT_HOME")
    env.project_path = '%(project_home)s/%(project_name)s' % env
    env.user = env.local_user
    env.hosts = ['localhost']


def env_vagrant():
    "All the environment variables relating to our vagrant virtual machine"
    raw_ssh_config = subprocess.Popen(["vagrant", "ssh-config"], stdout=subprocess.PIPE).communicate()[0]
    ssh_config = dict([l.strip().split() for l in raw_ssh_config.split("\n") if l])
    env.user = ssh_config["User"]
    env.hosts = ["127.0.0.1:%s" % (ssh_config["Port"])]
    env.host_string = env.hosts[0]    # We need to explicitly specify this for sudo and run.
    env.key_filename = ssh_config["IdentityFile"]
    print env.key_filename


def env_development():
    env.user = 'gituser'  # TODO: create a more elegant solution in future
    env.hosts = [env.project_sites['development']['NAME']]
    env.host_string = env.hosts[0]
    env.path = '/var/www/dev/%(project_name)s' % env


def env_production():
    env.user = 'gituser'
    env.hosts = [env.project_sites['production']['NAME']]
    env.host_string = env.hosts[0]
    env.path = '/var/www/prod/%(project_name)s' % env


##########################
# User management
##########################

def server_create_user(name, target):
    "Create user on the deployment and production servers"
    print("This command can only be executed by the root user")
    env.user = 'root'
    if target == 'dev':
        env.hosts = [env.project_sites['development']['NAME']]
    elif target == 'prod':
        env.hosts = [env.project_sites['production']['NAME']]

    env.host_string = env.hosts[0]
    run('useradd -m {0}'.format(name))
    run('gpasswd -a {0} wheel'.format(name))
    run('passwd {0}'.format(name))
    print("Make sure that the wheel group has sudo rights")
    print("ssh root@[yourserver]")
    print("run visudo manually and uncomment the %wheel group")


##########################
# Server-side stuff
##########################


def server_setup_standardpackages():
    sudo('pacman -S tmux htop git-core --noconfirm')


def server_setup_fullsystemupgrade():
    sudo('pacman -Syyu --noconfirm')


def server_setup_community_repo():
    run('echo \'echo "[archlinuxfr]" >> /etc/pacman.conf\' | sudo -s')
    run('echo \'Server = http://repo.archlinux.fr/$arch\' | sudo -s tee -a /etc/pacman.conf')
    run('echo \'echo " " project_home_stringpacman.conf\' | sudo -s')
    sudo('pacman -Syy yaourt --noconfirm')


def server_setup_mirror():
    """Installs necessary packages on host, depending on distro specified"""
    # Here are the arch-specific installs
    country = "Singapore"
    mirror_url = "http://www.archlinux.org/mirrorlist/?country={0}&protocol=ftp&protocol=http&ip_version=4&use_mirror_status=on".format(country)
    create_tmpfile = run('mktemp --suffix=-mirrorlist')
    tmpfile = create_tmpfile
    run('wget -qO- "{0}" | sed "s/^#Server/Server/g" > "{1}"'.format(mirror_url, tmpfile))
    print('Backing up the original mirrorlist...')
    sudo('mv -if /etc/pacman.d/mirrorlist /etc/pacman.d/mirrorlist.orig;')
    print('Rotating the new list into place...')
    sudo('mv -i "{0}" /etc/pacman.d/mirrorlist;'.format(tmpfile))


def server_setup_bash_profile():
    sudo("echo \"PS1='\\[\\033[0;31m\\]\\H \\l \\[\\033[1;33m\\]\\d \\[\\033[1;36m\\]\\t\\[\\033[0;32m\\] |\\w|\\[\\033[0m\\]\n\\u\\$ ';\" > ~/.bash_profile")


def server_setup_base():
    sudo('pacman -Syy --noconfirm')
    sudo('pacman -S tzdata')
    sudo('pacman -Sy pacman --noconfirm')
    sudo('pacman -S base-devel --noconfirm')
    sudo('pacman -S filesystem --force --noconfirm')
    sudo('rm /etc/profile.d/locale.sh')


def server_setup_python():
    sudo('pacman -S python2 --noconfirm')
    sudo('ln -s /usr/bin/python2 /usr/local/bin/python')  # handle arch-specific quirk
    sudo('pacman -S python2-distribute --noconfirm')
    sudo('pacman -S python2-pip --noconfirm')
    sudo('pip2 install virtualenvwrapper')


def server_setup_python_env():
    sudo('echo \'export WORKON_HOME=$HOME/.virtualenvs\' >> ~/.bash_profile')
    sudo('echo \'export PROJECT_HOME=$HOME/work\' >> ~/.bash_profile')
    sudo('echo \'source `which virtualenvwrapper.sh`\' >> ~/.bash_profile')
    with prefix(env.activate):
        sudo('mkdir $PROJECT_HOME')


def server_setup(user, target):
    if target == 'vagrant':
        vagrant_init(name=env.project_name)
    elif target == 'dev':
        env_development()
        env.user = user
    elif target == 'prod':
        env_production()

    #server_setup_mirror()
    server_setup_bash_profile()
    #server_setup_base()
    #server_setup_community_repo()
    #server_setup_fullsystemupgrade()
    #server_setup_standardpackages()
    #server_setup_python()
    #server_setup_python_env()


##########################
# Vagrant related stuff
##########################


def vagrant_box_add(name='project', distro='arch'):
    if distro == 'arch':
        distro_version = 'archlinux-20110919-64'
        distro_url = 'http://ftp.heanet.ie/mirrors/sourceforge/v/project/va/vagrantarchlinx/2011.08.19/archlinux_2011.08.19.box'
    local("vagrant box add {0}-{1} {2}".format(name, distro_version, distro_url))


def vagrant_init(name='project', distro='arch'):
    if distro == 'arch':
        distro_version = 'archlinux-20110819-64'
    local("vagrant init {0}-{1}".format(name, distro_version))
    local("vagrant up")
    raw_ssh_config = subprocess.Popen(["vagrant", "ssh-config"], stdout=subprocess.PIPE).communicate()[0]
    ssh_config = dict([l.strip().split() for l in raw_ssh_config.split("\n") if l])
    env.user = ssh_config["User"]
    env.hosts = ["127.0.0.1:%s" % (ssh_config["Port"])]
    env.host_string = env.hosts[0]    # We need to explicitly specify this for sudo and run.
    env.key_filename = ssh_config["IdentityFile"]


def vagrant_dostuff():
    require('hosts', provided_by=[vagrant_init(name='bbox')])
    #server_setup_clean()
    #server_setup_community_repo()
    #server_setup_fullsystemupgrade()
    server_setup_standardpackages()
    server_setup_python()


##########################
# Git related stuff
##########################


def git_aliases():
    local('git config --global alias.st status')
    local('git config --global alias.ci commit')
    local('git config --global alias.br branch')
    local('git config --global alias.co checkout')
    local('git config --global alias.p push')
    local('git config --global alias.pl pull')
    local('git config --global alias.lg "log --graph --pretty=format:\'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset\' --abbrev-commit --date=relative"')
    local('git config --global color.ui true')


##########################
# Mac OS X related stuff
##########################


def mac_port_setup():
    PACKAGES = ['vim +python27', 'htop', 'openssh']
    for item in PACKAGES:
        local('sudo port -v install {0}'.format(item))


def mac_set_locale():
    locale_vars = ['LANG', 'LC_COLLATE', 'LC_CTYPE', 'LC_MESSAGES', \
            'LC_MONETARY', 'LC_NUMERIC', 'LC_TIME', 'LC_ALL']
    for item in locale_vars:
        local("echo 'export {0}=\"en_US.UTF-8\"' >> ~/.bash_profile".format(item))
    local('source ~/.bash_profile')


##########################
# Database related stuff
##########################


def mac_port_postgresql():
    """
    Various standard tools that we need when setting up a mac machine.
    """
    local('sudo port -v install postgresql90 postgresql90-server')
    local('sudo mkdir -p /opt/local/var/db/postgresql90/defaultdb')
    local('sudo chown postgres:postgres /opt/local/var/db/postgresql90/defaultdb')
    local('sudo su postgres -c \'/opt/local/lib/postgresql90/bin/initdb -D /opt/local/var/db/postgresql90/defaultdb\'')
    local('sudo port -v load postgresql90-server')
    # setting postgresql90 as the default client so /opt/local/bin/createuser and etc cmds
    # become available
    local('sudo port select --set postgresql postgresql90')


def mac_port_postgresql_launch():
    local('launchctl load -w /Library/LaunchDaemons/org.macports.postgresql90-server.plist')


def setupdb():
    """
    Generic.
    postgresql db and user creation for a django project.
    """
    print("Creating a new postgresql user and db based on our settings.py")
    with prefix(env.activate):
        local('echo $VIRTUAL_ENV')
        local('psql -U postgres -c "CREATE ROLE {0} WITH PASSWORD \'{1}\' NOSUPERUSER CREATEDB NOCREATEROLE LOGIN;"'\
                .format(db['default']['USER'], db['default']['PASSWORD']))
        local('psql -U postgres -c "CREATE DATABASE {0} WITH OWNER={1} TEMPLATE=template0 ENCODING=\'utf-8\';"'\
                .format(db['default']['NAME'], db['default']['USER']))


def syncdb():
    with prefix(env.activate):
        local("./manage.py collectstatic --noinput")
        local("./manage.py syncdb --noinput")
        local("./manage.py migrate --all")


def loaddata():
    with prefix(env.activate):
        local("./manage.py loaddata fixtures/start_data.json")


def deploy(target):
    if target == "dev":
        env_development()
    elif target == "prod":
        env_production()
    else:
        print("Use `fab deploy:prod` or `fab deploy:dev`")
        return
    import time
    env.release = time.strftime('%Y%m%d_%H%M%S')
    local('git archive --format=tar master | gzip > %(release)s.tar.gz' % env)
    put('%(release)s' % env, '%(path)s/packages/' % env)
