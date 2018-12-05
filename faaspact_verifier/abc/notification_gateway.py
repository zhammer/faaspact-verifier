from abc import ABC, abstractmethod
from typing import List

from faaspact_verifier.definitions import Pact, VerificationResult
from faaspact_verifier.types import EmulatorResult


class NotificationGateway(ABC):

    @abstractmethod
    def announce_job_results(self,
                             pacts: List[Pact],
                             emulator_results_list: List[List[EmulatorResult]],
                             verification_results_list: List[List[VerificationResult]],
                             results_published: bool,
                             succeeded: bool) -> None:
        ...
