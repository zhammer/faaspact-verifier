from typing import Dict, FrozenSet

from faaspact_verifier.context import Context
from faaspact_verifier.entities import emulator, job
from faaspact_verifier.types import Faasport, ProviderStateFixture


def use_verifier(context: Context,
                 provider: str,
                 provider_state_fixture_by_descriptor: Dict[str, ProviderStateFixture],
                 faasport: Faasport,
                 publish_results: bool,
                 failon: FrozenSet,
                 provider_version: str) -> bool:
    pacts = context.pact_broker_gateway.fetch_provider_pacts(provider)

    emulator_results_list = [
        emulator.emulate_pact_interactions(pact, provider_state_fixture_by_descriptor, faasport)
        for pact in pacts
    ]

    verification_results_list = [context.verifier.verify_pact(pact, emulator_results)
                                 for pact, emulator_results in zip(pacts, emulator_results_list)]

    if publish_results:
        for pact, verification_results in zip(pacts, verification_results_list):
            context.pact_broker_gateway.provide_verification_results(
                provider_version,
                pact,
                verification_results
            )

    succeeded = job.succeeded(zip(pacts, verification_results_list), failon)

    context.notification_gateway.announce_job_results(
        pacts=pacts,
        emulator_results_list=emulator_results_list,
        verification_results_list=verification_results_list,
        results_published=publish_results,
        succeeded=succeeded
    )

    return succeeded
