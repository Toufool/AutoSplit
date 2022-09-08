# https://pyinstaller.org/en/stable/hooks-config.html `hook_api` is a PostGraphAPI

from collections.abc import Iterable

from _typeshed import StrOrBytesPath
from PyInstaller.building.build_main import Analysis  # type: ignore[import]

#


class PostGraphAPI:
    @property
    def __path__(self) -> tuple[str, ...] | None: ...
    @property
    def analysis(self) -> Analysis: ...
    def add_datas(self, list_of_tuples: Iterable[tuple[StrOrBytesPath, StrOrBytesPath]]) -> None: ...
