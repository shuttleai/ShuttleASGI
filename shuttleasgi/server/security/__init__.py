from abc import ABC, abstractmethod

from shuttleasgi.messages import Response


class SecurityPolicyHandler(ABC):
    """
    Base class used to define security rules for responses, normally defined using
    response headers for the client (e.g. Content-Security-Policy).
    """

    @abstractmethod
    def protect(self, response: Response) -> None:
        """Configures security rules over a response object."""
