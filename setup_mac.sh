#!/bin/sh

#####################
# Mac OS X
#####################

# Mac personal apps
# TODO: use wget to automate these :-)
# manually download and install skype
# manually download and install dropbox
# manually download and install vuze
# manually download and install vlc and vlcstreamer

# Mac Developer's set-up
# manually download and install Xcode
# manually download and install macports
# In Xcode download and install command line tools (in Xcode)
sudo port -v selfupdate
# upgrade to the latest bash version and make our user use it
sudo port -v install bash
echo 'echo "/opt/local/bin/bash" >> /etc/shells' | sudo -s
chsh -s /opt/local/bin/bash

# Some core packages we need on our mac, via macports
sudo port -v install wget iterm2 python27 git-core
sudo port -v install vim +x11 +python27
sudo easy_install-2.7 pip                              # easy_install-2.7 should be available when python27-distribute is installed by port as a dependency on one of the above
sudo pip install virtualenvwrapper

# Update .bash_profile
echo 'PS1="\[\033[0;31m\]\H \l \[\033[1;33m\]\d \[\033[1;36m\]\t\[\033[0;32m\] |\w|\[\033[0m\]\n\u\$ ";' > ~/.bash_profile
echo 'export PATH="/opt/local/library/Frameworks/Python.framework/Versions/2.7/bin:$PATH";' >> ~/.bash_profile
echo 'export PATH="/opt/local/bin:/opt/local/sbin:/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin:/usr/X11/bin:$PATH";' >> ~/.bash_profile
echo 'export WORKON_HOME=$HOME/.virtualenvs' >> ~/.bash_profile
echo 'export PROJECT_HOME=$HOME/work' >> ~/.bash_profile
echo 'source virtualenvwrapper.sh' >> ~/.bash_profile
source ~/.bash_profile
