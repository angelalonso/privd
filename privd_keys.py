import gnupg
import subprocess
"""
Class to manage keys used for encryption and decryption

I'm using bash directly for the gnupg library does not seem to produce proper decryptable files for binary files

"""
# TODO: create typical functions too: delete, list...
class Key(object):
  """ The GPG keys we will use and reuse
  """
  def __init__(self, key_email):
    """ Returns a File whose path is path
    """
    #self.id = key_email
    self.id = 'aux@foo.foo'

    checkcmd = 'gpg --list-keys ' + self.id + ' | grep pub'
    try:
      subprocess.check_output([checkcmd], shell=True)
      print('Key FOUND')
    except subprocess.CalledProcessError as e:
      #TODO: ask user for confirmation before we create it?
      print('Key not found, generating...')
      self.create_key()


  def create_key(self):
    # TODO: create key with bash instead
    key_config = 'Key-Type: RSA\n Key-Length: 4096\n Name-Real: Privd Key\n Name-Email: ' + self.id + '\n Expire-Date: 0'
    key_config_file = './key.config'
    key_config_buffer = open(key_config_file,"w")
    key_config_buffer.write(key_config)
    key_config_buffer.close()

    cmd = 'gpg --batch --gen-key ' + key_config_file
    cmd_run = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True)