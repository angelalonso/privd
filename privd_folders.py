import subprocess

class Folder(object):
    """ A folder object which contains:
    data to be encrypted
    details about the encryption
    details to identify newer versions
  """

  def __init__(self, path):
    """ Returns a File whose path is path
    """
    self.path = path
