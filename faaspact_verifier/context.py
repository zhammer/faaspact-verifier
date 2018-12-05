from typing import NamedTuple

from faaspact_verifier.abc import (
    PactBrokerGateway as PactBrokerGatewayABC,
    Verifier as VerifierABC
)
from faaspact_verifier.gateways import PactBrokerGateway, PactmanVerifier


class Context(NamedTuple):
    pact_broker_gateway: PactBrokerGatewayABC
    verifier: VerifierABC


def create_default_context(host: str, username: str, password: str) -> Context:
    return Context(
        pact_broker_gateway=PactBrokerGateway(
            host=host,
            username=username,
            password=password
        ),
        verifier=PactmanVerifier()
    )
