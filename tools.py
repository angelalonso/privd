import os

def correct_path(path):
    """ TOOL to replace environment variables on the go
    """
    # TODO: identify other environment vars (from $ to ...)
    new_path = path.replace('$HOME', os.environ['HOME'])
    return new_path

def get_timestamp(file):
    return format(os.stat(file).st_mtime)
