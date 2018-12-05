import contextlib
import inspect
import traceback
from typing import Callable, Dict, FrozenSet, Generator, List, Tuple

from faaspact_verifier.definitions import Error, Interaction, Pact, ProviderState
from faaspact_verifier.exceptions import UnsupportedProviderStateError
from faaspact_verifier.types import EmulatorResult, Faasport, ProviderStateFixture


def emulate_pact_interactions(pact: Pact,
                              provider_state_fixture_by_descriptor: Dict[str, ProviderStateFixture],
                              faasport: Faasport) -> List[EmulatorResult]:
    return [_emulate_interaction(interaction, provider_state_fixture_by_descriptor, faasport)
            for interaction in pact.interactions]


def _emulate_interaction(interaction: Interaction,
                         provider_state_fixture_by_descriptor: Dict[str, ProviderStateFixture],
                         faasport: Faasport) -> EmulatorResult:
    try:
        provider_state_fixtures_with_params = _provider_state_fixtures_with_params(
            provider_state_fixture_by_descriptor,
            interaction.provider_states
        )
    except UnsupportedProviderStateError as e:
        return Error(message=str(e))

    with _use_provider_states(provider_state_fixtures_with_params):
        try:
            return faasport(interaction.request)
        except Exception:
            return Error(
                message='Provider raised an exception',
                traceback=traceback.format_exc()
            )


def _provider_state_fixtures_with_params(
        provider_state_fixture_by_descriptor: Dict[str, ProviderStateFixture],
        provider_states: Tuple[ProviderState, ...]
) -> List[Tuple[ProviderStateFixture, Dict]]:
    """Get a list of provider states fixtures for an interaction with their parameters.
    Raises an UnsupportedProviderStateError on the first provider state in an interaction
    that isn't supported by the provider.
    """
    provider_state_fixtures_with_params: List[Tuple[ProviderStateFixture, Dict]] = []
    for provider_state in provider_states:
        provider_state_fixture = provider_state_fixture_by_descriptor.get(provider_state.descriptor)
        if not provider_state_fixture:
            raise UnsupportedProviderStateError(
                f'Missing expected provider state: {provider_state}'
            )
        if provider_state.params:
            fixture_params = _pluck_parameter_names(provider_state_fixture)
            if not frozenset(provider_state.params.keys()) == fixture_params:
                raise UnsupportedProviderStateError(
                    'Expected provider state params dont match those of '
                    + f'provider. Expected: {provider_state}. Actual: {fixture_params}.'
                )
        provider_state_fixtures_with_params.append(
            (provider_state_fixture, provider_state.params or {})
        )

    return provider_state_fixtures_with_params


def _pluck_parameter_names(provider_state_fixture: Callable) -> FrozenSet[str]:
    """Pluck the parameter names of a function.

    >>> def hello(name: str, yell: bool = False) -> str:
    ...     greeting = f'Hello {name}!'; return greeting.upper() if yell else greeting
    >>> _pluck_parameter_names(hello) == frozenset({'name', 'yell'})
    True
    """
    signature = inspect.signature(provider_state_fixture)
    return frozenset(signature.parameters.keys())


@contextlib.contextmanager
def _use_provider_states(
        provider_state_fixtures_with_params: List[Tuple[ProviderStateFixture, Dict]]
) -> Generator:
    """Run all given provider states as a contextmanager."""
    with contextlib.ExitStack() as stack:
        for provider_state_fixture, params in provider_state_fixtures_with_params:
            stack.enter_context(provider_state_fixture(**params))

        yield
