from typing import Optional

from faaspact_verifier.types import Faasport


user_faasport: Optional[Faasport] = None


def faasport(func: Faasport) -> Faasport:
    """Decorator that registers the user's faasport function."""
    global user_faasport

    if user_faasport is not None:
        raise RuntimeError('Multiple definitions of faasport.')

    user_faasport = func
    return func
