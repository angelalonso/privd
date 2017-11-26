import gnupg
"""
Class to manage keys used for encryption and decryption

I'm using bash directly for the gnupg library does not seem to produce proper decryptable files for binary files

"""
class Key(object):
  """ The GPG keys we will use and reuse
  """
  def __init__(self, gpghome):
    """ Returns a File whose path is path
    """
    self.gpghome = gpghome
    # TODO: add pubring and secring names to config
    self.gpg = gnupg.GPG(binary='/usr/bin/gpg',
      homedir=self.gpghome,
      keyring='privd_pubring.gpg',
      secring='privd_secring.gpg')
    self.gpg.encoding = 'utf-8'

  def create_key(self):
    self.key_input = self.gpg.gen_key_input(
      key_type='RSA',
      key_length=4096)

    self.key = self.gpg.gen_key(self.key_input)

  def get_fingerprint(self):
    # IS THIS NEEDED?
    # TODO: make sure only one key is there, needed to clean up?
    self.id = self.gpg.list_keys()[0]['fingerprint']
    return self.id
  
