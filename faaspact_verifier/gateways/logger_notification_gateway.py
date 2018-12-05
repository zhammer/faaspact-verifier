from typing import List

from colorama import Fore, Style

from faaspact_verifier.abc import NotificationGateway as NotificationGatewayABC
from faaspact_verifier.definitions import Pact, VerificationResult
from faaspact_verifier.types import EmulatorResult


class LoggerNotificationGateway(NotificationGatewayABC):

    def announce_job_results(self,
                             pacts: List[Pact],
                             emulator_results_list: List[List[EmulatorResult]],
                             verification_results_list: List[List[VerificationResult]],
                             results_published: bool,
                             succeeded: bool) -> None:
        """The ugliest logger."""
        lines: List[str] = []
        for group in zip(pacts, emulator_results_list, verification_results_list):
            lines += _format_pact_results(*group)
        if results_published:
            lines.append(Fore.BLACK + '**Results for passing pacts were published**')

        print('\n'.join(lines))
        print(Style.RESET_ALL)


def _format_pact_results(pact: Pact,
                         emulator_results: List[EmulatorResult],
                         verification_results: List[VerificationResult]) -> List[str]:
    lines: List[str] = []
    succeeded = all(verification_result.verified for verification_result in verification_results)
    lines.append(
        (Fore.GREEN if succeeded else Fore.RED) +
        f'pact between consumer "{pact.consumer_name}" and provider "{pact.provider_name}"'
    )
    lines.append(Fore.BLUE + f'tags: {set(pact.tags)}')
    for index, verification_result in enumerate(verification_results):
        if not verification_result.verified:
            lines.append(Fore.CYAN +
                         f'Failed interaction {index} with message: "{verification_result.reason}"')

    return lines
