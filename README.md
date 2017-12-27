# privd
Tool to syncronize and encrypt files on a folder into a cloud storage service's folder (eg.: Dropbox)

It should be compatible with Linx and MacOs

# Requirements
- Python3
- gnupg, both as a package and as a python module
- pyyaml

apt-get update && apt-get install gnupg python3
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

# Known Issues

## KeyError when running with an existing statusfile
Just delete that statusfile

# TODO List (in Prio order):

- Automate config, have the script run with as little config as possible.
- Make it possible to extract GPG key frm privd.py, document process to configure a second machine. 
