from typing import NamedTuple

from faaspact_verifier.abc import (
    NotificationGateway as NotificationGatewayABC,
    PactBrokerGateway as PactBrokerGatewayABC,
    Verifier as VerifierABC
)
from faaspact_verifier.gateways import LoggerNotificationGateway, PactBrokerGateway, PactmanVerifier


class Context(NamedTuple):
    notification_gateway: NotificationGatewayABC
    pact_broker_gateway: PactBrokerGatewayABC
    verifier: VerifierABC


def create_default_context(host: str, username: str, password: str) -> Context:
    return Context(
        notification_gateway=LoggerNotificationGateway(),
        pact_broker_gateway=PactBrokerGateway(
            host=host,
            username=username,
            password=password
        ),
        verifier=PactmanVerifier()
    )
