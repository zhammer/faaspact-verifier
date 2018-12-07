from contextlib import contextmanager
from typing import Callable, Generator, Optional

from faaspact_verifier.types import AlwaysFixture


user_always: Optional[AlwaysFixture] = None


def always(func: Callable[[], Generator]) -> AlwaysFixture:
    """Decorator that registers an 'always' fixture, which is always run before all provider
    state fixtures and faasport call.
    """
    global user_always

    if user_always is not None:
        raise RuntimeError('Multiple definitions of @always fixture.')

    as_context_manager = contextmanager(func)
    user_always = as_context_manager
    return as_context_manager
