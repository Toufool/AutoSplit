import typing

import PyQt6.sip

# Email sent to pyqt@riverbankcomputing.com


class QTest(PyQt6.sip.simplewrapper):
    @typing.overload
    @staticmethod
    def qWait(ms: int) -> None: ...
    @typing.overload
    def qWait(self, ms: int) -> None: ...
