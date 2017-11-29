import subprocess

class Syncer(object):
  """ A syncer object which contains:
  folders to be encrypted
  details about the encryption
  details to identify newer versions -> Moved to Files maybe?
  """

  def __init__(self, config):
    """ Returns a File whose path is path
    """
    print(config.folders)
