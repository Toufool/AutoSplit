import typing
import PyQt6.sip


class QTest(PyQt6.sip.simplewrapper):
    # Email sent to pyqt@riverbankcomputing.com
    @typing.overload
    @staticmethod
    def qWait(ms: int) -> None: ...
    @typing.overload
    def qWait(self, ms: int) -> None: ...
