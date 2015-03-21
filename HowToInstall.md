# step-by-step install of ga-bitbot #

## Using Linux Mint x64 OS ##

`*`Note: Replace vmuser with the user home directory in the paths given below.

### Install Required Packages ###
sudo apt-get install make gcc g++ libssl-dev git curl

### Install Node ###
Known Issue: On UNIX platforms, make sure that the destination file path doesn't contain whitespace: /home/user/My Projects/node won't work.

cd $home

mkdir config

cd config

git clone https://github.com/joyent/node.git

cd node

git checkout v0.8.16 #Try checking nodejs.org for what the stable version is

./configure

make

sudo make install


### Install Redis ###
cd $home

cd config

wget http://redis.googlecode.com/files/redis-2.6.7.tar.gz

tar -zxvf `*`.tar.gz

rm `*`.tar.gz

cd redis`*`

make

cd /usr/local/bin

sudo ln -s /home/vmuser/config/redis-2.6.7/src/redis-server redis-server

`*`replace vmuser with the user home directory.

### Install ga-bitbot ###
cd $home

cd config

git clone https://code.google.com/p/ga-bitbot/


### Install Required Python Libraries ###

curl http://python-distribute.org/distribute_setup.py | sudo python

curl https://raw.github.com/pypa/pip/master/contrib/get-pip.py | sudo python

rm `*`.gz

sudo pip install redis

sudo pip install boto

sudo pip install defusedxml

### Install PYPY ###
cd $home

cd config

#for 64 bit linux systems:

wget http://buildbot.pypy.org/nightly/trunk/pypy-c-jit-latest-linux64.tar.bz2

#or 32 bit systems

wget http://buildbot.pypy.org/nightly/trunk/pypy-c-jit-latest-linux.tar.bz2


tar -xvjf `*`.tar.bz2

rm `*`.tar.bz2

mv pypy`*` pypy

cd /usr/local/bin

sudo ln -s /home/vmuser/config/pypy/bin/pypy pypy

`*`replace vmuser with the user home directory.

### Install PIP for PYPY ###

cd /home/vmuser/

wget http://python-distribute.org/distribute_setup.py

wget https://raw.github.com/pypa/pip/master/contrib/get-pip.py

/home/vmuser/config/pypy/bin/pypy distribute\_setup.py

/home/vmuser/config/pypy/bin/pypy get-pip.py

rm distribute\_setup.py

rm get-pip.py


### Install additional libraries for PYPY ###
/home/vmuser/config/pypy/bin/pip install defusedxml

`*`replace vmuser with the user home directory.