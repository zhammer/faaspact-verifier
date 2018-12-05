from typing import Dict, List

from pactman.verifier import verify

from faaspact_verifier.abc import Verifier as VerifierABC
from faaspact_verifier.definitions import Error, Interaction, Pact, Response, VerificationResult
from faaspact_verifier.gateways import pactman_adapters
from faaspact_verifier.types import EmulatorResult


class PactmanVerifier(VerifierABC):
    """Verifier that wraps around pactman's verification logic."""

    def verify_pact(self,
                    pact: Pact,
                    emulator_results: List[EmulatorResult]) -> List[VerificationResult]:
        return [self._verify_interaction(interaction, emulator_result)
                for interaction, emulator_result in zip(pact.interactions, emulator_results)]

    def _verify_interaction(self,
                            interaction: Interaction,
                            emulator_result: EmulatorResult) -> VerificationResult:
        if isinstance(emulator_result, Error):
            return VerificationResult(False, emulator_result.message)

        pactman_interaction = _build_pactman_interaction(interaction)
        pactman_result = pactman_adapters.PactmanResult()
        pactman_pact = pactman_adapters.PactmanPact
        pactman_response = _build_pactman_response(emulator_result)
        verifier = verify.ResponseVerifier(pactman_pact, pactman_interaction, pactman_result)
        if verifier.verify(pactman_response):
            return VerificationResult(True)
        else:
            return VerificationResult(False, pactman_result.messages)


def _build_pactman_response(response: Response) -> pactman_adapters.PactmanResponse:
    return pactman_adapters.PactmanResponse(
        response.status,
        response.headers,
        response.body
    )


def _build_pactman_interaction(interaction: Interaction) -> Dict:
    return _drop_none_values({
        'status': interaction.response.status,
        'headers': interaction.response.headers,
        'body': interaction.response.body,
        'matchingRules': interaction.response.matching_rules or {}
    })


def _drop_none_values(dictionary: Dict) -> Dict:
    """Drops fields from a dictionary where value is None.

    >>> _drop_none_values({'greeting': 'hello', 'name': None})
    {'greeting': 'hello'}
    """
    return {key: value for key, value in dictionary.items() if value is not None}
