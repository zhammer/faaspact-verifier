from abc import ABC, abstractmethod
from typing import List

from faaspact_verifier.definitions import Pact, VerificationResult
from faaspact_verifier.types import EmulatorResult


class Verifier(ABC):

    @abstractmethod
    def verify_pact(self,
                    pact: Pact,
                    emulator_results: List[EmulatorResult]) -> List[VerificationResult]:
        ...
