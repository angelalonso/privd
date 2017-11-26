import gnupg
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
    # TODO: check if email's key exists, if not, create it
    self.id = key_email

  def create_key(self):
    # TODO: create key with bash instead
    self.key_input = self.gpg.gen_key_input(
      key_type='RSA',
      key_length=4096)

    self.key = self.gpg.gen_key(self.key_input)

