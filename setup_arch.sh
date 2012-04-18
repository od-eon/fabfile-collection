#!/bin/sh

#####################
# Arch Linux
#####################

[ "$UID" != 0 ] && su=sudo

country='Singapore'
url="http://www.archlinux.org/mirrorlist/?country=$country&protocol=ftp&protocol=http&ip_version=4&use_mirror_status=on"

tmpfile=$(mktemp --suffix=-mirrorlist)

# Get latest mirror list and save to tmpfile
wget -qO- "$url" | sed 's/^#Server/Server/g' > "$tmpfile"

# Backup and replace current mirrorlist file
{ echo "Backing up the original mirrorlist..."
  $su mv -i /etc/pacman.d/mirrorlist /etc/pacman.d/mirrorlist.orig; } &&
{ echo "Rotating the new list into place..."
  $su mv -i "$tmpfile" /etc/pacman.d/mirrorlist; }
echo "PS1='\[\033[0;31m\]\H \l \[\033[1;33m\]\d \[\033[1;36m\]\t\[\033[0;32m\] |\w|\[\033[0m\]\n\u\$ ';" > ~/.bash_profile
source ~/.bash_profile
sudo pacman -Syy --noconfirm
sudo pacman -S tzdata                                     # say no to upgrade packman and yes for tzdata install
sudo pacman -Sy pacman --noconfirm 
sudo pacman -S base-devel --noconfirm 
sudo pacman -S filesystem --force --noconfirm
sudo rm /etc/profile.d/locale.sh
echo 'echo "[archlinuxfr]" >> /etc/pacman.conf' | sudo -s
echo 'echo "Server = http://repo.archlinux.fr/$arch" >> /etc/pacman.conf' | sudo -s
echo 'echo " " >> /etc/pacman.conf' | sudo -s
sudo pacman -Syy yaourt --noconfirm           # yaourt is required for us to community contributed packages
sudo pacman -Syyu --noconfirm                     # full system upgrade
sudo pacman -S tmux htop git-core --noconfirm

# Get ready for python stuff!
sudo pacman -S python2 --noconfirm
sudo pacman -S python2-distribute --noconfirm
sudo pacman -S python2-pip --noconfirm
sudo pip2 install virtualenvwrapper               # note that there is a arch linux python2 python bug in the /usr/bin/virtualenvwrapper.sh, when checking "which python".

# Update .bash_profile
echo "export WORKON_HOME=$HOME/.virtualenvs" >> ~/.bash_profile
echo "export PROJECT_HOME=$HOME/work" >> ~/.bash_profile
echo "source /usr/bin/virtualenvwrapper.sh" >> ~/.bash_profile
source ~/.bash_profile
mkdir $PROJECT_HOME
