from contextlib import contextmanager
from typing import Callable, Dict

from faaspact_verifier.types import ProviderStateFixture, UserProviderStateFixture


user_provider_state_fixture_by_descriptor: Dict[str, ProviderStateFixture] = {}


def provider_state(descriptor: str) -> Callable[[UserProviderStateFixture], ProviderStateFixture]:
    global user_provider_state_fixture_by_descriptor

    def provider_state_collector(func: UserProviderStateFixture) -> ProviderStateFixture:
        if descriptor in user_provider_state_fixture_by_descriptor:
            raise RuntimeError(f'A provider_state fixture for {descriptor} is already defined.')

        as_context_manager = contextmanager(func)
        user_provider_state_fixture_by_descriptor[descriptor] = as_context_manager
        return as_context_manager

    return provider_state_collector
