# privd
Tool to syncronize and encrypt files on a folder into a cloud storage service's folder (eg.: Dropbox)

It should be compatible with Linx and MacOs

# TL;DR

cp config.yaml.template config.yaml

python3 privd.py

# Requirements
- Python3
- gnupg, both as a package and as a python module
- pyyaml
- rng-tools
- sudo

## Install requirements On Ubuntu
apt-get update && apt-get install gnupg python3 rng-tools sudo
pip3 install gnupg pyyaml

# Install
git clone https://github.com/angelalonso/privd

# Before you launch

Rename config.yaml.template to config.yaml and modify the following to your liking:
- mainfolder
- enc_mainfolder
- key_email
  - This is used to identify the GPG key we will be using. 
  - Default one should be fine, but you can change this if you want to reuse your own GPG key.
- folders > name, path
  - These are the folders that will be synced.
  - Set a full path on "path", or use $HOME. No other environment variables work for now.
  - Name is irrelevant

# How to run it

python3 <path where you cloned this repo>/privd.py

## Verbose mode

python3 <path where you cloned this repo>/privd.py -v

# How to configure a second machine

After you have successfully run privd on one machine, you can copy over the GPG keys to have it run on a second one, which is actually the purpose of this whole thing.

- In the 'old' machine:
python3 <path where you cloned this repo>/privd.py -e

Choose a folder to export to. 

HINT: this can also go into a mounted USB drive <wink>

- Install privd on the 'new' machine too.
Then, copy the folder to the new machine somehow.
HINT: you can use the previously mentioned USB drive <wink, wink>

python3 <path where you cloned this repo>/privd.py -i

Indicate the folder to import to.


# Known Issues

## KeyError when running with an existing statusfile
Just delete that statusfile

# TODO List (in Prio order):

- Document all functions properly
- Automate config, have the script run with as little config as possible.
- Create a tiny 'interactive' function to help configure a second machine. Maybe with an export and import parameter
