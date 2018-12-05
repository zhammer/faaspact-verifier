from abc import ABC, abstractmethod
from typing import List

from faaspact_verifier.definitions import Pact, VerificationResult


class PactBrokerGateway(ABC):
    """Gateway to a pact broker."""

    @abstractmethod
    def fetch_provider_pacts(self, provider: str) -> List[Pact]:
        ...

    @abstractmethod
    def provide_verification_results(self,
                                     provider_version: str,
                                     pact: Pact,
                                     verification_results: List[VerificationResult]) -> None:
        ...
