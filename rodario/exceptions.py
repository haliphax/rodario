""" Exceptions for rodario framework """


class InvalidActorException(Exception):

    """ Raised when a referenced actor does not exist """

    pass


class InvalidProxyException(Exception):

    """ Raised when a proxy is not given a valid object to wrap """

    pass


class UUIDInUseException(Exception):

    """ Raised during UUID registration if the UUID is already taken """

    pass


class RegistrationException(Exception):

    """ Raised when actor registration fails """

    pass

class EmptyClusterException(Exception):

    """ Raised when a message is passed to an empty cluster channel """

    pass
