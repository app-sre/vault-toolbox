class InvalidPathError(Exception):
    def __init__(self, path):
        self.path = path
        message = "`{}` is an invalid path. Expected format: <mountpoint>/<path>".format(path)
        super(Exception, self).__init__(message)
