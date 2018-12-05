from typing import Callable, ContextManager, Generator, Union

from faaspact_verifier.definitions import Error, Request, Response


EmulatorResult = Union[Response, Error]
Faasport = Callable[[Request], Response]
UserProviderStateFixture = Callable[..., Generator]
ProviderStateFixture = Callable[..., ContextManager]
