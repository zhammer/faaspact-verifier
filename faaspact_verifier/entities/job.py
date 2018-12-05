from typing import FrozenSet, Iterable, List, Tuple

from faaspact_verifier.definitions import Pact, VerificationResult


def should_fail(pact_with_verification_results: Iterable[Tuple[Pact, List[VerificationResult]]],
                failon: FrozenSet[str]) -> bool:
    for pact, verification_results in pact_with_verification_results:
        verified = all(verification_result.verified for verification_result in verification_results)
        if not verified and _overlap(pact.tags, failon):
            return False

    return True


def _overlap(set_a: FrozenSet, set_b: FrozenSet) -> bool:
    """Return True if there are overlapping items in set_a and set_b, otherwise return False.

    # Passes as both sets have element 'b'
    >>> _overlap(frozenset({'a', 'b'}), frozenset({'b', 'c'}))
    True

    # Fails as there are no similar elements
    >>> _overlap(frozenset({'a', 'b'}), frozenset({'c', 'd'}))
    False

    # Fails as one set is empty
    >>> _overlap(frozenset({'a', 'b'}), frozenset())
    False

    # Fails as both sets are empty
    >>> _overlap(frozenset(), frozenset())
    False
    """
    return not set_a.isdisjoint(set_b)
