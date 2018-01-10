#!/usr/bin/env bash

#If a command fails, make the whole script exit
#Treat unset variables as an error, and immediately exit.
#Disable filename expansion (globbing) upon seeing *, ?, etc..
#Produce a failure return code if any command errors
#set -euf -o pipefail

FLDR_MAIN=$(dirname $0)
FLDR_REMOTE="$HOME/Dropbox/.privd"
FLDR_ENC="${FLDR_REMOTE}/enc"
FILE_STATUS="${FLDR_REMOTE}/.status"
FLDR_LOCAL="$HOME/Private"
KEY_ID="privd@privd.foo"


remove_remote_data() {
  rm ${FILE_STATUS} 2>/dev/null
  rm -rf ${FLDR_ENC} 2>/dev/null
}
remove_local_data() {
  rm -rf ${FLDR_LOCAL} 2>/dev/null
}
remove_configfile() {
  rm ${FLDR_MAIN}/config.yaml 2>/dev/null
}
remove_keys() {
  gpg --delete-secret-keys ${KEY_ID}
  gpg --delete-keys ${KEY_ID}
}

first_from_scratch() {
  echo "TESTING case:"
  echo "- First run, from scratch"
  echo "- No remote data"
  echo "- No local data"
  echo "- No config file"
  echo "- No key present"
  echo "---- Press Enter to continue ----"
  read answer
  remove_remote_data
  remove_local_data
  remove_configfile
  remove_keys
  python3 ${FLDR_MAIN}/privd.py -v
}

from_import_remote_empty() {
  echo "TESTING case:"
  echo "First run, from an import"
  echo "- No remote data"
  echo "- No local data"
  echo "- Importing config file"
  echo "- Importing key"
  echo "---- Press Enter to continue ----"
  read answer
  remove_remote_data
  remove_local_data
  remove_configfile
  remove_keys
  python3 ${FLDR_MAIN}/privd.py -i
  python3 ${FLDR_MAIN}/privd.py -v
  # ERROR:
  #   KeyError: '$HOME/Private'

  # ERROR: FileNotFoundError: [Errno 2] No such file or directory: 'import/config.yaml'
  #   when using a folder that does not exist
}

from_import_remote_with_data() {
  echo "TESTING case:"
  echo "First run, remote has data"
  echo "- Some remote data"
  echo "- No local data"
  echo "- Importing config file"
  echo "- Importing key"
  echo "---- Press Enter to continue ----"
  read answer
  create_remote_data
  remove_local_data
  remove_configfile
  remove_keys
  python3 ${FLDR_MAIN}/privd.py -i
  python3 ${FLDR_MAIN}/privd.py -v
}

menu() {
  MODES="[from_clean|from_import|from_import_remote_data]"
  if [ "$1" == "" ]; then
    echo "ERROR! no parameters provided"
    echo " Usage:"
    echo " $0 $MODES"
    exit 2
  fi
  mode=$1
  case $mode in
  from_clean)
    first_from_scratch
    ;;
  from_import)
    from_import_remote_empty
    ;;
  from_import_remote_data)
    from_import_remote_with_data
    ;;
  esac

}

menu $@
