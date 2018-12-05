class FaaspactVerifierException(Exception):
    """Base exception class."""


class UnsupportedProviderStateError(FaaspactVerifierException):
    """Error raised upon encountering a provider state in a pact that is not supported by the
    consumer.
    """


class PactBrokerError(FaaspactVerifierException):
    """Eror raised upon encountering an error with the pact broker."""
