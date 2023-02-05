class ChpipException(Exception):
    msg_fmt = 'An unknown exception occurred.'

    def __init__(self, *args, **kwargs):
        msg = self.msg_fmt.format(*args, **kwargs)
        super(ChpipException, self).__init__(msg)


class NoAvailableIndex(ChpipException):
    msg_fmt = 'There is no available index to change. Please use `chpip set` to set one.'


class IndexNameNotFound(ChpipException):
    msg_fmt = 'There is no index with name {name}. Please use `chpip set` to set one.'


class InvalidIndexName(ChpipException):
    msg_fmt = 'Invalid index name `{name}`. Cannot use revered name.'


class InvalidIndexURL(ChpipException):
    msg_fmt = 'Invalid base URL `{url}` for Python package index.'


class RequestError(ChpipException):
    msg_fmt = 'Request to `{url}` error. Reason: {reason}.'
