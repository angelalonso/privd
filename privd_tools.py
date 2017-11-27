import os

def correct_path(path):
  new_path = path.replace('$HOME', os.environ['HOME'])
  return new_path
