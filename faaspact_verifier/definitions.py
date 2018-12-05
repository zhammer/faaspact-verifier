from typing import Any, Dict, FrozenSet, NamedTuple, Optional, Tuple, cast


class Response(NamedTuple):
    headers: Dict
    status: int
    body: Optional[Dict] = None
    matching_rules: Optional[Dict] = None


class Request(NamedTuple):
    headers: Dict
    path: str
    method: str
    query: Optional[Dict] = None
    body: Optional[str] = None


class ProviderState(NamedTuple):
    descriptor: str
    params: Optional[Dict[str, Any]] = None


class Interaction(NamedTuple):
    request: Request
    response: Response
    provider_states: Tuple[ProviderState, ...]


class Pact(NamedTuple):
    consumer_version: str
    pact_json: Dict
    pact_version: str
    tags: FrozenSet[str] = frozenset()

    @property
    def interactions(self) -> Tuple[Interaction, ...]:
        return _pluck_interactions(self)

    @property
    def provider_name(self) -> str:
        return cast(str, self.pact_json['provider']['name'])

    @property
    def consumer_name(self) -> str:
        return cast(str, self.pact_json['consumer']['name'])


class VerificationResult(NamedTuple):
    verified: bool
    reason: Optional[str] = None


class Error(NamedTuple):
    message: str
    traceback: Optional[str] = None


def _pluck_interactions(pact: Pact) -> Tuple[Interaction, ...]:
    return tuple([_pluck_interaction(raw_interaction)
                 for raw_interaction in pact.pact_json['interactions']])


def _pluck_interaction(raw_interaction: Dict) -> Interaction:
    raw_provider_states = raw_interaction.get('providerStates')
    if raw_provider_states:
        provider_states = tuple([_pluck_provider_state(raw_provider_state)
                                 for raw_provider_state in raw_provider_states])
    else:
        provider_states = tuple()

    request = _pluck_request(raw_interaction['request'])
    response = _pluck_response(raw_interaction['response'])

    return Interaction(
        request=request,
        provider_states=provider_states,
        response=response
    )


def _pluck_request(raw_request: Dict) -> Request:
    return Request(
        headers=raw_request.get('headers', {}),
        path=raw_request['path'],
        method=raw_request['method'],
        query=raw_request.get('query', {}),
        body=raw_request.get('body', {})
    )


def _pluck_response(raw_response: Dict) -> Response:
    return Response(
        status=raw_response['status'],
        headers=raw_response.get('headers', {}),
        body=raw_response.get('body'),
        matching_rules=raw_response.get('matchingRules')
    )


def _pluck_provider_state(raw_provider_state: Dict) -> ProviderState:
    return ProviderState(**raw_provider_state)
