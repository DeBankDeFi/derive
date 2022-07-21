from abc import ABC, abstractmethod


class DidNotEnable(Exception):
    """
    The integration could not be enabled due to a trivial user error like
    `flask` not being installed for the `FlaskIntegration`.

    This exception is silently swallowed for default integrations, but reraised
    for explicitly enabled integrations.
    """


class BaseIntegration(ABC):
    @property
    @abstractmethod
    def identifier(self) -> str:
        pass

    def setup(self):
        self.setup_trace()
        self.setup_logging()

    def setup_trace(self):
        pass

    def setup_logging(self):
        pass
