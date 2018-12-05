from typing import Any, Dict, List, NamedTuple, Optional


class PactmanResponse(NamedTuple):
    status_code: int
    headers: Dict
    body: Optional[Dict] = None

    @property
    def text(self) -> str:
        return str(self)

    def json(self) -> Dict:
        return self.body or {}


class PactmanResult:
    def __init__(self) -> None:
        self._messages: List[str] = []

    def fail(self, message: str, path: Any = None) -> bool:
        self._messages.append(message)
        return False

    @property
    def messages(self) -> str:
        return 'Pactman messages: ' + str(self._messages)


class PactmanPact:
    semver = {'major': 3}
