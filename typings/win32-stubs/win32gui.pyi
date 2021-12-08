__all__=['', 'EnumFontFamilies', 'set_logger', 'LOGFONT', 'CreateFontIndirect', 'GetObject', 'GetObjectType', 'PyGetMemory', 'PyGetString', 'PySetString', 'PySetMemory', 'PyGetArraySignedLong', 'PyGetBufferAddressAndLen', 'FlashWindow', 'FlashWindowEx', 'GetWindowLong', 'GetClassLong', 'SetWindowLong', 'CallWindowProc', 'SendMessage', 'SendMessageTimeout', 'PostMessage', 'PostThreadMessage', 'ReplyMessage', 'RegisterWindowMessage', 'DefWindowProc', 'EnumWindows', 'EnumThreadWindows', 'EnumChildWindows', 'DialogBox', 'DialogBoxParam', 'DialogBoxIndirect', 'DialogBoxIndirectParam', 'CreateDialogIndirect', 'DialogBoxIndirectParam', 'EndDialog', 'GetDlgItem', 'GetDlgItemInt', 'SetDlgItemInt', 'GetDlgCtrlID', 'GetDlgItemText', 'SetDlgItemText', 'GetNextDlgTabItem', 'GetNextDlgGroupItem', 'SetWindowText', 'GetWindowText', 'InitCommonControls', 'InitCommonControlsEx', 'LoadCursor', 'SetCursor', 'GetCursor', 'GetCursorInfo', 'CreateAcceleratorTable', 'DestroyAccleratorTable', 'LoadMenu', 'DestroyMenu', 'SetMenu', 'GetMenu', 'LoadIcon', 'CopyIcon', 'DrawIcon', 'DrawIconEx', 'CreateIconIndirect', 'CreateIconFromResource', 'LoadImage', 'DeleteObject', 'BitBlt', 'StretchBlt', 'PatBlt', 'SetStretchBltMode', 'GetStretchBltMode', 'TransparentBlt', 'MaskBlt', 'AlphaBlend', 'ImageList_Add', 'ImageList_Create', 'ImageList_Destroy', 'ImageList_Draw', 'ImageList_DrawEx', 'ImageList_GetIcon', 'ImageList_GetImageCount', 'ImageList_LoadImage', 'ImageList_LoadBitmap', 'ImageList_Remove', 'ImageList_Replace', 'ImageList_ReplaceIcon', 'ImageList_SetBkColor', 'ImageList_SetOverlayImage', 'MessageBox', 'MessageBeep', 'CreateWindow', 'DestroyWindow', 'EnableWindow', 'FindWindow', 'FindWindowEx', 'DragAcceptFiles', 'DragDetect', 'SetDoubleClickTime', 'GetDoubleClickTime', 'HideCaret', 'SetCaretPos', 'GetCaretPos', 'ShowCaret', 'ShowWindow', 'IsWindowVisible', 'IsWindowEnabled', 'SetFocus', 'GetFocus', 'UpdateWindow', 'BringWindowToTop', 'SetActiveWindow', 'GetActiveWindow', 'SetForegroundWindow', 'GetForegroundWindow', 'GetClientRect', 'GetDC', 'SaveDC', 'RestoreDC', 'DeleteDC', 'CreateCompatibleDC', 'CreateCompatibleBitmap', 'CreateBitmap', 'SelectObject', 'GetCurrentObject', 'GetWindowRect', 'GetStockObject', 'PostQuitMessage', 'WaitMessage', 'SetWindowPos', 'GetWindowPlacement', 'SetWindowPlacement', 'RegisterClass', 'UnregisterClass', 'PumpMessages', 'PumpWaitingMessages', 'GetMessage', 'TranslateMessage', 'DispatchMessage', 'TranslateAccelerator', 'PeekMessage', 'Shell_NotifyIcon', 'GetSystemMenu', 'DrawMenuBar', 'MoveWindow', 'CloseWindow', 'DeleteMenu', 'RemoveMenu', 'CreateMenu', 'CreatePopupMenu', 'TrackPopupMenu', 'CommDlgExtendedError', 'ExtractIcon', 'ExtractIconEx', 'DestroyIcon', 'GetIconInfo', 'ScreenToClient', 'ClientToScreen', 'PaintDesktop', 'RedrawWindow', 'GetTextExtentPoint32', 'GetTextMetrics', 'GetTextCharacterExtra', 'SetTextCharacterExtra', 'GetTextAlign', 'SetTextAlign', 'GetTextFace', 'GetMapMode', 'SetMapMode', 'GetGraphicsMode', 'SetGraphicsMode', 'GetLayout', 'SetLayout', 'GetPolyFillMode', 'SetPolyFillMode', 'GetWorldTransform', 'SetWorldTransform', 'ModifyWorldTransform', 'CombineTransform', 'GetWindowOrgEx', 'SetWindowOrgEx', 'GetViewportOrgEx', 'SetViewportOrgEx', 'GetWindowExtEx', 'SetWindowExtEx', 'GetViewportExtEx', 'SetViewportExtEx', 'GradientFill', 'GetOpenFileName', 'InsertMenuItem', 'SetMenuItemInfo', 'GetMenuItemInfo', 'GetMenuItemCount', 'GetMenuItemRect', 'GetMenuState', 'SetMenuDefaultItem', 'GetMenuDefaultItem', 'AppendMenu', 'InsertMenu', 'EnableMenuItem', 'CheckMenuItem', 'GetSubMenu', 'ModifyMenu', 'GetMenuItemID', 'SetMenuItemBitmaps', 'CheckMenuRadioItem', 'SetMenuInfo', 'GetMenuInfo', 'DrawFocusRect', 'DrawText', 'LineTo', 'Ellipse', 'Pie', 'Arc', 'ArcTo', 'AngleArc', 'Chord', 'ExtFloodFill', 'SetPixel', 'GetPixel', 'GetROP2', 'SetROP2', 'SetPixelV', 'MoveToEx', 'GetCurrentPositionEx', 'GetArcDirection', 'SetArcDirection', 'Polygon', 'Polyline', 'PolylineTo', 'PolyBezier', 'PolyBezierTo', 'PlgBlt', 'CreatePolygonRgn', 'ExtTextOut', 'GetTextColor', 'SetTextColor', 'GetBkMode', 'SetBkMode', 'GetBkColor', 'SetBkColor', 'DrawEdge', 'FillRect', 'FillRgn', 'PaintRgn', 'FrameRgn', 'InvertRgn', 'EqualRgn', 'PtInRegion', 'PtInRect', 'RectInRegion', 'SetRectRgn', 'CombineRgn', 'DrawAnimatedRects', 'CreateSolidBrush', 'CreatePatternBrush', 'CreateHatchBrush', 'CreatePen', 'GetSysColor', 'GetSysColorBrush', 'InvalidateRect', 'FrameRect', 'InvertRect', 'WindowFromDC', 'GetUpdateRgn', 'GetWindowRgn', 'SetWindowRgn', 'GetWindowRgnBox', 'ValidateRgn', 'InvalidateRgn', 'GetRgnBox', 'OffsetRgn', 'Rectangle', 'RoundRect', 'BeginPaint', 'EndPaint', 'BeginPath', 'EndPath', 'AbortPath', 'CloseFigure', 'FlattenPath', 'FillPath', 'WidenPath', 'StrokePath', 'StrokeAndFillPath', 'GetMiterLimit', 'SetMiterLimit', 'PathToRegion', 'GetPath', 'CreateRoundRectRgn', 'CreateRectRgnIndirect', 'CreateEllipticRgnIndirect', 'CreateWindowEx', 'GetParent', 'SetParent', 'GetCursorPos', 'GetDesktopWindow', 'GetWindow', 'GetWindowDC', 'IsIconic', 'IsWindow', 'IsChild', 'ReleaseCapture', 'GetCapture', 'SetCapture', '_TrackMouseEvent', 'ReleaseDC', 'CreateCaret', 'DestroyCaret', 'ScrollWindowEx', 'SetScrollInfo', 'GetScrollInfo', 'GetClassName', 'WindowFromPoint', 'ChildWindowFromPoint', 'ChildWindowFromPoint', 'ListView_SortItems', 'ListView_SortItemsEx', 'CreateDC', 'GetSaveFileNameW', 'GetOpenFileNameW', 'SystemParametersInfo', 'SetLayeredWindowAttributes', 'GetLayeredWindowAttributes', 'UpdateLayeredWindow', 'AnimateWindow', 'CreateBrushIndirect', 'ExtCreatePen', 'DrawTextW', 'EnumPropsEx', 'RegisterDeviceNotification', 'UnregisterDeviceNotification', 'RegisterHotKey', 'CLR_NONE', 'ILC_COLOR', 'ILC_COLOR16', 'ILC_COLOR24', 'ILC_COLOR32', 'ILC_COLOR4', 'ILC_COLOR8', 'ILC_COLORDDB', 'ILC_MASK', 'ILD_BLEND', 'ILD_BLEND25', 'ILD_BLEND50', 'ILD_FOCUS', 'ILD_MASK', 'ILD_NORMAL', 'ILD_SELECTED', 'ILD_TRANSPARENT', 'IMAGE_BITMAP', 'IMAGE_CURSOR', 'IMAGE_ICON', 'LR_CREATEDIBSECTION', 'LR_DEFAULTCOLOR', 'LR_DEFAULTSIZE', 'LR_LOADFROMFILE', 'LR_LOADMAP3DCOLORS', 'LR_LOADTRANSPARENT', 'LR_MONOCHROME', 'LR_SHARED', 'LR_VGACOLOR', 'NIF_ICON', 'NIF_INFO', 'NIF_MESSAGE', 'NIF_STATE', 'NIF_TIP', 'NIIF_ERROR', 'NIIF_ICON_MASK', 'NIIF_INFO', 'NIIF_NONE', 'NIIF_NOSOUND', 'NIIF_WARNING', 'NIM_ADD', 'NIM_DELETE', 'NIM_MODIFY', 'NIM_SETFOCUS', 'NIM_SETVERSION', 'TPM_BOTTOMALIGN', 'TPM_CENTERALIGN', 'TPM_LEFTALIGN', 'TPM_LEFTBUTTON', 'TPM_NONOTIFY', 'TPM_RETURNCMD', 'TPM_RIGHTALIGN', 'TPM_RIGHTBUTTON', 'TPM_TOPALIGN', 'TPM_VCENTERALIGN']
import typing
import win32typing
""""""


def EnumFontFamilies(hdc:'int',Family:'typing.Union[str]',EnumFontFamProc:'typing.Any',Param:'typing.Any') -> 'typing.Any':
    """
    Enumerates the available font families.

Args:

      hdc(int):Handle to a device context for which to enumerate available fonts
      Family(typing.Union[str]):Family of fonts to enumerate. If none, first member of each font family will be returned.
      EnumFontFamProc(typing.Any):The Python function called with each font family. This function is called with 4 arguments.
      Param(typing.Any):An arbitrary object to be passed to the callback functionCommentsThe parameters that the callback function will receive are as follows:PyLOGFONT - contains the font parameters None - Placeholder for a TEXTMETRIC structure, not supported yet int - Font type, combination of DEVICE_FONTTYPE, RASTER_FONTTYPE, TRUETYPE_FONTTYPE object - The Param originally passed in to EnumFontFamilies

Returns:

      typing.Any

    """
    pass


def set_logger(logger:'typing.Any') -> 'None':
    """
    Sets a logger object for exceptions and error information

Args:

      logger(typing.Any):A logger object, generally from the standard logger package.CommentsOnce a logger has been set for the module, unhandled exceptions, such as from a window's WNDPROC, will be written (via logger.exception()) to the log instead of to stderr. Note that using this with the Python 2.3 logging package will prevent the traceback from being written to the log.  However, it is possible to use the Python 2.4 logging package directly with Python 2.3

Returns:

      None

    """
    pass


def LOGFONT() -> 'win32typing.PyLOGFONT':
    """
    Creates a LOGFONT object.

Args:



Returns:

      win32typing.PyLOGFONT

    """
    pass


def CreateFontIndirect(lplf:'win32typing.PyLOGFONT') -> 'typing.Any':
    """
    function creates a logical font that has the specified characteristics.

The font can subsequently be selected as the current font for any device context.

Args:

      lplf(win32typing.PyLOGFONT):A LOGFONT object as returned by win32gui::LOGFONT

Returns:

      typing.Any

    """
    pass


def GetObject(handle:'int') -> 'typing.Any':
    """
    Returns a struct containing the parameters used to create a GDI object

Args:

      handle(int):Handle to the object.CommentsThe result depends on the type of the handle.Object type as determined by win32gui::GetObjectTypeReturned objectOBJ_FONTPyLOGFONTOBJ_BITMAPPyBITMAPOBJ_PENDict representing a LOGPEN struct

Returns:

      typing.Any

    """
    pass


def GetObjectType(h:'int') -> 'typing.Any':
    """
    Returns the type (OBJ_* constant) of a GDI handle

Args:

      h(int):A handle to a GDI object

Returns:

      typing.Any

    """
    pass


def PyGetMemory(addr:'typing.Any',_len:'typing.Any') -> 'typing.Any':
    """
    Returns a buffer object from and address and length

Args:

      addr(typing.Any):Address of the memory to reference.
      _len(typing.Any):Number of bytes to return.CommentsIf zero is passed a ValueError will be raised.

Returns:

      typing.Any

    """
    pass


def PyGetString(addr:'typing.Any',_len:'typing.Any') -> 'str':
    """
    Returns a string from an address.

Args:

      addr(typing.Any):Address of the memory to reference
      _len(typing.Any):Number of characters to read.  If not specified, the string must be NULL terminated.Return ValueIf win32gui.UNICODE is True, this will return a unicode object.

Returns:

      str:Number of characters to read.  If not specified, the

string must be NULL terminated.Return ValueIf win32gui.UNICODE is True, this will return a unicode object.


    """
    pass


def PySetString(addr:'typing.Any',String:'typing.Any',maxLen:'typing.Any') -> 'typing.Any':
    """
    None

Args:

      addr(typing.Any):Address of the memory to reference
      String(typing.Any):The string to copy
      maxLen(typing.Any):Maximum number of chars to copy (optional)

Returns:

      typing.Any

    """
    pass


def PySetMemory(addr:'typing.Any',String:'typing.Any') -> 'typing.Any':
    """
    Copies bytes to an address.

Args:

      addr(typing.Any):Address of the memory to reference
      String(typing.Any):The string to copy

Returns:

      typing.Any

    """
    pass


def PyGetArraySignedLong(array:'typing.Any',index:'typing.Any') -> 'typing.Any':
    """
    Returns a signed long from an array object at specified index

Args:

      array(typing.Any):array object to use
      index(typing.Any):index of offset

Returns:

      typing.Any

    """
    pass


def PyGetBufferAddressAndLen(obj:'typing.Any') -> 'typing.Any':
    """
    Returns a buffer object address and len

Args:

      obj(typing.Any):the buffer object

Returns:

      typing.Any

    """
    pass


def FlashWindow(hwnd:'int',bInvert:'typing.Any') -> 'typing.Any':
    """
    The FlashWindow function flashes the specified window one time. It does not change the active state of the window.

Args:

      hwnd(int):Handle to a window
      bInvert(typing.Any):Indicates if window should toggle between active and inactive

Returns:

      typing.Any

    """
    pass


def FlashWindowEx(hwnd:'int',dwFlags:'typing.Any',uCount:'typing.Any',dwTimeout:'typing.Any') -> 'typing.Any':
    """
    The FlashWindowEx function flashes the specified window a specified number of times.

Args:

      hwnd(int):Handle to a window
      dwFlags(typing.Any):Combination of win32con.FLASHW_* flags
      uCount(typing.Any):Nbr of times to flash
      dwTimeout(typing.Any):Elapsed time between flashes, in milliseconds

Returns:

      typing.Any

    """
    pass


def GetWindowLong(hwnd:'int',index:'typing.Any') -> 'typing.Any':
    """
    None

Args:

      hwnd(typing.Any):
      index(typing.Any):

Returns:

      typing.Any

    """
    pass


def GetClassLong(hwnd:'int',index:'typing.Any') -> 'typing.Any':
    """
    None

Args:

      hwnd(typing.Any):
      index(typing.Any):

Returns:

      typing.Any

    """
    pass


def SetWindowLong(hwnd:'int',index:'typing.Any',value:'typing.Any') -> 'typing.Any':
    """
    Places a long value at the specified offset into the extra window memory of the given window.

Args:

      hwnd(int):The handle to the window
      index(typing.Any):The index of the item to set.
      value(typing.Any):The value to set.CommentsThis function calls the SetWindowLongPtr Api functionIf index is GWLP_WNDPROC, then the value parameter must be a callable object (or a dictionary) to use as the new window procedure.

Returns:

      typing.Any

    """
    pass


def CallWindowProc(wndproc:'typing.Any',hwnd:'int',msg:'typing.Any',wparam:'typing.Union[typing.Any]',lparam:'typing.Union[typing.Any]') -> 'typing.Any':
    """
    None

Args:

      wndproc(typing.Any):The wndproc to call - this is generally the return value of SetWindowLong(GWL_WNDPROC)
      hwnd(int):Handle to the window
      msg(typing.Any):A window message
      wparam(typing.Union[typing.Any]):Type is dependent on the message
      lparam(typing.Union[typing.Any]):Type is dependent on the message

Returns:

      typing.Any

    """
    pass


def SendMessage(hwnd:'int',message:'typing.Any',wparam:'typing.Union[typing.Any]'=None,lparam:'typing.Union[typing.Any]'=None) -> 'typing.Any':
    """
    Sends a message to the window.

Args:

      hwnd(typing.Any):The handle to the Window
      message(typing.Any):The ID of the message to post
      wparam(typing.Union[typing.Any]):Type depends on the message
      lparam(typing.Union[typing.Any]):Type depends on the message

Returns:

      typing.Any

    """
    pass


def SendMessageTimeout(hwnd:'int',message:'typing.Any',wparam:'typing.Any',lparam:'typing.Any',flags:'typing.Any',timeout:'typing.Any') -> 'tuple[typing.Any, typing.Any]':
    """
    Sends a message to the window.

Args:

      hwnd(typing.Any):The handle to the Window
      message(typing.Any):The ID of the message to post
      wparam(typing.Any):An integer whose value depends on the message
      lparam(typing.Any):An integer whose value depends on the message
      flags(typing.Any):Send options
      timeout(typing.Any):Timeout duration in milliseconds.Return ValueThe result is the result of the SendMessageTimeout call, plus the last 'result' param. If the timeout period expires, a pywintypes.error exception will be thrown, with zero as the error code.  See the Microsoft documentation for more information.

Returns:

      tuple[typing.Any, typing.Any]:Timeout duration in milliseconds.Return ValueThe result is the result of the SendMessageTimeout call, plus the last 'result' param.

If the timeout period expires, a pywintypes.error exception will be thrown,

with zero as the error code.  See the Microsoft documentation for more information.


    """
    pass


def PostMessage(hwnd:'int',message:'typing.Any',wparam:'typing.Any'=0,lparam:'typing.Any'=0) -> 'None':
    """
    None

Args:

      hwnd(typing.Any):The handle to the Window
      message(typing.Any):The ID of the message to post
      wparam(typing.Any):An integer whose value depends on the message
      lparam(typing.Any):An integer whose value depends on the message

Returns:

      None

    """
    pass


def PostThreadMessage(threadId:'typing.Any',message:'typing.Any',wparam:'typing.Any',lparam:'typing.Any') -> 'None':
    """
    None

Args:

      threadId(typing.Any):The ID of the thread to post the message to.
      message(typing.Any):The ID of the message to post
      wparam(typing.Any):An integer whose value depends on the message
      lparam(typing.Any):An integer whose value depends on the message

Returns:

      None

    """
    pass


def ReplyMessage(result:'typing.Any') -> 'typing.Any':
    """
    Used to reply to a message sent through the SendMessage function without returning control to the function that called SendMessage.

Args:

      result(typing.Any):Specifies the result of the message processing. The possible values are based on the message sent.

Returns:

      typing.Any

    """
    pass


def RegisterWindowMessage(name:'typing.Union[str, typing.Any]') -> 'typing.Any':
    """
    Defines a new window message that is guaranteed to be unique throughout the system. The message value can be used when sending or posting messages.

Args:

      name(typing.Union[str, typing.Any]):The string

Returns:

      typing.Any

    """
    pass


def DefWindowProc(hwnd:'int',message:'typing.Any',wparam:'typing.Any',lparam:'typing.Any') -> 'typing.Any':
    """
    None

Args:

      hwnd(typing.Any):The handle to the Window
      message(typing.Any):The ID of the message to send
      wparam(typing.Any):An integer whose value depends on the message
      lparam(typing.Any):An integer whose value depends on the message

Returns:

      typing.Any

    """
    pass


def EnumWindows(callback:'typing.Any',extra:'typing.Any') -> 'None':
    """
    Enumerates all top-level windows on the screen by passing the handle to each window, in turn, to an application-defined callback function.

Args:

      callback(typing.Any):A Python function to be used as the callback.  Function can return False to stop enumeration, or raise an exception.
      extra(typing.Any):Any python object - this is passed to the callback function as the second param (first is the hwnd).

Returns:

      None

    """
    pass


def EnumThreadWindows(dwThreadId:'typing.Any',callback:'typing.Any',extra:'typing.Any') -> 'None':
    """
    Enumerates all top-level windows associated with a thread on the screen by passing the handle to each window, in turn, to an application-defined callback function. EnumThreadWindows continues until the last top-level window associated with the thread is enumerated or the callback function returns FALSE

Args:

      dwThreadId(typing.Any):The id of the thread for which the windows need to be enumerated.
      callback(typing.Any):A Python function to be used as the callback.
      extra(typing.Any):Any python object - this is passed to the callback function as the second param (first is the hwnd).

Returns:

      None

    """
    pass


def EnumChildWindows(hwnd:'int',callback:'typing.Any',extra:'typing.Any') -> 'None':
    """
    Enumerates the child windows that belong to the specified parent window by passing the handle to each child window, in turn, to an application-defined callback function. EnumChildWindows continues until the last child window is enumerated or the callback function returns FALSE.

Args:

      hwnd(int):The handle to the window to enumerate.
      callback(typing.Any):A Python function to be used as the callback.
      extra(typing.Any):Any python object - this is passed to the callback function as the second param (first is the hwnd).

Returns:

      None

    """
    pass


def DialogBox(hInstance:'int',TemplateName:'win32typing.PyResourceId',hWndParent:'int',DialogFunc:'typing.Any',InitParam:'typing.Any'=0) -> 'typing.Any':
    """
    Creates a modal dialog box.

Args:

      hInstance(int):Handle to module that contains the dialog template
      TemplateName(win32typing.PyResourceId):Name or resource id of the dialog resource
      hWndParent(int):Handle to dialog's parent window
      DialogFunc(typing.Any):Dialog box procedure to process messages
      InitParam(typing.Any):Initialization data to be passed to above procedure during WM_INITDIALOG processing

Returns:

      typing.Any

    """
    pass


def DialogBoxParam() -> 'typing.Any':
    """
    None

Args:



Returns:

      typing.Any

    """
    pass


def DialogBoxIndirect(hInstance:'int',controlList:'win32typing.PyDialogTemplate',hWndParent:'int',DialogFunc:'typing.Any',InitParam:'typing.Any'=0) -> 'typing.Any':
    """
    None

Args:

      hInstance(int):Handle to module creating the dialog box
      controlList(win32typing.PyDialogTemplate):Sequence of items defining the dialog box and subcontrols
      hWndParent(int):Handle to dialog's parent window
      DialogFunc(typing.Any):Dialog box procedure to process messages
      InitParam(typing.Any):Initialization data to be passed to above procedure during WM_INITDIALOG processing

Returns:

      typing.Any

    """
    pass


def DialogBoxIndirectParam() -> 'typing.Any':
    """
    None

Args:



Returns:

      typing.Any

    """
    pass


def CreateDialogIndirect(hInstance:'int',controlList:'win32typing.PyDialogTemplate',hWndParent:'int',DialogFunc:'typing.Any',InitParam:'typing.Any'=0) -> 'typing.Any':
    """
    None

Args:

      hInstance(int):Handle to module creating the dialog box
      controlList(win32typing.PyDialogTemplate):Sequence containing a PyDLGTEMPLATE, followed by variable number of PyDLGITEMTEMPLATEs
      hWndParent(int):Handle to dialog's parent window
      DialogFunc(typing.Any):Dialog box procedure to process messages
      InitParam(typing.Any):Initialization data to be passed to above procedure during WM_INITDIALOG processing

Returns:

      typing.Any

    """
    pass


def DialogBoxIndirectParam() -> 'typing.Any':
    """
    None

Args:



Returns:

      typing.Any

    """
    pass


def EndDialog(hwnd:'int',result:'typing.Any') -> 'None':
    """
    Ends a dialog box.

Args:

      hwnd(typing.Any):Handle to the window.
      result(typing.Any):result

Returns:

      None

    """
    pass


def GetDlgItem(hDlg:'int',IDDlgItem:'typing.Any') -> 'typing.Any':
    """
    Retrieves the handle to a control in the specified dialog box.

Args:

      hDlg(int):Handle to a dialog window
      IDDlgItem(typing.Any):Identifier of one of the dialog's controls

Returns:

      typing.Any

    """
    pass


def GetDlgItemInt(hDlg:'int',IDDlgItem:'typing.Any',Signed:'typing.Any') -> 'None':
    """
    Returns the integer value of a dialog control

Args:

      hDlg(int):Handle to a dialog window
      IDDlgItem(typing.Any):Identifier of one of the dialog's controls
      Signed(typing.Any):Indicates whether control value should be interpreted as signed

Returns:

      None

    """
    pass


def SetDlgItemInt(hDlg:'int',IDDlgItem:'typing.Any',Value:'typing.Any',Signed:'typing.Any') -> 'None':
    """
    Places an integer value in a dialog control

Args:

      hDlg(int):Handle to a dialog window
      IDDlgItem(typing.Any):Identifier of one of the dialog's controls
      Value(typing.Any):Value to placed in the control
      Signed(typing.Any):Indicates if the input value is signed

Returns:

      None

    """
    pass


def GetDlgCtrlID(hwnd:'int') -> 'typing.Any':
    """
    Retrieves the identifier of the specified control.

Args:

      hwnd(typing.Any):The handle to the control

Returns:

      typing.Any

    """
    pass


def GetDlgItemText(hDlg:'int',IDDlgItem:'typing.Any') -> 'str':
    """
    Returns the text of a dialog control

Args:

      hDlg(int):Handle to a dialog window
      IDDlgItem(typing.Any):The Id of a control within the dialog

Returns:

      str

    """
    pass


def SetDlgItemText(hDlg:'int',IDDlgItem:'typing.Any',String:'typing.Union[typing.Any]') -> 'None':
    """
    Sets the text for a window or control

Args:

      hDlg(int):Handle to a dialog window
      IDDlgItem(typing.Any):The Id of a control within the dialog
      String(typing.Union[typing.Any]):The text to put in the control

Returns:

      None

    """
    pass


def GetNextDlgTabItem(hDlg:'typing.Any',hCtl:'typing.Any',bPrevious:'typing.Any') -> 'typing.Any':
    """
    Retrieves a handle to the first control that has the WS_TABSTOP style that precedes (or follows) the specified control.

Args:

      hDlg(typing.Any):handle to dialog box
      hCtl(typing.Any):handle to known control
      bPrevious(typing.Any):direction flag

Returns:

      typing.Any

    """
    pass


def GetNextDlgGroupItem(hDlg:'typing.Any',hCtl:'typing.Any',bPrevious:'typing.Any') -> 'typing.Any':
    """
    Retrieves a handle to the first control in a group of controls that precedes (or follows) the specified control in a dialog box.

Args:

      hDlg(typing.Any):handle to dialog box
      hCtl(typing.Any):handle to known control
      bPrevious(typing.Any):direction flag

Returns:

      typing.Any

    """
    pass


def SetWindowText() -> 'None':
    """
    Sets the window text.

Args:



Returns:

      None

    """
    pass


def GetWindowText(hwnd:'int') -> 'str':
    """
    Get the window text.

Args:

      hwnd(int):The handle to the windowCommentsNote that previous versions of PyWin32 returned a (empty) Unicode object when the string was empty, or an MBCS encoded string value otherwise.  A String is now returned in all cases.

Returns:

      str

    """
    pass


def InitCommonControls() -> 'None':
    """
    Initializes the common controls.

Args:



Returns:

      None

    """
    pass


def InitCommonControlsEx(flag:'typing.Any') -> 'None':
    """
    Initializes specific common controls.

Args:

      flag(typing.Any):One of the ICC_ constants

Returns:

      None

    """
    pass


def LoadCursor(hinstance:'typing.Any',resid:'typing.Any') -> 'typing.Any':
    """
    Loads a cursor.

Args:

      hinstance(typing.Any):The module to load from
      resid(typing.Any):The resource ID

Returns:

      typing.Any

    """
    pass


def SetCursor(hcursor:'typing.Any') -> 'typing.Any':
    """
    None

Args:

      hcursor(typing.Any):

Returns:

      typing.Any

    """
    pass


def GetCursor() -> 'typing.Any':
    """
    None

Args:



Returns:

      typing.Any

    """
    pass


def GetCursorInfo() -> 'tuple[int, int, int, int]':
    """
    Retrieves information about the global cursor.

Args:



Returns:

      tuple[int, int, int, int]

    """
    pass


def CreateAcceleratorTable(accels:'tuple[tuple[typing.Any, typing.Any, typing.Any], ...]') -> 'typing.Any':
    """
    Creates an accelerator table

Args:

      accels(tuple[tuple[typing.Any, typing.Any, typing.Any], ...]):A sequence of (fVirt, key, cmd), as per the Win32 ACCEL structure.

Returns:

      typing.Any

    """
    pass


def DestroyAccleratorTable(haccel:'typing.Any') -> 'None':
    """
    Destroys an accelerator table

Args:

      haccel(typing.Any):

Returns:

      None

    """
    pass


def LoadMenu(hinstance:'typing.Any',resource_id:'typing.Union[str, typing.Any]') -> 'typing.Any':
    """
    Loads a menu

Args:

      hinstance(typing.Any):
      resource_id(typing.Union[str, typing.Any]):

Returns:

      typing.Any

    """
    pass


def DestroyMenu() -> 'None':
    """
    Destroys a previously loaded menu.

Args:



Returns:

      None

    """
    pass


def SetMenu(hwnd:'int',hmenu:'typing.Any') -> 'None':
    """
    Sets the menu for the specified window.

Args:

      hwnd(typing.Any):
      hmenu(typing.Any):

Returns:

      None

    """
    pass


def GetMenu() -> 'None':
    """
    Gets the menu for the specified window.

Args:



Returns:

      None

    """
    pass


def LoadIcon(hinstance:'typing.Any',resource_id:'typing.Union[str, typing.Any]') -> 'typing.Any':
    """
    Loads an icon

Args:

      hinstance(typing.Any):
      resource_id(typing.Union[str, typing.Any]):

Returns:

      typing.Any

    """
    pass


def CopyIcon(hicon:'typing.Any') -> 'typing.Any':
    """
    Copies an icon

Args:

      hicon(typing.Any):Existing icon

Returns:

      typing.Any

    """
    pass


def DrawIcon(hDC:'typing.Any',X:'typing.Any',Y:'typing.Any',hicon:'typing.Any') -> 'None':
    """
    None

Args:

      hDC(typing.Any):handle to DC
      X(typing.Any):x-coordinate of upper-left corner
      Y(typing.Any):y-coordinate of upper-left corner
      hicon(typing.Any):handle to icon

Returns:

      None

    """
    pass


def DrawIconEx(hDC:'typing.Any',xLeft:'typing.Any',yTop:'typing.Any',hIcon:'typing.Any',cxWidth:'typing.Any',cyWidth:'typing.Any',istepIfAniCur:'typing.Any',hbrFlickerFreeDraw:'win32typing.PyGdiHANDLE',diFlags:'typing.Any') -> 'None':
    """
    Draws an icon or cursor into the specified device context,

performing the specified raster operations, and stretching or compressing the

icon or cursor as specified.

Args:

      hDC(typing.Any):handle to device context
      xLeft(typing.Any):x-coord of upper left corner
      yTop(typing.Any):y-coord of upper left corner
      hIcon(typing.Any):handle to icon
      cxWidth(typing.Any):icon width
      cyWidth(typing.Any):icon height
      istepIfAniCur(typing.Any):frame index, animated cursor
      hbrFlickerFreeDraw(win32typing.PyGdiHANDLE):handle to background brush, can be None
      diFlags(typing.Any):icon-drawing flags (win32con.DI_*)

Returns:

      None

    """
    pass


def CreateIconIndirect(iconinfo:'win32typing.PyICONINFO') -> 'typing.Any':
    """
    Creates an icon or cursor from an ICONINFO structure.

Args:

      iconinfo(win32typing.PyICONINFO):Tuple defining the icon parameters

Returns:

      typing.Any

    """
    pass


def CreateIconFromResource(bits:'str',fIcon:'typing.Any',ver:'typing.Any'=0x00030000) -> 'int':
    """
    Creates an icon or cursor from resource bits describing the icon.

Args:

      bits(str):The bits
      fIcon(typing.Any):True if an icon, False if a cursor.
      ver(typing.Any):Specifies the version number of the icon or cursor format for the resource bits pointed to by the presbits parameter. This parameter can be 0x00030000.

Returns:

      int

    """
    pass


def LoadImage(hinst:'typing.Any',name:'typing.Union[str, typing.Any]',_type:'typing.Any',cxDesired:'typing.Any',cyDesired:'typing.Any',fuLoad:'typing.Any') -> 'typing.Any':
    """
    Loads a bitmap, cursor or icon

Args:

      hinst(typing.Any):Handle to an instance of the module that contains the image to be loaded. To load an OEM image, set this parameter to zero.
      name(typing.Union[str, typing.Any]):Specifies the image to load. If the hInst parameter is non-zero and the fuLoad parameter omits LR_LOADFROMFILE, name specifies the image resource in the hInst module. If the image resource is to be loaded by name, the name parameter is a string that contains the name of the image resource.
      _type(typing.Any):Specifies the type of image to be loaded.
      cxDesired(typing.Any):Specifies the width, in pixels, of the icon or cursor. If this parameter is zero and the fuLoad parameter is LR_DEFAULTSIZE, the function uses the SM_CXICON or SM_CXCURSOR system metric value to set the width. If this parameter is zero and LR_DEFAULTSIZE is not used, the function uses the actual resource width.
      cyDesired(typing.Any):Specifies the height, in pixels, of the icon or cursor. If this parameter is zero and the fuLoad parameter is LR_DEFAULTSIZE, the function uses the SM_CYICON or SM_CYCURSOR system metric value to set the height. If this parameter is zero and LR_DEFAULTSIZE is not used, the function uses the actual resource height.
      fuLoad(typing.Any):

Returns:

      typing.Any

    """
    pass


def DeleteObject(handle:'win32typing.PyGdiHANDLE') -> 'None':
    """
    Deletes a logical pen, brush, font, bitmap, region, or palette, freeing all system resources associated with the object. After the object is deleted, the specified handle is no longer valid.

Args:

      handle(win32typing.PyGdiHANDLE):handle to the object to delete.

Returns:

      None

    """
    pass


def BitBlt(hdcDest:'typing.Any',x:'typing.Any',y:'typing.Any',width:'typing.Any',height:'typing.Any',hdcSrc:'typing.Any',nXSrc:'typing.Any',nYSrc:'typing.Any',dwRop:'typing.Any') -> 'None':
    """
    Performs a bit-block transfer of the color data corresponding

to a rectangle of pixels from the specified source device context into a

destination device context.

Args:

      hdcDest(typing.Any):handle to destination DC
      x(typing.Any):x-coord of destination upper-left corner
      y(typing.Any):y-coord of destination upper-left corner
      width(typing.Any):width of destination rectangle
      height(typing.Any):height of destination rectangle
      hdcSrc(typing.Any):handle to source DC
      nXSrc(typing.Any):x-coordinate of source upper-left corner
      nYSrc(typing.Any):y-coordinate of source upper-left corner
      dwRop(typing.Any):raster operation code

Returns:

      None

    """
    pass


def StretchBlt(hdcDest:'typing.Any',x:'typing.Any',y:'typing.Any',width:'typing.Any',height:'typing.Any',hdcSrc:'typing.Any',nXSrc:'typing.Any',nYSrc:'typing.Any',nWidthSrc:'typing.Any',nHeightSrc:'typing.Any',dwRop:'typing.Any') -> 'None':
    """
    Copies a bitmap from a source rectangle into a destination

rectangle, stretching or compressing the bitmap to fit the dimensions of the

destination rectangle, if necessary

Args:

      hdcDest(typing.Any):handle to destination DC
      x(typing.Any):x-coord of destination upper-left corner
      y(typing.Any):y-coord of destination upper-left corner
      width(typing.Any):width of destination rectangle
      height(typing.Any):height of destination rectangle
      hdcSrc(typing.Any):handle to source DC
      nXSrc(typing.Any):x-coord of source upper-left corner
      nYSrc(typing.Any):y-coord of source upper-left corner
      nWidthSrc(typing.Any):width of source rectangle
      nHeightSrc(typing.Any):height of source rectangle
      dwRop(typing.Any):raster operation code

Returns:

      None

    """
    pass


def PatBlt(hdc:'int',XLeft:'typing.Any',YLeft:'typing.Any',Width:'typing.Any',Height:'typing.Any',Rop:'typing.Any') -> 'None':
    """
    Paints a rectangle by combining the current brush with existing colors

Args:

      hdc(int):Handle to a device context
      XLeft(typing.Any):Horizontal pos
      YLeft(typing.Any):Vertical pos
      Width(typing.Any):Width of rectangular area
      Height(typing.Any):Height of rectangular area
      Rop(typing.Any):Raster operation, one of PATCOPY,PATINVERT,DSTINVERT,BLACKNESS,WHITENESS

Returns:

      None

    """
    pass


def SetStretchBltMode(hdc:'int',StretchMode:'typing.Any') -> 'typing.Any':
    """
    None

Args:

      hdc(int):Handle to a device context
      StretchMode(typing.Any):One of BLACKONWHITE,COLORONCOLOR,HALFTONE,STRETCH_ANDSCANS,STRETCH_DELETESCANS,STRETCH_HALFTONE,STRETCH_ORSCANS, or WHITEONBLACK (from win32con)Return ValueIf the function succeeds, the return value is the previous stretching mode. If the function fails, the return value is zero.

Returns:

      typing.Any:One of BLACKONWHITE,COLORONCOLOR,HALFTONE,STRETCH_ANDSCANS,STRETCH_DELETESCANS,STRETCH_HALFTONE,STRETCH_ORSCANS, or WHITEONBLACK (from win32con)Return ValueIf the function succeeds, the return value is the previous stretching mode.

If the function fails, the return value is zero.


    """
    pass


def GetStretchBltMode(hdc:'int') -> 'typing.Any':
    """
    None

Args:

      hdc(int):Handle to a device contextReturn ValueReturns one of BLACKONWHITE,COLORONCOLOR,HALFTONE,STRETCH_ANDSCANS,STRETCH_DELETESCANS,STRETCH_HALFTONE,STRETCH_ORSCANS,WHITEONBLACK, or 0 on error.

Returns:

      typing.Any:Handle to a device contextReturn ValueReturns one of BLACKONWHITE,COLORONCOLOR,HALFTONE,STRETCH_ANDSCANS,STRETCH_DELETESCANS,STRETCH_HALFTONE,STRETCH_ORSCANS,WHITEONBLACK, or 0 on error.


    """
    pass


def TransparentBlt(Dest:'int',XOriginDest:'typing.Any',YOriginDest:'typing.Any',WidthDest:'typing.Any',HeightDest:'typing.Any',Src:'int',XOriginSrc:'typing.Any',YOriginSrc:'typing.Any',WidthSrc:'typing.Any',HeightSrc:'typing.Any',Transparent:'typing.Any') -> 'None':
    """
    Transfers color from one DC to another, with one color treated as transparent

Args:

      Dest(int):Destination device context handle
      XOriginDest(typing.Any):X pos of dest rect
      YOriginDest(typing.Any):Y pos of dest rect
      WidthDest(typing.Any):Width of dest rect
      HeightDest(typing.Any):Height of dest rect
      Src(int):Source DC handle
      XOriginSrc(typing.Any):X pos of src rect
      YOriginSrc(typing.Any):Y pos of src rect
      WidthSrc(typing.Any):Width of src rect
      HeightSrc(typing.Any):Height of src rect
      Transparent(typing.Any):RGB color value that will be transparent

Returns:

      None

    """
    pass


def MaskBlt(Dest:'int',XDest:'typing.Any',YDest:'typing.Any',Width:'typing.Any',Height:'typing.Any',Src:'int',XSrc:'typing.Any',YSrc:'typing.Any',Mask:'win32typing.PyGdiHANDLE',xMask:'typing.Any',yMask:'typing.Any',Rop:'typing.Any') -> 'None':
    """
    Combines the color data for the source and destination

bitmaps using the specified mask and raster operation.

Args:

      Dest(int):Destination device context handle
      XDest(typing.Any):X pos of dest rect
      YDest(typing.Any):Y pos of dest rect
      Width(typing.Any):Width of rect to be copied
      Height(typing.Any):Height of rect to be copied
      Src(int):Source DC handle
      XSrc(typing.Any):X pos of src rect
      YSrc(typing.Any):Y pos of src rect
      Mask(win32typing.PyGdiHANDLE):Handle to monochrome bitmap used to mask color
      xMask(typing.Any):X pos in mask
      yMask(typing.Any):Y pos in mask
      Rop(typing.Any):Foreground and background raster operations.  See MSDN docs for how to construct this value.CommentsThis function is not supported on Win9x.Win32 API References

Returns:

      None

    """
    pass


def AlphaBlend(Dest:'int',XOriginDest:'typing.Any',YOriginDest:'typing.Any',WidthDest:'typing.Any',HeightDest:'typing.Any',Src:'int',XOriginSrc:'typing.Any',YOriginSrc:'typing.Any',WidthSrc:'typing.Any',HeightSrc:'typing.Any',blendFunction:'win32typing.PyBLENDFUNCTION') -> 'None':
    """
    Transfers color information using alpha blending

Args:

      Dest(int):Destination device context handle
      XOriginDest(typing.Any):X pos of dest rect
      YOriginDest(typing.Any):Y pos of dest rect
      WidthDest(typing.Any):Width of dest rect
      HeightDest(typing.Any):Height of dest rect
      Src(int):Source DC handle
      XOriginSrc(typing.Any):X pos of src rect
      YOriginSrc(typing.Any):Y pos of src rect
      WidthSrc(typing.Any):Width of src rect
      HeightSrc(typing.Any):Height of src rect
      blendFunction(win32typing.PyBLENDFUNCTION):Alpha blending parameters

Returns:

      None

    """
    pass


def ImageList_Add(himl:'typing.Any',hbmImage:'win32typing.PyGdiHANDLE',hbmMask:'win32typing.PyGdiHANDLE') -> 'typing.Any':
    """
    Adds an image or images to an image list.

Args:

      himl(typing.Any):Handle to the image list.
      hbmImage(win32typing.PyGdiHANDLE):Handle to the bitmap that contains the image or images. The number of images is inferred from the width of the bitmap.
      hbmMask(win32typing.PyGdiHANDLE):Handle to the bitmap that contains the mask. If no mask is used with the image list, this parameter is ignoredReturn ValueReturns the index of the first new image if successful, or -1 otherwise.

Returns:

      typing.Any:Handle to the bitmap that contains the mask. If no mask is used with the image list, this parameter is ignoredReturn ValueReturns the index of the first new image if successful, or -1 otherwise.


    """
    pass


def ImageList_Create() -> 'typing.Any':
    """
    Create an image list

Args:



Returns:

      typing.Any

    """
    pass


def ImageList_Destroy() -> 'typing.Any':
    """
    Destroy an imagelist

Args:



Returns:

      typing.Any

    """
    pass


def ImageList_Draw() -> 'typing.Any':
    """
    Draw an image on an HDC

Args:



Returns:

      typing.Any

    """
    pass


def ImageList_DrawEx() -> 'typing.Any':
    """
    Draw an image on an HDC

Args:



Returns:

      typing.Any

    """
    pass


def ImageList_GetIcon() -> 'typing.Any':
    """
    Extract an icon from an imagelist

Args:



Returns:

      typing.Any

    """
    pass


def ImageList_GetImageCount() -> 'typing.Any':
    """
    Return count of images in imagelist

Args:



Returns:

      typing.Any

    """
    pass


def ImageList_LoadImage() -> 'typing.Any':
    """
    Loads bitmaps, cursors or icons, creates imagelist

Args:



Returns:

      typing.Any

    """
    pass


def ImageList_LoadBitmap() -> 'typing.Any':
    """
    Creates an image list from the specified bitmap resource.

Args:



Returns:

      typing.Any

    """
    pass


def ImageList_Remove() -> 'typing.Any':
    """
    Remove an image from an imagelist

Args:



Returns:

      typing.Any

    """
    pass


def ImageList_Replace() -> 'typing.Any':
    """
    Replace an image in an imagelist with a bitmap image

Args:



Returns:

      typing.Any

    """
    pass


def ImageList_ReplaceIcon() -> 'typing.Any':
    """
    Replace an image in an imagelist with an icon image

Args:



Returns:

      typing.Any

    """
    pass


def ImageList_SetBkColor() -> 'typing.Any':
    """
    Set the background color for the imagelist

Args:



Returns:

      typing.Any

    """
    pass


def ImageList_SetOverlayImage(hImageList:'typing.Any',iImage:'typing.Any',iOverlay:'typing.Any') -> 'None':
    """
    Adds a specified image to the list of images to be used as overlay masks. An image list can have up to four overlay masks in version 4.70 and earlier and up to 15 in version 4.71. The function assigns an overlay mask index to the specified image.

Args:

      hImageList(typing.Any):
      iImage(typing.Any):
      iOverlay(typing.Any):

Returns:

      None

    """
    pass


def MessageBox(parent:'typing.Any',text:'typing.Union[str]',caption:'typing.Union[str]',flags:'typing.Any') -> 'typing.Any':
    """
    Displays a message box

Args:

      parent(typing.Any):The parent window
      text(typing.Union[str]):The text for the message box
      caption(typing.Union[str]):The caption for the message box
      flags(typing.Any):

Returns:

      typing.Any

    """
    pass


def MessageBeep(_type:'typing.Any') -> 'None':
    """
    Plays a waveform sound.

Args:

      _type(typing.Any):The type of the beep

Returns:

      None

    """
    pass


def CreateWindow(className:'typing.Union[str, typing.Any]',windowTitle:'str',style:'typing.Any',x:'typing.Any',y:'typing.Any',width:'typing.Any',height:'typing.Any',parent:'typing.Any',menu:'typing.Any',hinstance:'typing.Any',reserved:'typing.Any') -> 'typing.Any':
    """
    Creates a new window.

Args:

      className(typing.Union[str, typing.Any]):
      windowTitle(str):
      style(typing.Any):The style for the window.
      x(typing.Any):
      y(typing.Any):
      width(typing.Any):
      height(typing.Any):
      parent(typing.Any):Handle to the parent window.
      menu(typing.Any):Handle to the menu to use for this window.
      hinstance(typing.Any):
      reserved(typing.Any):Must be None

Returns:

      typing.Any

    """
    pass


def DestroyWindow(hwnd:'int') -> 'None':
    """
    None

Args:

      hwnd(typing.Any):The handle to the window

Returns:

      None

    """
    pass


def EnableWindow(hWnd:'int',bEnable:'typing.Any') -> 'typing.Any':
    """
    Enables and disables keyboard and mouse input to a window

Args:

      hWnd(int):Handle to window
      bEnable(typing.Any):True to enable input to the window, False to disable inputReturn ValueReturns True if window was already disabled when call was made, False otherwise

Returns:

      typing.Any:True to enable input to the window, False to disable inputReturn ValueReturns True if window was already disabled when call was made, False otherwise


    """
    pass


def FindWindow(ClassName:'win32typing.PyResourceId',WindowName:'str') -> 'int':
    """
    Retrieves a handle to the top-level window whose class name and window name match the specified strings.

Args:

      ClassName(win32typing.PyResourceId):Name or atom of window class to find, can be None
      WindowName(str):Title of window to find, can be None

Returns:

      int

    """
    pass


def FindWindowEx(Parent:'int',ChildAfter:'int',ClassName:'win32typing.PyResourceId',WindowName:'str') -> 'int':
    """
    Retrieves a handle to the top-level window whose class name and window name match the specified strings.

Args:

      Parent(int):Window whose child windows will be searched.  If 0, desktop window is assumed.
      ChildAfter(int):Child window after which to search in Z-order, can be 0 to search all
      ClassName(win32typing.PyResourceId):Name or atom of window class to find, can be None
      WindowName(str):Title of window to find, can be None

Returns:

      int

    """
    pass


def DragAcceptFiles(hwnd:'int',fAccept:'typing.Any') -> 'None':
    """
    Registers whether a window accepts dropped files.

Args:

      hwnd(typing.Any):Handle to the Window
      fAccept(typing.Any):Value that indicates if the window identified by the hWnd parameter accepts dropped files. This value is True to accept dropped files or False to discontinue accepting dropped files.

Returns:

      None

    """
    pass


def DragDetect(hwnd:'int',point:'tuple[typing.Any, typing.Any]') -> 'None':
    """
    captures the mouse and tracks its movement until the user releases the left button, presses the ESC key, or moves the mouse outside the drag rectangle around the specified point.

Args:

      hwnd(typing.Any):Handle to the Window
      point(tuple[typing.Any, typing.Any]):Initial position of the mouse, in screen coordinates. The function determines the coordinates of the drag rectangle by using this point.Return ValueIf the user moved the mouse outside of the drag rectangle while holding down the left button , the return value is nonzero. If the user did not move the mouse outside of the drag rectangle while holding down the left button , the return value is zero.

Returns:

      None:Initial position of the mouse, in screen coordinates. The function determines the coordinates of the drag rectangle by using this point.Return ValueIf the user moved the mouse outside of the drag rectangle while holding down the left button , the return value is nonzero.

If the user did not move the mouse outside of the drag rectangle while holding down the left button , the return value is zero.


    """
    pass


def SetDoubleClickTime(newVal:'typing.Any') -> 'None':
    """
    None

Args:

      newVal(typing.Any):

Returns:

      None

    """
    pass


def GetDoubleClickTime() -> 'typing.Any':
    """
    None

Args:



Returns:

      typing.Any

    """
    pass


def HideCaret(hWnd:'int') -> 'None':
    """
    Hides the caret

Args:

      hWnd(int):Window that owns the caret, can be 0.

Returns:

      None

    """
    pass


def SetCaretPos(x:'typing.Any',y:'typing.Any') -> 'None':
    """
    Changes the position of the caret

Args:

      x(typing.Any):horizontal position
      y(typing.Any):vertical position

Returns:

      None

    """
    pass


def GetCaretPos() -> 'tuple[typing.Any, typing.Any]':
    """
    Returns the current caret position

Args:



Returns:

      tuple[typing.Any, typing.Any]

    """
    pass


def ShowCaret(hWnd:'int') -> 'None':
    """
    Shows the caret at its current position

Args:

      hWnd(int):Window that owns the caret, can be 0.

Returns:

      None

    """
    pass


def ShowWindow(hWnd:'typing.Any',cmdShow:'typing.Any') -> 'typing.Any':
    """
    Shows or hides a window and changes its state

Args:

      hWnd(typing.Any):The handle to the window
      cmdShow(typing.Any):Combination of win32con.SW_* flags

Returns:

      typing.Any

    """
    pass


def IsWindowVisible(hwnd:'int') -> 'typing.Any':
    """
    Indicates if the window has the WS_VISIBLE style.

Args:

      hwnd(typing.Any):The handle to the window

Returns:

      typing.Any

    """
    pass


def IsWindowEnabled(hwnd:'int') -> 'typing.Any':
    """
    Indicates if the window is enabled.

Args:

      hwnd(typing.Any):The handle to the window

Returns:

      typing.Any

    """
    pass


def SetFocus(hwnd:'int') -> 'None':
    """
    Sets focus to the specified window.

Args:

      hwnd(typing.Any):The handle to the window

Returns:

      None

    """
    pass


def GetFocus() -> 'None':
    """
    Returns the HWND of the window with focus.

Args:



Returns:

      None

    """
    pass


def UpdateWindow(hwnd:'int') -> 'None':
    """
    None

Args:

      hwnd(typing.Any):The handle to the window

Returns:

      None

    """
    pass


def BringWindowToTop(hwnd:'int') -> 'None':
    """
    None

Args:

      hwnd(typing.Any):The handle to the window

Returns:

      None

    """
    pass


def SetActiveWindow(hwnd:'int') -> 'typing.Any':
    """
    None

Args:

      hwnd(typing.Any):The handle to the window

Returns:

      typing.Any

    """
    pass


def GetActiveWindow() -> 'typing.Any':
    """
    None

Args:



Returns:

      typing.Any

    """
    pass


def SetForegroundWindow(hwnd:'int') -> 'typing.Any':
    """
    None

Args:

      hwnd(typing.Any):The handle to the window

Returns:

      typing.Any

    """
    pass


def GetForegroundWindow() -> 'typing.Any':
    """
    None

Args:



Returns:

      typing.Any

    """
    pass


def GetClientRect(hwnd:'int') -> 'tuple[int, int, int, int]':
    """
    Returns the rectangle of the client area of a window, in client coordinates

Args:

      hwnd(typing.Any):The handle to the window

Returns:

      tuple[int, int, int, int]

    """
    pass


def GetDC(hwnd:'int') -> 'typing.Any':
    """
    Gets the device context for the window.

Args:

      hwnd(typing.Any):The handle to the window

Returns:

      typing.Any

    """
    pass


def SaveDC(hdc:'int') -> 'typing.Any':
    """
    Save the state of a device context

Args:

      hdc(int):Handle to device contextReturn ValueReturns a value identifying the state that can be passed to win32gui::RestoreDC.  On error, returns 0.

Returns:

      typing.Any:Handle to device contextReturn ValueReturns a value identifying the state that can be passed to win32gui::RestoreDC.  On error, returns 0.


    """
    pass


def RestoreDC(hdc:'int',SavedDC:'typing.Any') -> 'None':
    """
    Restores a device context state

Args:

      hdc(int):Handle to a device context
      SavedDC(typing.Any):Identifier of state to be restored, as returned by win32gui::SaveDC.

Returns:

      None

    """
    pass


def DeleteDC(hdc:'typing.Any') -> 'None':
    """
    Deletes a DC

Args:

      hdc(typing.Any):The source DC

Returns:

      None

    """
    pass


def CreateCompatibleDC(dc:'typing.Any') -> 'typing.Any':
    """
    Creates a memory device context (DC) compatible with the specified device.

Args:

      dc(typing.Any):handle to DC

Returns:

      typing.Any

    """
    pass


def CreateCompatibleBitmap(hdc:'typing.Any',width:'typing.Any',height:'typing.Any') -> 'win32typing.PyGdiHANDLE':
    """
    Creates a bitmap compatible with the device that is associated with the specified device context.

Args:

      hdc(typing.Any):handle to DC
      width(typing.Any):width of bitmap, in pixels
      height(typing.Any):height of bitmap, in pixels

Returns:

      win32typing.PyGdiHANDLE

    """
    pass


def CreateBitmap(width:'typing.Any',height:'typing.Any',cPlanes:'typing.Any',cBitsPerPixel:'typing.Any',bitmap_bits:'typing.Any') -> 'win32typing.PyGdiHANDLE':
    """
    Creates a bitmap

Args:

      width(typing.Any):bitmap width, in pixels
      height(typing.Any):bitmap height, in pixels
      cPlanes(typing.Any):number of color planes
      cBitsPerPixel(typing.Any):number of bits to identify color
      bitmap_bits(typing.Any):Must be None

Returns:

      win32typing.PyGdiHANDLE

    """
    pass


def SelectObject(hdc:'typing.Any',_object:'typing.Any') -> 'typing.Any':
    """
    Selects an object into the specified device context (DC). The new object replaces the previous object of the same type.

Args:

      hdc(typing.Any):handle to DC
      _object(typing.Any):The GDI object

Returns:

      typing.Any

    """
    pass


def GetCurrentObject(hdc:'int',ObjectType:'typing.Any') -> 'int':
    """
    Retrieves currently selected object from a DC

Args:

      hdc(int):Handle to a device context
      ObjectType(typing.Any):Type of object to retrieve, one of win32con.OBJ_*;

Returns:

      int

    """
    pass


def GetWindowRect(hwnd:'int') -> 'tuple[int, int, int, int]':
    """
    Returns the rectangle for a window in screen coordinates

Args:

      hwnd(typing.Any):The handle to the window

Returns:

      tuple[int, int, int, int]

    """
    pass


def GetStockObject(Object:'typing.Any') -> 'int':
    """
    Creates a handle to one of the standard system Gdi objects

Args:

      Object(typing.Any):One of *_BRUSH, *_PEN, *_FONT, or *_PALLETTE constants

Returns:

      int

    """
    pass


def PostQuitMessage(rc:'typing.Any') -> 'None':
    """
    None

Args:

      rc(typing.Any):

Returns:

      None

    """
    pass


def WaitMessage() -> 'None':
    """
    Waits for a message

Args:



Returns:

      None

    """
    pass


def SetWindowPos(hWnd:'int',InsertAfter:'int',X:'typing.Any',Y:'typing.Any',cx:'typing.Any',cy:'typing.Any',Flags:'typing.Any') -> 'None':
    """
    Sets the position and size of a window

Args:

      hWnd(int):Handle to the window
      InsertAfter(int):Window that hWnd will be placed below.  Can be a window handle or one of HWND_BOTTOM,HWND_NOTOPMOST,HWND_TOP, or HWND_TOPMOST
      X(typing.Any):New X coord
      Y(typing.Any):New Y coord
      cx(typing.Any):New width of window
      cy(typing.Any):New height of window
      Flags(typing.Any):Combination of win32con.SWP_* flags

Returns:

      None

    """
    pass


def GetWindowPlacement() -> 'typing.Any':
    """
    Returns placement information about the current window.

Args:



Returns:

      typing.Any:win32gui.GetWindowPlacement

tuple = GetWindowPlacement()Returns placement information about the current window.
Return ValueThe result is a tuple of

(flags, showCmd, (minposX, minposY), (maxposX, maxposY), (normalposX, normalposY))



Item


Description



flagsOne of the WPF_* constants
showCmdCurrent state - one of the SW_* constants.
minposSpecifies the coordinates of the window's upper-left corner when the window is minimized.
maxposSpecifies the coordinates of the window's upper-left corner when the window is maximized.
normalposSpecifies the window's coordinates when the window is in the restored position.


    """
    pass


def SetWindowPlacement(hWnd:'int',placement:'typing.Any') -> 'None':
    """
    Sets the windows placement

Args:

      hWnd(int):Handle to a window
      placement(typing.Any):A tuple representing the WINDOWPLACEMENT structure.

Returns:

      None

    """
    pass


def RegisterClass(wndClass:'win32typing.PyWNDCLASS') -> 'typing.Any':
    """
    Registers a window class.

Args:

      wndClass(win32typing.PyWNDCLASS):An object describing the window class.

Returns:

      typing.Any

    """
    pass


def UnregisterClass(atom:'win32typing.PyResourceId',hinst:'int') -> 'None':
    """
    None

Args:

      atom(win32typing.PyResourceId):The atom or classname identifying the class previously registered.
      hinst(int):The handle to the instance unregistering the class, can be None

Returns:

      None

    """
    pass


def PumpMessages() -> 'None':
    """
    Runs a message loop until a WM_QUIT message is received.

Args:



Returns:

      None:win32gui::PumpWaitingMessages
Return ValueReturns exit code from PostQuitMessage when a WM_QUIT message is received


    """
    pass


def PumpWaitingMessages() -> 'typing.Any':
    """
    Pumps all waiting messages for the current thread.

Args:



Returns:

      typing.Any:Search for PeekMessage and DispatchMessage at msdn, google or google groups.
Return ValueReturns non-zero (exit code from PostQuitMessage) if a WM_QUIT message was received, else 0


    """
    pass


def GetMessage(hwnd:'int',_min:'typing.Any',_max:'typing.Any') -> 'typing.Any':
    """
    None

Args:

      hwnd(typing.Any):
      _min(typing.Any):
      _max(typing.Any):

Returns:

      typing.Any

    """
    pass


def TranslateMessage(msg:'typing.Any') -> 'typing.Any':
    """
    None

Args:

      msg(typing.Any):

Returns:

      typing.Any

    """
    pass


def DispatchMessage(msg:'typing.Any') -> 'typing.Any':
    """
    None

Args:

      msg(typing.Any):

Returns:

      typing.Any

    """
    pass


def TranslateAccelerator(hwnd:'int',haccel:'typing.Any',msg:'typing.Any') -> 'typing.Any':
    """
    None

Args:

      hwnd(typing.Any):
      haccel(typing.Any):
      msg(typing.Any):

Returns:

      typing.Any

    """
    pass


def PeekMessage(hwnd:'int',filterMin:'typing.Any',filterMax:'typing.Any',removalOptions:'typing.Any') -> 'typing.Any':
    """
    None

Args:

      hwnd(typing.Any):
      filterMin(typing.Any):
      filterMax(typing.Any):
      removalOptions(typing.Any):

Returns:

      typing.Any

    """
    pass


def Shell_NotifyIcon(Message:'typing.Any',nid:'win32typing.PyNOTIFYICONDATA') -> 'None':
    """
    Adds, removes or modifies a taskbar icon.

Args:

      Message(typing.Any):One of win32gui.NIM_* flags
      nid(win32typing.PyNOTIFYICONDATA):Tuple containing NOTIFYICONDATA info

Returns:

      None

    """
    pass


def GetSystemMenu(hwnd:'int',bRevert:'typing.Any') -> 'typing.Any':
    """
    None

Args:

      hwnd(typing.Any):The handle to the window
      bRevert(typing.Any):Return ValueThe result is a HMENU to the menu.

Returns:

      typing.Any:Return ValueThe result is a HMENU to the menu.


    """
    pass


def DrawMenuBar(hwnd:'int') -> 'None':
    """
    None

Args:

      hwnd(typing.Any):The handle to the window

Returns:

      None

    """
    pass


def MoveWindow(hwnd:'int',x:'typing.Any',y:'typing.Any',width:'typing.Any',height:'typing.Any',bRepaint:'typing.Any') -> 'None':
    """
    None

Args:

      hwnd(typing.Any):The handle to the window
      x(typing.Any):
      y(typing.Any):
      width(typing.Any):
      height(typing.Any):
      bRepaint(typing.Any):

Returns:

      None

    """
    pass


def CloseWindow() -> 'None':
    """
    None

Args:



Returns:

      None

    """
    pass


def DeleteMenu(hmenu:'typing.Any',position:'typing.Any',flags:'typing.Any') -> 'None':
    """
    None

Args:

      hmenu(typing.Any):The handle to the menu
      position(typing.Any):The position to delete.
      flags(typing.Any):

Returns:

      None

    """
    pass


def RemoveMenu(hmenu:'typing.Any',position:'typing.Any',flags:'typing.Any') -> 'None':
    """
    None

Args:

      hmenu(typing.Any):The handle to the menu
      position(typing.Any):The position to delete.
      flags(typing.Any):

Returns:

      None

    """
    pass


def CreateMenu() -> 'typing.Any':
    """
    None

Args:



Returns:

      typing.Any:win32gui.CreateMenu

int = CreateMenu()
Return ValueThe result is a HMENU to the new menu.


    """
    pass


def CreatePopupMenu() -> 'typing.Any':
    """
    None

Args:



Returns:

      typing.Any:win32gui.CreatePopupMenu

int = CreatePopupMenu()
Return ValueThe result is a HMENU to the new menu.


    """
    pass


def TrackPopupMenu(hmenu:'typing.Any',flags:'typing.Any',x:'typing.Any',y:'typing.Any',reserved:'typing.Any',hwnd:'int',prcRect:'win32typing.PyRECT') -> 'typing.Any':
    """
    Display popup shortcut menu

Args:

      hmenu(typing.Any):The handle to the menu
      flags(typing.Any):flags
      x(typing.Any):x pos
      y(typing.Any):y pos
      reserved(typing.Any):reserved
      hwnd(typing.Any):owner window
      prcRect(win32typing.PyRECT):Pointer to rec (can be None)

Returns:

      typing.Any

    """
    pass


def CommDlgExtendedError() -> 'typing.Any':
    """
    None

Args:



Returns:

      typing.Any

    """
    pass


def ExtractIcon(hinstance:'typing.Any',moduleName:'typing.Union[str]',index:'typing.Any') -> 'typing.Any':
    """
    None

Args:

      hinstance(typing.Any):
      moduleName(typing.Union[str]):
      index(typing.Any):CommentsYou must destroy the icon handle returned by calling the win32gui::DestroyIcon function.Return ValueThe result is a HICON.

Returns:

      typing.Any:Comments

You must destroy the icon handle returned by calling the win32gui::DestroyIcon function.
Return ValueThe result is a HICON.


    """
    pass


def ExtractIconEx(moduleName:'str',index:'typing.Any',numIcons:'typing.Any'=1) -> 'typing.Any':
    """
    None

Args:

      moduleName(str):
      index(typing.Any):
      numIcons(typing.Any):CommentsYou must destroy each icon handle returned by calling the win32gui::DestroyIcon function.Return ValueIf index==-1, the result is an integer with the number of icons in the file, otherwise it is 2 arrays of icon handles.

Returns:

      typing.Any:
Comments

You must destroy each icon handle returned by calling the win32gui::DestroyIcon function.
Return ValueIf index==-1, the result is an integer with the number of icons in

the file, otherwise it is 2 arrays of icon handles.


    """
    pass


def DestroyIcon(hicon:'typing.Any') -> 'None':
    """
    None

Args:

      hicon(typing.Any):The icon to destroy.

Returns:

      None

    """
    pass


def GetIconInfo(hicon:'int') -> 'win32typing.PyICONINFO':
    """
    Returns parameters for an icon or cursor

Args:

      hicon(int):The icon to queryReturn ValueThe result is a tuple of (fIcon, xHotspot, yHotspot, hbmMask, hbmColor) The hbmMask and hbmColor items are bitmaps created for the caller, so must be freed.

Returns:

      win32typing.PyICONINFO:The icon to queryReturn ValueThe result is a tuple of (fIcon, xHotspot, yHotspot, hbmMask, hbmColor)

The hbmMask and hbmColor items are bitmaps created for the caller, so must be freed.


    """
    pass


def ScreenToClient(hWnd:'int',Point:'tuple[typing.Any, typing.Any]') -> 'tuple[typing.Any, typing.Any]':
    """
    Convert screen coordinates to client coords

Args:

      hWnd(int):Handle to a window
      Point(tuple[typing.Any, typing.Any]):Screen coordinates to be converted

Returns:

      tuple[typing.Any, typing.Any]

    """
    pass


def ClientToScreen(hWnd:'int',Point:'tuple[typing.Any, typing.Any]') -> 'tuple[typing.Any, typing.Any]':
    """
    Convert client coordinates to screen coords

Args:

      hWnd(int):Handle to a window
      Point(tuple[typing.Any, typing.Any]):Client coordinates to be converted

Returns:

      tuple[typing.Any, typing.Any]

    """
    pass


def PaintDesktop(hdc:'int') -> 'None':
    """
    Fills a DC with the destop background

Args:

      hdc(int):Handle to a device context

Returns:

      None

    """
    pass


def RedrawWindow(hWnd:'int',rcUpdate:'tuple[int, int, int, int]',hrgnUpdate:'win32typing.PyGdiHANDLE',flags:'typing.Any') -> 'None':
    """
    Causes a portion of a window to be redrawn

Args:

      hWnd(int):Handle to window to be redrawn
      rcUpdate(tuple[int, int, int, int]):Rectangle (left, top, right, bottom) identifying part of window to be redrawn, can be None
      hrgnUpdate(win32typing.PyGdiHANDLE):Handle to region to be redrawn, can be None to indicate entire client area
      flags(typing.Any):Combination of win32con.RDW_* flags

Returns:

      None

    """
    pass


def GetTextExtentPoint32(hdc:'int',_str:'str') -> 'tuple[typing.Any, typing.Any]':
    """
    Computes the width and height of the specified string of text.

Args:

      hdc(int):The device context
      _str(str):The string to measure.

Returns:

      tuple[typing.Any, typing.Any]

    """
    pass


def GetTextMetrics() -> 'typing.Any':
    """
    Returns info for the font selected into a DC

Args:



Returns:

      typing.Any

    """
    pass


def GetTextCharacterExtra(hdc:'int') -> 'typing.Any':
    """
    Returns the space between characters

Args:

      hdc(int):Handle to a device context

Returns:

      typing.Any

    """
    pass


def SetTextCharacterExtra(hdc:'int',CharExtra:'typing.Any') -> 'typing.Any':
    """
    Sets the spacing between characters

Args:

      hdc(int):Handle to a device context
      CharExtra(typing.Any):Space between adjacent chars, in logical unitsReturn ValueReturns the previous spacing

Returns:

      typing.Any:Space between adjacent chars, in logical unitsReturn ValueReturns the previous spacing


    """
    pass


def GetTextAlign(hdc:'int') -> 'typing.Any':
    """
    Returns horizontal and vertical alignment for text in a device context

Args:

      hdc(int):Handle to a device contextReturn ValueReturns combination of win32con.TA_* flags

Returns:

      typing.Any:Handle to a device contextReturn ValueReturns combination of win32con.TA_* flags


    """
    pass


def SetTextAlign(hdc:'int',Mode:'typing.Any') -> 'typing.Any':
    """
    Sets horizontal and vertical alignment for text in a device context

Args:

      hdc(int):Handle to a device context
      Mode(typing.Any):Combination of win32con.TA_* constantsReturn ValueReturns the previous alignment flags

Returns:

      typing.Any:Combination of win32con.TA_* constantsReturn ValueReturns the previous alignment flags


    """
    pass


def GetTextFace(hdc:'int') -> 'str':
    """
    Retrieves the name of the font currently selected in a DC

Args:

      hdc(int):Handle to a device contextCommentsCalls unicode api function (GetTextFaceW)

Returns:

      str

    """
    pass


def GetMapMode(hdc:'int') -> 'typing.Any':
    """
    Returns the method a device context uses to translate logical units to physical units

Args:

      hdc(int):Handle to a device contextReturn ValueReturns one of win32con.MM_* values

Returns:

      typing.Any:Handle to a device contextReturn ValueReturns one of win32con.MM_* values


    """
    pass


def SetMapMode(hdc:'int',MapMode:'typing.Any') -> 'typing.Any':
    """
    Sets the method used for translating logical units to device units

Args:

      hdc(int):Handle to a device context
      MapMode(typing.Any):The new mapping mode (win32con.MM_*)Return ValueReturns the previous mapping mode, one of win32con.MM_* constants

Returns:

      typing.Any:The new mapping mode (win32con.MM_*)Return ValueReturns the previous mapping mode, one of win32con.MM_* constants


    """
    pass


def GetGraphicsMode(hdc:'int') -> 'typing.Any':
    """
    Determines if advanced GDI features are enabled for a device context

Args:

      hdc(int):Handle to a device contextReturn ValueReturns GM_COMPATIBLE or GM_ADVANCED

Returns:

      typing.Any:Handle to a device contextReturn ValueReturns GM_COMPATIBLE or GM_ADVANCED


    """
    pass


def SetGraphicsMode(hdc:'int',Mode:'typing.Any') -> 'typing.Any':
    """
    Enables or disables advanced graphics features for a DC

Args:

      hdc(int):Handle to a device context
      Mode(typing.Any):GM_COMPATIBLE or GM_ADVANCED (from win32con)Return ValueReturns the previous mode, one of win32con.GM_COMPATIBLE or win32con.GM_ADVANCED

Returns:

      typing.Any:GM_COMPATIBLE or GM_ADVANCED (from win32con)Return ValueReturns the previous mode, one of win32con.GM_COMPATIBLE or win32con.GM_ADVANCED


    """
    pass


def GetLayout(hdc:'int') -> 'typing.Any':
    """
    Retrieves the layout mode of a device context

Args:

      hdc(int):Handle to a device contextReturn ValueReturns one of win32con.LAYOUT_*

Returns:

      typing.Any:Handle to a device contextReturn ValueReturns one of win32con.LAYOUT_*


    """
    pass


def SetLayout(hdc:'int',Layout:'typing.Any') -> 'typing.Any':
    """
    Sets the layout for a device context

Args:

      hdc(int):Handle to a device context
      Layout(typing.Any):One of win32con.LAYOUT_* constantsReturn ValueReturns the previous layout mode

Returns:

      typing.Any:One of win32con.LAYOUT_* constantsReturn ValueReturns the previous layout mode


    """
    pass


def GetPolyFillMode(hdc:'int') -> 'typing.Any':
    """
    Returns the polygon filling mode for a device context

Args:

      hdc(int):Handle to a device contextReturn ValueReturns win32con.ALTERNATE or win32con.WINDING

Returns:

      typing.Any:Handle to a device contextReturn ValueReturns win32con.ALTERNATE or win32con.WINDING


    """
    pass


def SetPolyFillMode(hdc:'int',PolyFillMode:'typing.Any') -> 'typing.Any':
    """
    Sets the polygon filling mode for a device context

Args:

      hdc(int):Handle to a device context
      PolyFillMode(typing.Any):One of ALTERNATE or WINDINGReturn ValueReturns the previous mode, one of win32con.ALTERNATE or win32con.WINDING

Returns:

      typing.Any:One of ALTERNATE or WINDINGReturn ValueReturns the previous mode, one of win32con.ALTERNATE or win32con.WINDING


    """
    pass


def GetWorldTransform(hdc:'int') -> 'win32typing.PyXFORM':
    """
    Retrieves a device context's coordinate space translation matrix

Args:

      hdc(int):Handle to a device contextCommentsDC's mode must be set to GM_ADVANCED.  See win32gui::SetGraphicsMode.

Returns:

      win32typing.PyXFORM

    """
    pass


def SetWorldTransform(hdc:'int',Xform:'win32typing.PyXFORM') -> 'None':
    """
    Transforms a device context's coordinate space

Args:

      hdc(int):Handle to a device context
      Xform(win32typing.PyXFORM):Matrix defining the transformationCommentsDC's mode must be set to GM_ADVANCED.  See win32gui::SetGraphicsMode.

Returns:

      None

    """
    pass


def ModifyWorldTransform(hdc:'int',Xform:'win32typing.PyXFORM',Mode:'typing.Any') -> 'None':
    """
    Combines a coordinate tranformation with device context's current transformation

Args:

      hdc(int):Handle to a device context
      Xform(win32typing.PyXFORM):Transformation to be applied.  Ignored if Mode is MWT_IDENTITY.
      Mode(typing.Any):One of win32con.MWT_* values specifying how transformations will be combinedCommentsDC's mode must be set to GM_ADVANCED.  See win32gui::SetGraphicsMode.

Returns:

      None

    """
    pass


def CombineTransform(xform1:'win32typing.PyXFORM',xform2:'win32typing.PyXFORM') -> 'win32typing.PyXFORM':
    """
    Combines two coordinate space transformations

Args:

      xform1(win32typing.PyXFORM):First transformation
      xform2(win32typing.PyXFORM):Second transformation

Returns:

      win32typing.PyXFORM

    """
    pass


def GetWindowOrgEx(hdc:'int') -> 'tuple[typing.Any, typing.Any]':
    """
    Retrievs the window origin for a DC

Args:

      hdc(int):Handle to a device context

Returns:

      tuple[typing.Any, typing.Any]

    """
    pass


def SetWindowOrgEx(hdc:'int',X:'typing.Any',Y:'typing.Any') -> 'tuple[typing.Any, typing.Any]':
    """
    Changes the window origin for a DC

Args:

      hdc(int):Handle to a device context
      X(typing.Any):New X coord in logical units
      Y(typing.Any):New Y coord in logical unitsReturn ValueReturns the previous origin

Returns:

      tuple[typing.Any, typing.Any]:New Y coord in logical unitsReturn ValueReturns the previous origin


    """
    pass


def GetViewportOrgEx(hdc:'int') -> 'tuple[typing.Any, typing.Any]':
    """
    Retrievs the origin for a DC's viewport

Args:

      hdc(int):Handle to a device context

Returns:

      tuple[typing.Any, typing.Any]

    """
    pass


def SetViewportOrgEx(hdc:'int',X:'typing.Any',Y:'typing.Any') -> 'tuple[typing.Any, typing.Any]':
    """
    Changes the viewport origin for a DC

Args:

      hdc(int):Handle to a device context
      X(typing.Any):New X coord in logical units
      Y(typing.Any):New Y coord in logical unitsReturn ValueReturns the previous origin as (x,y)

Returns:

      tuple[typing.Any, typing.Any]:New Y coord in logical unitsReturn ValueReturns the previous origin as (x,y)


    """
    pass


def GetWindowExtEx(hdc:'int') -> 'tuple[typing.Any, typing.Any]':
    """
    Retrieves the window extents for a DC

Args:

      hdc(int):Handle to a device contextReturn ValueReturns the extents as (x,y) in logical units

Returns:

      tuple[typing.Any, typing.Any]:Handle to a device contextReturn ValueReturns the extents as (x,y) in logical units


    """
    pass


def SetWindowExtEx(hdc:'int',XExtent:'typing.Any',YExtent:'typing.Any') -> 'tuple[typing.Any, typing.Any]':
    """
    Changes the window extents for a DC

Args:

      hdc(int):Handle to a device context
      XExtent(typing.Any):New X extent in logical units
      YExtent(typing.Any):New Y extent in logical unitsReturn ValueReturns the previous extents

Returns:

      tuple[typing.Any, typing.Any]:New Y extent in logical unitsReturn ValueReturns the previous extents


    """
    pass


def GetViewportExtEx(hdc:'int') -> 'tuple[typing.Any, typing.Any]':
    """
    Retrieves the viewport extents for a DC

Args:

      hdc(int):Handle to a device contextReturn ValueReturns the extents as (x,y) in logical units

Returns:

      tuple[typing.Any, typing.Any]:Handle to a device contextReturn ValueReturns the extents as (x,y) in logical units


    """
    pass


def SetViewportExtEx(hdc:'int',XExtent:'typing.Any',YExtent:'typing.Any') -> 'tuple[typing.Any, typing.Any]':
    """
    Changes the viewport extents for a DC

Args:

      hdc(int):Handle to a device context
      XExtent(typing.Any):New X extent in logical units
      YExtent(typing.Any):New Y extent in logical unitsReturn ValueReturns the previous extents as (x,y) in logical units

Returns:

      tuple[typing.Any, typing.Any]:New Y extent in logical unitsReturn ValueReturns the previous extents as (x,y) in logical units


    """
    pass


def GradientFill(hdc:'typing.Any',Vertex:'tuple[win32typing.PyTRIVERTEX, ...]',Mesh:'typing.Any',Mode:'typing.Any') -> 'None':
    """
    Shades triangles or rectangles by interpolating between vertex colors

Args:

      hdc(typing.Any):Handle to device context
      Vertex(tuple[win32typing.PyTRIVERTEX, ...]):Sequence of TRIVERTEX dicts defining color info
      Mesh(typing.Any):Sequence of tuples containing either 2 or 3 ints that index into the trivertex array to define either triangles or rectangles
      Mode(typing.Any):win32con.GRADIENT_FILL_* value defining whether to fill by triangle or by rectangle

Returns:

      None

    """
    pass


def GetOpenFileName(OPENFILENAME:'typing.Union[str, typing.Any]') -> 'typing.Any':
    """
    Creates an Open dialog box that lets the user specify the drive, directory, and the name of a file or set of files to open.

Args:

      OPENFILENAME(typing.Union[str, typing.Any]):A string packed into an OPENFILENAME structure, probably via the struct module.CommentsThe win32gui::GetOpenFileNameW function is far more convenient to use.Return ValueIf the user presses OK, the function returns TRUE.  Otherwise, use CommDlgExtendedError for error details (ie, a win32gui.error is raised).  If the user cancels the dialog, the winerror attribute of the exception will be zero.

Returns:

      typing.Any:A string packed into an OPENFILENAME structure, probably via the struct module.Comments

The win32gui::GetOpenFileNameW function is far more convenient to use.
Return ValueIf the user presses OK, the function returns TRUE.  Otherwise, use CommDlgExtendedError for error details

(ie, a win32gui.error is raised).  If the user cancels the dialog, the winerror attribute of the exception will be zero.


    """
    pass


def InsertMenuItem(hMenu:'typing.Any',uItem:'typing.Any',fByPosition:'typing.Any',menuItem:'typing.Any') -> 'None':
    """
    Inserts a menu item

Args:

      hMenu(typing.Any):Handle to the menu
      uItem(typing.Any):The menu item identifier or the menu item position.
      fByPosition(typing.Any):Boolean value of True if uItem is set to a menu item position. This parameter is set to False if uItem is set to a menu item identifier.
      menuItem(typing.Any):A string or buffer in the format of a MENUITEMINFO structure.

Returns:

      None

    """
    pass


def SetMenuItemInfo(hMenu:'typing.Any',uItem:'typing.Any',fByPosition:'typing.Any',menuItem:'typing.Any') -> 'None':
    """
    Sets menu information

Args:

      hMenu(typing.Any):Handle to the menu
      uItem(typing.Any):The menu item identifier or the menu item position.
      fByPosition(typing.Any):Boolean value of True if uItem is set to a menu item position. This parameter is set to False if uItem is set to a menu item identifier.
      menuItem(typing.Any):A string or buffer in the format of a MENUITEMINFO structure.

Returns:

      None

    """
    pass


def GetMenuItemInfo(hMenu:'typing.Any',uItem:'typing.Any',fByPosition:'typing.Any',menuItem:'typing.Any') -> 'None':
    """
    Gets menu information

Args:

      hMenu(typing.Any):Handle to the menu
      uItem(typing.Any):The menu item identifier or the menu item position.
      fByPosition(typing.Any):Boolean value of True if uItem is set to a menu item position. This parameter is set to False if uItem is set to a menu item identifier.
      menuItem(typing.Any):A string or buffer in the format of a MENUITEMINFO structure.

Returns:

      None

    """
    pass


def GetMenuItemCount(hMenu:'typing.Any') -> 'typing.Any':
    """
    None

Args:

      hMenu(typing.Any):Handle to the menu

Returns:

      typing.Any

    """
    pass


def GetMenuItemRect(hWnd:'typing.Any',hMenu:'typing.Any',uItem:'typing.Any') -> 'tuple[int, int, int, int]':
    """
    None

Args:

      hWnd(typing.Any):
      hMenu(typing.Any):Handle to the menu
      uItem(typing.Any):

Returns:

      tuple[int, int, int, int]

    """
    pass


def GetMenuState(hMenu:'typing.Any',uID:'typing.Any',flags:'typing.Any') -> 'typing.Any':
    """
    None

Args:

      hMenu(typing.Any):Handle to the menu
      uID(typing.Any):
      flags(typing.Any):

Returns:

      typing.Any

    """
    pass


def SetMenuDefaultItem(hMenu:'typing.Any',uItem:'typing.Any',fByPos:'typing.Any') -> 'None':
    """
    None

Args:

      hMenu(typing.Any):Handle to the menu
      uItem(typing.Any):
      fByPos(typing.Any):

Returns:

      None

    """
    pass


def GetMenuDefaultItem(hMenu:'typing.Any',fByPos:'typing.Any',flags:'typing.Any') -> 'typing.Any':
    """
    None

Args:

      hMenu(typing.Any):Handle to the menu
      fByPos(typing.Any):
      flags(typing.Any):

Returns:

      typing.Any

    """
    pass


def AppendMenu() -> 'None':
    """
    None

Args:



Returns:

      None

    """
    pass


def InsertMenu() -> 'None':
    """
    None

Args:



Returns:

      None

    """
    pass


def EnableMenuItem() -> 'None':
    """
    None

Args:



Returns:

      None

    """
    pass


def CheckMenuItem() -> 'typing.Any':
    """
    None

Args:



Returns:

      typing.Any

    """
    pass


def GetSubMenu(hMenu:'typing.Any',nPos:'typing.Any') -> 'typing.Any':
    """
    None

Args:

      hMenu(typing.Any):Handle to the menu
      nPos(typing.Any):

Returns:

      typing.Any

    """
    pass


def ModifyMenu(hMnu:'typing.Any',uPosition:'typing.Any',uFlags:'typing.Any',uIDNewItem:'typing.Any',newItem:'str') -> 'None':
    """
    Changes an existing menu item. This function is used to specify the content, appearance, and behavior of the menu item.

Args:

      hMnu(typing.Any):handle to menu
      uPosition(typing.Any):menu item to modify
      uFlags(typing.Any):options
      uIDNewItem(typing.Any):identifier, menu, or submenu
      newItem(str):menu item content

Returns:

      None

    """
    pass


def GetMenuItemID(hMenu:'typing.Any',nPos:'typing.Any') -> 'typing.Any':
    """
    Retrieves the menu item identifier of a menu item located at the specified position in a menu.

Args:

      hMenu(typing.Any):handle to menu
      nPos(typing.Any):position of menu item

Returns:

      typing.Any

    """
    pass


def SetMenuItemBitmaps(hMenu:'typing.Any',uPosition:'typing.Any',uFlags:'typing.Any',hBitmapUnchecked:'win32typing.PyGdiHANDLE',hBitmapChecked:'win32typing.PyGdiHANDLE') -> 'None':
    """
    Associates the specified bitmap with a menu item. Whether the menu item is selected or clear, the system displays the appropriate bitmap next to the menu item.

Args:

      hMenu(typing.Any):handle to menu
      uPosition(typing.Any):menu item
      uFlags(typing.Any):options
      hBitmapUnchecked(win32typing.PyGdiHANDLE):handle to unchecked bitmap, can be None
      hBitmapChecked(win32typing.PyGdiHANDLE):handle to checked bitmap, can be None

Returns:

      None

    """
    pass


def CheckMenuRadioItem(hMenu:'typing.Any',idFirst:'typing.Any',idLast:'typing.Any',idCheck:'typing.Any',uFlags:'typing.Any') -> 'None':
    """
    Checks a specified menu item and makes it a

radio item. At the same time, the function clears all other menu items in

the associated group and clears the radio-item type flag for those items.

Args:

      hMenu(typing.Any):handle to menu
      idFirst(typing.Any):identifier or position of first item
      idLast(typing.Any):identifier or position of last item
      idCheck(typing.Any):identifier or position of item to check
      uFlags(typing.Any):options

Returns:

      None

    """
    pass


def SetMenuInfo(hmenu:'typing.Any',info:'typing.Any') -> 'None':
    """
    Sets information for a specified menu.

Args:

      hmenu(typing.Any):handle to menu
      info(typing.Any):menu information in the format of a buffer.CommentsSee win32gui_struct for helper functions.This function will raise NotImplementedError on early platforms (eg, Windows NT.)

Returns:

      None

    """
    pass


def GetMenuInfo(hmenu:'typing.Any',info:'typing.Any') -> 'None':
    """
    Gets information about a specified menu.

Args:

      hmenu(typing.Any):handle to menu
      info(typing.Any):A buffer to fill with the information.CommentsSee win32gui_struct for helper functions.This function will raise NotImplementedError on early platforms (eg, Windows NT.)

Returns:

      None

    """
    pass


def DrawFocusRect(hDC:'int',rc:'tuple[int, int, int, int]') -> 'None':
    """
    Draws a standard focus outline around a rectangle

Args:

      hDC(int):Handle to a device context
      rc(tuple[int, int, int, int]):Tuple of (left,top,right,bottom) defining the rectangle

Returns:

      None

    """
    pass


def DrawText(hDC:'typing.Union[typing.Any, int]',String:'typing.Any',nCount:'typing.Any',Rect:'win32typing.PyRECT',Format:'typing.Any') -> 'tuple[typing.Any, win32typing.PyRECT]':
    """
    Draws formatted text on a device context

Args:

      hDC(typing.Union[typing.Any, int]):The device context on which to draw
      String(typing.Any):The text to be drawn
      nCount(typing.Any):The number of characters, use -1 for simple null-terminated string
      Rect(win32typing.PyRECT):Tuple of 4 ints specifying the position (left, top, right, bottom)
      Format(typing.Any):Formatting flags, combination of win32con.DT_* valuesReturn ValueReturns the height of the drawn text, and the rectangle coordinates

Returns:

      tuple[typing.Any, win32typing.PyRECT]:Formatting flags, combination of win32con.DT_* valuesReturn ValueReturns the height of the drawn text, and the rectangle coordinates


    """
    pass


def LineTo(hdc:'int',XEnd:'typing.Any',YEnd:'typing.Any') -> 'None':
    """
    Draw a line from current position to specified point

Args:

      hdc(int):Handle to a device context
      XEnd(typing.Any):Horizontal position in logical units
      YEnd(typing.Any):Vertical position in logical units

Returns:

      None

    """
    pass


def Ellipse(hdc:'int',LeftRect:'typing.Any',TopRect:'typing.Any',RightRect:'typing.Any',BottomRect:'typing.Any') -> 'None':
    """
    Draws a filled ellipse on a device context

Args:

      hdc(int):Device context on which to draw
      LeftRect(typing.Any):Left limit of ellipse
      TopRect(typing.Any):Top limit of ellipse
      RightRect(typing.Any):Right limit of ellipse
      BottomRect(typing.Any):Bottom limit of ellipse

Returns:

      None

    """
    pass


def Pie(hdc:'int',LeftRect:'typing.Any',TopRect:'typing.Any',RightRect:'typing.Any',BottomRect:'typing.Any',XRadial1:'typing.Any',YRadial1:'typing.Any',XRadial2:'typing.Any',YRadial2:'typing.Any') -> 'None':
    """
    Draws a section of an ellipse cut by 2 radials

Args:

      hdc(int):Device context on which to draw
      LeftRect(typing.Any):Left limit of ellipse
      TopRect(typing.Any):Top limit of ellipse
      RightRect(typing.Any):Right limit of ellipse
      BottomRect(typing.Any):Bottom limit of ellipse
      XRadial1(typing.Any):Horizontal pos of Radial1 endpoint
      YRadial1(typing.Any):Vertical pos of Radial1 endpoint
      XRadial2(typing.Any):Horizontal pos of Radial2 endpoint
      YRadial2(typing.Any):Vertical pos of Radial2 endpoint

Returns:

      None

    """
    pass


def Arc(hdc:'int',LeftRect:'typing.Any',TopRect:'typing.Any',RightRect:'typing.Any',BottomRect:'typing.Any',XRadial1:'typing.Any',YRadial1:'typing.Any',XRadial2:'typing.Any',YRadial2:'typing.Any') -> 'None':
    """
    Draws an arc defined by an ellipse and 2 radials

Args:

      hdc(int):Device context on which to draw
      LeftRect(typing.Any):Left limit of ellipse
      TopRect(typing.Any):Top limit of ellipse
      RightRect(typing.Any):Right limit of ellipse
      BottomRect(typing.Any):Bottom limit of ellipse
      XRadial1(typing.Any):Horizontal pos of Radial1 endpoint
      YRadial1(typing.Any):Vertical pos of Radial1 endpoint
      XRadial2(typing.Any):Horizontal pos of Radial2 endpoint
      YRadial2(typing.Any):Vertical pos of Radial2 endpoint

Returns:

      None

    """
    pass


def ArcTo(hdc:'int',LeftRect:'typing.Any',TopRect:'typing.Any',RightRect:'typing.Any',BottomRect:'typing.Any',XRadial1:'typing.Any',YRadial1:'typing.Any',XRadial2:'typing.Any',YRadial2:'typing.Any') -> 'None':
    """
    Draws an arc defined by an ellipse and 2 radials

Args:

      hdc(int):Device context on which to draw
      LeftRect(typing.Any):Left limit of ellipse
      TopRect(typing.Any):Top limit of ellipse
      RightRect(typing.Any):Right limit of ellipse
      BottomRect(typing.Any):Bottom limit of ellipse
      XRadial1(typing.Any):Horizontal pos of Radial1 endpoint
      YRadial1(typing.Any):Vertical pos of Radial1 endpoint
      XRadial2(typing.Any):Horizontal pos of Radial2 endpoint
      YRadial2(typing.Any):Vertical pos of Radial2 endpointCommentsDraws exactly as win32gui::Arc, but changes current drawing position

Returns:

      None

    """
    pass


def AngleArc(hdc:'int',Y:'typing.Any',Y1:'typing.Any',Radius:'typing.Any',StartAngle:'float',SweepAngle:'float') -> 'None':
    """
    Draws a line from current pos and a section of a circle's arc

Args:

      hdc(int):Handle to a device context
      Y(typing.Any):x pos of circle
      Y1(typing.Any):y pos of circle
      Radius(typing.Any):Radius of circle
      StartAngle(float):Angle where arc starts, in degrees
      SweepAngle(float):Angle that arc covers, in degrees

Returns:

      None

    """
    pass


def Chord(hdc:'int',LeftRect:'typing.Any',TopRect:'typing.Any',RightRect:'typing.Any',BottomRect:'typing.Any',XRadial1:'typing.Any',YRadial1:'typing.Any',XRadial2:'typing.Any',YRadial2:'typing.Any') -> 'None':
    """
    Draws a chord defined by an ellipse and 2 radials

Args:

      hdc(int):Device context on which to draw
      LeftRect(typing.Any):Left limit of ellipse
      TopRect(typing.Any):Top limit of ellipse
      RightRect(typing.Any):Right limit of ellipse
      BottomRect(typing.Any):Bottom limit of ellipse
      XRadial1(typing.Any):Horizontal pos of Radial1 endpoint
      YRadial1(typing.Any):Vertical pos of Radial1 endpoint
      XRadial2(typing.Any):Horizontal pos of Radial2 endpoint
      YRadial2(typing.Any):Vertical pos of Radial2 endpoint

Returns:

      None

    """
    pass


def ExtFloodFill(arg:'int',XStart:'typing.Any',YStart:'typing.Any',Color:'typing.Any',FillType:'typing.Any') -> 'None':
    """
    Fills an area with current brush

Args:

      arg(int):Handle to a device context
      XStart(typing.Any):Horizontal starting pos
      YStart(typing.Any):Vertical starting pos
      Color(typing.Any):RGB color value.  See win32api::RGB.
      FillType(typing.Any):One of win32con.FLOODFILL* values

Returns:

      None

    """
    pass


def SetPixel(hdc:'int',X:'typing.Any',Y:'typing.Any',Color:'typing.Any') -> 'typing.Any':
    """
    Set the color of a single pixel

Args:

      hdc(int):Handle to a device context
      X(typing.Any):Horizontal pos
      Y(typing.Any):Vertical pos
      Color(typing.Any):RGB color to be set.Return ValueReturns the RGB color actually set, which may be different from the one passed in

Returns:

      typing.Any:RGB color to be set.Return ValueReturns the RGB color actually set, which may be different from the one passed in


    """
    pass


def GetPixel(hdc:'int',XPos:'typing.Any',YPos:'typing.Any') -> 'typing.Any':
    """
    Returns the RGB color of a single pixel

Args:

      hdc(int):Handle to a device context
      XPos(typing.Any):Horizontal pos
      YPos(typing.Any):Vertical pos

Returns:

      typing.Any

    """
    pass


def GetROP2(hdc:'int') -> 'typing.Any':
    """
    Returns the foreground mixing mode of a DC

Args:

      hdc(int):Handle to a device contextReturn ValueReturns one of win32con.R2_* values

Returns:

      typing.Any:Handle to a device contextReturn ValueReturns one of win32con.R2_* values


    """
    pass


def SetROP2(hdc:'int',DrawMode:'typing.Any') -> 'typing.Any':
    """
    Sets the foreground mixing mode of a DC

Args:

      hdc(int):Handle to a device context
      DrawMode(typing.Any):Mixing mode, one of win32con.R2_*.Return ValueReturns previous mode

Returns:

      typing.Any:Mixing mode, one of win32con.R2_*.Return ValueReturns previous mode


    """
    pass


def SetPixelV(hdc:'int',X:'typing.Any',Y:'typing.Any',Color:'typing.Any') -> 'None':
    """
    Sets the color of a single pixel to an approximation of specified color

Args:

      hdc(int):Handle to a device context
      X(typing.Any):Horizontal pos
      Y(typing.Any):Vertical pos
      Color(typing.Any):RGB color to be set.

Returns:

      None

    """
    pass


def MoveToEx(hdc:'int',X:'typing.Any',Y:'typing.Any') -> 'tuple[typing.Any, typing.Any]':
    """
    Changes the current drawing position

Args:

      hdc(int):Device context handle
      X(typing.Any):Horizontal pos in logical units
      Y(typing.Any):Vertical pos in logical unitsReturn ValueReturns the previous position as (X, Y)

Returns:

      tuple[typing.Any, typing.Any]:Vertical pos in logical unitsReturn ValueReturns the previous position as (X, Y)


    """
    pass


def GetCurrentPositionEx(hdc:'int') -> 'tuple[typing.Any, typing.Any]':
    """
    Returns a device context's current drawing position

Args:

      hdc(int):Device context

Returns:

      tuple[typing.Any, typing.Any]

    """
    pass


def GetArcDirection(hdc:'int') -> 'typing.Any':
    """
    Returns the direction in which rectangles and arcs are drawn

Args:

      hdc(int):Handle to a device contextReturn ValueRecturns one of win32con.AD_* values

Returns:

      typing.Any:Handle to a device contextReturn ValueRecturns one of win32con.AD_* values


    """
    pass


def SetArcDirection(hdc:'int',ArcDirection:'typing.Any') -> 'typing.Any':
    """
    Sets the drawing direction for arcs and rectangles

Args:

      hdc(int):Handle to a device context
      ArcDirection(typing.Any):One of win32con.AD_* constantsReturn ValueReturns the previous direction, or 0 on error.

Returns:

      typing.Any:One of win32con.AD_* constantsReturn ValueReturns the previous direction, or 0 on error.


    """
    pass


def Polygon(hdc:'int',Points:'typing.List[tuple[typing.Any, typing.Any]]') -> 'None':
    """
    Draws a closed filled polygon defined by a sequence of points

Args:

      hdc(int):Handle to a device context
      Points(typing.List[tuple[typing.Any, typing.Any]]):Sequence of POINT tuples: ((x,y),...)

Returns:

      None

    """
    pass


def Polyline(hdc:'int',Points:'typing.List[tuple[typing.Any, typing.Any]]') -> 'None':
    """
    Connects a sequence of points using currently selected pen

Args:

      hdc(int):Handle to a device context
      Points(typing.List[tuple[typing.Any, typing.Any]]):Sequence of POINT tuples: ((x,y),...)

Returns:

      None

    """
    pass


def PolylineTo(hdc:'int',Points:'typing.List[tuple[typing.Any, typing.Any]]') -> 'None':
    """
    Draws a series of lines starting from current position.  Updates current position with end point.

Args:

      hdc(int):Handle to a device context
      Points(typing.List[tuple[typing.Any, typing.Any]]):Sequence of POINT tuples: ((x,y),...)

Returns:

      None

    """
    pass


def PolyBezier(hdc:'int',Points:'typing.List[tuple[typing.Any, typing.Any]]') -> 'None':
    """
    Draws a series of Bezier curves starting from first point specified.

Args:

      hdc(int):Handle to a device context
      Points(typing.List[tuple[typing.Any, typing.Any]]):Sequence of POINT tuples: ((x,y),...).CommentsNumber of points must be a multiple of 3 plus 1.

Returns:

      None

    """
    pass


def PolyBezierTo(hdc:'int',Points:'typing.List[tuple[typing.Any, typing.Any]]') -> 'None':
    """
    Draws a series of Bezier curves starting from current drawing position.

Args:

      hdc(int):Handle to a device context
      Points(typing.List[tuple[typing.Any, typing.Any]]):Sequence of POINT tuples: ((x,y),...).CommentsPoints must contain 3 points for each curve.  Current position is updated with last endpoint.

Returns:

      None

    """
    pass


def PlgBlt(Dest:'int',Point:'typing.Any',Src:'int',XSrc:'typing.Any',YSrc:'typing.Any',Width:'typing.Any',Height:'typing.Any',Mask:'win32typing.PyGdiHANDLE'=None,xMask:'typing.Any'=0,yMask:'typing.Any'=0) -> 'None':
    """
    Copies color from a rectangle into a parallelogram

Args:

      Dest(int):Destination DC
      Point(typing.Any):Sequence of 3 POINT tuples (x,y) describing a paralellogram
      Src(int):Source device context
      XSrc(typing.Any):Left edge of source rectangle
      YSrc(typing.Any):Top of source rectangle
      Width(typing.Any):Width of source rectangle
      Height(typing.Any):Height of source rectangle
      Mask(win32typing.PyGdiHANDLE):Handle to monochrome bitmap to mask source, can be None
      xMask(typing.Any):x pos in mask
      yMask(typing.Any):y pos in mask

Returns:

      None

    """
    pass


def CreatePolygonRgn(Points:'typing.List[tuple[typing.Any, typing.Any]]',PolyFillMode:'typing.Any') -> 'win32typing.PyGdiHANDLE':
    """
    Creates a region from a sequence of vertices

Args:

      Points(typing.List[tuple[typing.Any, typing.Any]]):Sequence of POINT tuples: ((x,y),...).
      PolyFillMode(typing.Any):Filling mode, one of ALTERNATE, WINDING

Returns:

      win32typing.PyGdiHANDLE

    """
    pass


def ExtTextOut(hdc:'int',_int:'typing.Any',_int1:'typing.Any',_int2:'typing.Any',rect:'win32typing.PyRECT',string:'typing.Any',_tuple:'tuple[tuple[typing.Any, typing.Any], ...]') -> 'typing.Any':
    """
    Writes text to a DC.

Args:

      hdc(int):Handle to a device context
      _int(typing.Any):The x coordinate to write the text to.
      _int1(typing.Any):The y coordinate to write the text to.
      _int2(typing.Any):Specifies the rectangle type. This parameter can be one, both, or neither of ETO_CLIPPED and ETO_OPAQUE
      rect(win32typing.PyRECT):Specifies the text's bounding rectangle.  (Can be None.)
      string(typing.Any):The text to write.
      _tuple(tuple[tuple[typing.Any, typing.Any], ...]):Optional array of values that indicate distance between origins of character cells.Win32 API References

Returns:

      typing.Any:Search for ExtTextOut at msdn, google or google groups.
Return ValueAlways none.  If the function fails, an exception is raised.


    """
    pass


def GetTextColor(hdc:'typing.Any') -> 'typing.Any':
    """
    Returns the text color for a DC

Args:

      hdc(typing.Any):Handle to a device contextReturn ValueReturns an RGB color.  On error, returns CLR_INVALID

Returns:

      typing.Any:Handle to a device contextReturn ValueReturns an RGB color.  On error, returns CLR_INVALID


    """
    pass


def SetTextColor(hdc:'typing.Any',color:'typing.Any') -> 'typing.Any':
    """
    Changes the text color for a device context

Args:

      hdc(typing.Any):Handle to a device context
      color(typing.Any):The RGB color value - see win32api::RGBReturn ValueReturns the previous color, or CLR_INVALID on failure

Returns:

      typing.Any:The RGB color value - see win32api::RGBReturn ValueReturns the previous color, or CLR_INVALID on failure


    """
    pass


def GetBkMode(hdc:'int') -> 'typing.Any':
    """
    Returns the background mode for a device context

Args:

      hdc(int):Handle to a device contextReturn ValueReturns OPAQUE, TRANSPARENT, or 0 on failure

Returns:

      typing.Any:Handle to a device contextReturn ValueReturns OPAQUE, TRANSPARENT, or 0 on failure


    """
    pass


def SetBkMode(hdc:'typing.Union[typing.Any, int]',BkMode:'typing.Any') -> 'typing.Any':
    """
    Sets the background mode for a device context

Args:

      hdc(typing.Union[typing.Any, int]):Handle to a device context
      BkMode(typing.Any):OPAQUE or TRANSPARENTReturn ValueReturns the previous mode, or 0 on failure

Returns:

      typing.Any:OPAQUE or TRANSPARENTReturn ValueReturns the previous mode, or 0 on failure


    """
    pass


def GetBkColor(hdc:'int') -> 'typing.Any':
    """
    Returns the background color for a device context

Args:

      hdc(int):Handle to a device contextReturn ValueReturns an RGB color value.  On error, returns CLR_INVALID.

Returns:

      typing.Any:Handle to a device contextReturn ValueReturns an RGB color value.  On error, returns CLR_INVALID.


    """
    pass


def SetBkColor(hdc:'typing.Union[typing.Any, int]',color:'typing.Any') -> 'typing.Any':
    """
    Sets the background color for a device context

Args:

      hdc(typing.Union[typing.Any, int]):Handle to a device context
      color(typing.Any):Return ValueReturns the previous color, or CLR_INVALID on failure

Returns:

      typing.Any:Return ValueReturns the previous color, or CLR_INVALID on failure


    """
    pass


def DrawEdge(hdc:'int',rc:'win32typing.PyRECT',edge:'typing.Any',Flags:'typing.Any') -> 'win32typing.PyRECT':
    """
    Draws edge(s) of a rectangle

Args:

      hdc(int):Handle to a device context
      rc(win32typing.PyRECT):Rectangle whose edge(s) will be drawn
      edge(typing.Any):Combination of win32con.BDR_* flags, or one of win32con.EDGE_* flags
      Flags(typing.Any):Combination of win32con.BF_* flagsReturn ValueBF_ADJUST flag causes input rectange to be shrunk by size of border.. Rectangle is always returned.

Returns:

      win32typing.PyRECT:Combination of win32con.BF_* flagsReturn ValueBF_ADJUST flag causes input rectange to be shrunk by size of border.. Rectangle is always returned.


    """
    pass


def FillRect(hDC:'int',rc:'win32typing.PyRECT',hbr:'win32typing.PyGdiHANDLE') -> 'None':
    """
    Fills a rectangular area with specified brush

Args:

      hDC(int):Handle to a device context
      rc(win32typing.PyRECT):Rectangle to be filled
      hbr(win32typing.PyGdiHANDLE):Handle to brush to be used to fill area

Returns:

      None

    """
    pass


def FillRgn(hdc:'int',hrgn:'win32typing.PyGdiHANDLE',hbr:'win32typing.PyGdiHANDLE') -> 'None':
    """
    Fills a region with specified brush

Args:

      hdc(int):Handle to the device context
      hrgn(win32typing.PyGdiHANDLE):Handle to the region
      hbr(win32typing.PyGdiHANDLE):Brush to be used

Returns:

      None

    """
    pass


def PaintRgn(hdc:'int',hrgn:'win32typing.PyGdiHANDLE') -> 'None':
    """
    Paints a region with current brush

Args:

      hdc(int):Handle to the device context
      hrgn(win32typing.PyGdiHANDLE):Handle to the region

Returns:

      None

    """
    pass


def FrameRgn(hdc:'int',hrgn:'typing.Any',hbr:'typing.Any',Width:'typing.Any',Height:'typing.Any') -> 'None':
    """
    Draws a frame around a region

Args:

      hdc(int):Handle to the device context
      hrgn(typing.Any):Handle to the region
      hbr(typing.Any):Handle to brush to be used
      Width(typing.Any):Frame width
      Height(typing.Any):Frame height

Returns:

      None

    """
    pass


def InvertRgn(hdc:'int',hrgn:'typing.Any') -> 'None':
    """
    Inverts the colors in a region

Args:

      hdc(int):Handle to the device context
      hrgn(typing.Any):Handle to the region

Returns:

      None

    """
    pass


def EqualRgn(SrcRgn1:'typing.Any',SrcRgn2:'typing.Any') -> 'typing.Any':
    """
    Determines if 2 regions are equal

Args:

      SrcRgn1(typing.Any):Handle to a region
      SrcRgn2(typing.Any):Handle to a region

Returns:

      typing.Any

    """
    pass


def PtInRegion(hrgn:'typing.Any',X:'typing.Any',Y:'typing.Any') -> 'typing.Any':
    """
    Determines if a region contains a point

Args:

      hrgn(typing.Any):Handle to a region
      X(typing.Any):X coord
      Y(typing.Any):Y coord

Returns:

      typing.Any

    """
    pass


def PtInRect(rect:'tuple[int, int, int, int]',point:'tuple[typing.Any, typing.Any]') -> 'typing.Any':
    """
    Determines if a rectangle contains a point

Args:

      rect(tuple[int, int, int, int]):The rect to check
      point(tuple[typing.Any, typing.Any]):The point

Returns:

      typing.Any

    """
    pass


def RectInRegion(hrgn:'typing.Any',rc:'win32typing.PyRECT') -> 'typing.Any':
    """
    Determines if a region and rectangle overlap at any point

Args:

      hrgn(typing.Any):Handle to a region
      rc(win32typing.PyRECT):Rectangle coordinates in logical units

Returns:

      typing.Any

    """
    pass


def SetRectRgn(hrgn:'typing.Any',LeftRect:'typing.Any',TopRect:'typing.Any',RightRect:'typing.Any',BottomRect:'typing.Any') -> 'None':
    """
    Makes an existing region rectangular

Args:

      hrgn(typing.Any):Handle to a region
      LeftRect(typing.Any):Left edge in logical units
      TopRect(typing.Any):Top edge in logical units
      RightRect(typing.Any):Right edge in logical units
      BottomRect(typing.Any):Bottom edge in logical units

Returns:

      None

    """
    pass


def CombineRgn(Dest:'typing.Any',Src1:'typing.Any',Src2:'typing.Any',CombineMode:'typing.Any') -> 'typing.Any':
    """
    Combines two regions

Args:

      Dest(typing.Any):Handle to existing region that will receive combined region
      Src1(typing.Any):Handle to first region
      Src2(typing.Any):Handle to second region
      CombineMode(typing.Any):One of RGN_AND,RGN_COPY,RGN_DIFF,RGN_OR,RGN_XORReturn ValueReturns the type of region created, one of NULLREGION, SIMPLEREGION, COMPLEXREGION

Returns:

      typing.Any:One of RGN_AND,RGN_COPY,RGN_DIFF,RGN_OR,RGN_XORReturn ValueReturns the type of region created, one of NULLREGION, SIMPLEREGION, COMPLEXREGION


    """
    pass


def DrawAnimatedRects(hwnd:'int',idAni:'typing.Any',minCoords:'win32typing.PyRECT',restCoords:'win32typing.PyRECT') -> 'None':
    """
    Animates a rectangle in the manner of minimizing, mazimizing, or opening

Args:

      hwnd(typing.Any):handle to clipping window
      idAni(typing.Any):type of animation, win32con.IDANI_*
      minCoords(win32typing.PyRECT):rectangle coordinates (minimized)
      restCoords(win32typing.PyRECT):rectangle coordinates (restored)

Returns:

      None

    """
    pass


def CreateSolidBrush(Color:'typing.Any') -> 'win32typing.PyGdiHANDLE':
    """
    Creates a solid brush of specified color

Args:

      Color(typing.Any):RGB color value.  See win32api::RGB.

Returns:

      win32typing.PyGdiHANDLE

    """
    pass


def CreatePatternBrush(hbmp:'win32typing.PyGdiHANDLE') -> 'win32typing.PyGdiHANDLE':
    """
    Creates a brush using a bitmap as a pattern

Args:

      hbmp(win32typing.PyGdiHANDLE):Handle to a bitmap

Returns:

      win32typing.PyGdiHANDLE

    """
    pass


def CreateHatchBrush(Style:'typing.Any',clrref:'typing.Any') -> 'win32typing.PyGdiHANDLE':
    """
    Creates a hatch brush with specified style and color

Args:

      Style(typing.Any):Hatch style, one of win32con.HS_* constants
      clrref(typing.Any):Rgb color value.  See win32api::RGB.

Returns:

      win32typing.PyGdiHANDLE

    """
    pass


def CreatePen(PenStyle:'typing.Any',Width:'typing.Any',Color:'typing.Any') -> 'win32typing.PyGdiHANDLE':
    """
    Create a GDI pen

Args:

      PenStyle(typing.Any):One of win32con.PS_* pen styles
      Width(typing.Any):Drawing width in logical units.  Use zero for single pixel.
      Color(typing.Any):RGB color value.  See win32api::RGB.

Returns:

      win32typing.PyGdiHANDLE

    """
    pass


def GetSysColor(Index:'typing.Any') -> 'typing.Any':
    """
    Returns the color of a window element

Args:

      Index(typing.Any):One of win32con.COLOR_* values

Returns:

      typing.Any

    """
    pass


def GetSysColorBrush(Index:'typing.Any') -> 'win32typing.PyGdiHANDLE':
    """
    Creates a handle to a system color brush

Args:

      Index(typing.Any):Index of a window element color (win32con.COLOR_*)

Returns:

      win32typing.PyGdiHANDLE

    """
    pass


def InvalidateRect(hWnd:'int',Rect:'win32typing.PyRECT',Erase:'typing.Any') -> 'None':
    """
    Invalidates a rectangular area of a window and adds it to the window's update region

Args:

      hWnd(int):Handle to the window
      Rect(win32typing.PyRECT):Client coordinates defining area to be redrawn.  Use None for entire client area.
      Erase(typing.Any):Indicates if background should be erased

Returns:

      None

    """
    pass


def FrameRect(hDC:'int',rc:'win32typing.PyRECT',hbr:'win32typing.PyGdiHANDLE') -> 'None':
    """
    Draws an outline around a rectangle

Args:

      hDC(int):Handle to a device context
      rc(win32typing.PyRECT):Rectangle around which to draw
      hbr(win32typing.PyGdiHANDLE):Handle to brush created using CreateHatchBrush, CreatePatternBrush, CreateSolidBrush, or GetStockObject

Returns:

      None

    """
    pass


def InvertRect(hDC:'int',rc:'win32typing.PyRECT') -> 'None':
    """
    Inverts the colors in a regtangular region

Args:

      hDC(int):Handle to a device context
      rc(win32typing.PyRECT):Coordinates of rectangle to invert

Returns:

      None

    """
    pass


def WindowFromDC(hDC:'int') -> 'int':
    """
    Finds the window associated with a device context

Args:

      hDC(int):Handle to a device contextReturn ValueReturns a handle to the window, or 0 if the DC is not associated with a window

Returns:

      int:Handle to a device contextReturn ValueReturns a handle to the window, or 0 if the DC is not associated with a window


    """
    pass


def GetUpdateRgn(hWnd:'int',hRgn:'win32typing.PyGdiHANDLE',Erase:'typing.Any') -> 'typing.Any':
    """
    Copies the update region of a window into an existing region

Args:

      hWnd(int):Handle to a window
      hRgn(win32typing.PyGdiHANDLE):Handle to an existing region to receive update area
      Erase(typing.Any):Indicates if window background is to be erasedReturn ValueReturns type of region, one of COMPLEXREGION, NULLREGION, or SIMPLEREGION

Returns:

      typing.Any:Indicates if window background is to be erasedReturn ValueReturns type of region, one of COMPLEXREGION, NULLREGION, or SIMPLEREGION


    """
    pass


def GetWindowRgn(hWnd:'int',hRgn:'win32typing.PyGdiHANDLE') -> 'typing.Any':
    """
    Copies the window region of a window into an existing region

Args:

      hWnd(int):Handle to a window
      hRgn(win32typing.PyGdiHANDLE):Handle to an existing region that receives window regionReturn ValueReturns type of region, one of COMPLEXREGION, NULLREGION, or SIMPLEREGION

Returns:

      typing.Any:Handle to an existing region that receives window regionReturn ValueReturns type of region, one of COMPLEXREGION, NULLREGION, or SIMPLEREGION


    """
    pass


def SetWindowRgn(hWnd:'int',hRgn:'win32typing.PyGdiHANDLE',Redraw:'typing.Any') -> 'None':
    """
    Sets the visible region of a window

Args:

      hWnd(int):Handle to a window
      hRgn(win32typing.PyGdiHANDLE):Handle to region to be set, can be None
      Redraw(typing.Any):Indicates if window should be completely redrawnCommentsOn success, the system assumes ownership of the region so you should call the handle's Detach() method to prevent it from being automatically closed.

Returns:

      None

    """
    pass


def GetWindowRgnBox(hWnd:'int') -> 'tuple[typing.Any, win32typing.PyRECT]':
    """
    Returns the bounding box for a window's region

Args:

      hWnd(int):Handle to a window that has a window region. (see win32gui::SetWindowRgn)CommentsOnly available in winxpguiReturn ValueReturns type of region and rectangle coordinates in device units

Returns:

      tuple[typing.Any, win32typing.PyRECT]:Handle to a window that has a window region. (see win32gui::SetWindowRgn)Comments

Only available in winxpgui
Return ValueReturns type of region and rectangle coordinates in device units


    """
    pass


def ValidateRgn(hWnd:'int',hRgn:'win32typing.PyGdiHANDLE') -> 'None':
    """
    Removes a region from a window's update region

Args:

      hWnd(int):Handle to the window
      hRgn(win32typing.PyGdiHANDLE):Region to be validated

Returns:

      None

    """
    pass


def InvalidateRgn(hWnd:'int',hRgn:'win32typing.PyGdiHANDLE',Erase:'typing.Any') -> 'None':
    """
    Adds a region to a window's update region

Args:

      hWnd(int):Handle to the window
      hRgn(win32typing.PyGdiHANDLE):Region to be redrawn
      Erase(typing.Any):Indidates if background should be erased

Returns:

      None

    """
    pass


def GetRgnBox(hrgn:'win32typing.PyGdiHANDLE') -> 'tuple[typing.Any, win32typing.PyRECT]':
    """
    Calculates the bounding box of a region

Args:

      hrgn(win32typing.PyGdiHANDLE):Handle to a regionReturn ValueReturns type of region (COMPLEXREGION, NULLREGION, or SIMPLEREGION) and rectangle in logical units

Returns:

      tuple[typing.Any, win32typing.PyRECT]:Handle to a regionReturn ValueReturns type of region (COMPLEXREGION, NULLREGION, or SIMPLEREGION) and rectangle in logical units


    """
    pass


def OffsetRgn(hrgn:'win32typing.PyGdiHANDLE',XOffset:'typing.Any',YOffset:'typing.Any') -> 'typing.Any':
    """
    Relocates a region

Args:

      hrgn(win32typing.PyGdiHANDLE):Handle to a region
      XOffset(typing.Any):Horizontal offset
      YOffset(typing.Any):Vertical offsetReturn ValueReturns type of region (COMPLEXREGION, NULLREGION, or SIMPLEREGION)

Returns:

      typing.Any:Vertical offsetReturn ValueReturns type of region (COMPLEXREGION, NULLREGION, or SIMPLEREGION)


    """
    pass


def Rectangle(hdc:'int',LeftRect:'typing.Any',TopRect:'typing.Any',RightRect:'typing.Any',BottomRect:'typing.Any') -> 'None':
    """
    Creates a solid rectangle using currently selected pen and brush

Args:

      hdc(int):Handle to device context
      LeftRect(typing.Any):Position of left edge of rectangle
      TopRect(typing.Any):Position of top edge of rectangle
      RightRect(typing.Any):Position of right edge of rectangle
      BottomRect(typing.Any):Position of bottom edge of rectangle

Returns:

      None

    """
    pass


def RoundRect(hdc:'int',LeftRect:'typing.Any',TopRect:'typing.Any',RightRect:'typing.Any',BottomRect:'typing.Any',Width:'typing.Any',Height:'typing.Any') -> 'None':
    """
    Draws a rectangle with elliptically rounded corners, filled using using current brush

Args:

      hdc(int):Handle to device context
      LeftRect(typing.Any):Position of left edge of rectangle
      TopRect(typing.Any):Position of top edge of rectangle
      RightRect(typing.Any):Position of right edge of rectangle
      BottomRect(typing.Any):Position of bottom edge of rectangle
      Width(typing.Any):Width of ellipse
      Height(typing.Any):Height of ellipse

Returns:

      None

    """
    pass


def BeginPaint() -> 'tuple[typing.Any, typing.Any]':
    """
    None

Args:



Returns:

      tuple[typing.Any, typing.Any]

    """
    pass


def EndPaint(hwnd:'int',ps:'typing.Any') -> 'None':
    """
    None

Args:

      hwnd(typing.Any):
      ps(typing.Any):As returned from win32gui::BeginPaint

Returns:

      None

    """
    pass


def BeginPath(hdc:'int') -> 'None':
    """
    Initializes a path in a DC

Args:

      hdc(int):Handle to a device context

Returns:

      None

    """
    pass


def EndPath(hdc:'int') -> 'None':
    """
    None

Args:

      hdc(int):Handle to a device context

Returns:

      None

    """
    pass


def AbortPath(hdc:'int') -> 'None':
    """
    None

Args:

      hdc(int):Handle to a device context

Returns:

      None

    """
    pass


def CloseFigure(hdc:'int') -> 'None':
    """
    Closes a section of a path by connecting the beginning pos with the current pos

Args:

      hdc(int):Handle to a device context that contains an open path. See win32gui::BeginPath.

Returns:

      None

    """
    pass


def FlattenPath(hdc:'int') -> 'None':
    """
    Flattens any curves in current path into a series of lines

Args:

      hdc(int):Handle to a device context that contains a closed path. See win32gui::EndPath.

Returns:

      None

    """
    pass


def FillPath(hdc:'int') -> 'None':
    """
    Fills a path with currently selected brush

Args:

      hdc(int):Handle to a device context that contains a finalized path. See win32gui::EndPath.CommentsAny open figures are closed and path is deselected from the DC.

Returns:

      None

    """
    pass


def WidenPath(hdc:'int') -> 'None':
    """
    Widens current path by amount it would increase by if drawn with currently selected pen

Args:

      hdc(int):Handle to a device context that contains a closed path. See win32gui::EndPath.

Returns:

      None

    """
    pass


def StrokePath(hdc:'int') -> 'None':
    """
    Draws current path with currently selected pen

Args:

      hdc(int):Handle to a device context that contains a closed path. See win32gui::EndPath.

Returns:

      None

    """
    pass


def StrokeAndFillPath(hdc:'int') -> 'None':
    """
    Combines operations of StrokePath and FillPath with no overlap

Args:

      hdc(int):Handle to a device context that contains a closed path. See win32gui::EndPath.

Returns:

      None

    """
    pass


def GetMiterLimit(hdc:'int') -> 'float':
    """
    Retrieves the limit of miter joins for a DC

Args:

      hdc(int):Handle to a device context

Returns:

      float

    """
    pass


def SetMiterLimit(hdc:'int',NewLimit:'float') -> 'float':
    """
    Set the limit of miter joins for a DC

Args:

      hdc(int):Handle to a device context
      NewLimit(float):New limit to be setReturn ValueReturns the previous limit

Returns:

      float:New limit to be setReturn ValueReturns the previous limit


    """
    pass


def PathToRegion(hdc:'int') -> 'win32typing.PyGdiHANDLE':
    """
    Converts a closed path in a DC to a region

Args:

      hdc(int):Handle to a device context that contains a closed path. See win32gui::EndPath.CommentsOn success, the path is deselected from the DC

Returns:

      win32typing.PyGdiHANDLE

    """
    pass


def GetPath(hdc:'int') -> 'tuple[typing.Any, typing.Any]':
    """
    Returns a sequence of points that describe the current path

Args:

      hdc(int):Handle to a device context containing a finalized path.  See win32gui::EndPathReturn ValueReturns a sequence of POINT tuples, and a sequence of ints designating each point's function (combination of win32con.PT_* values)

Returns:

      tuple[typing.Any, typing.Any]:Handle to a device context containing a finalized path.  See win32gui::EndPathReturn ValueReturns a sequence of POINT tuples, and a sequence of ints designating each point's function (combination of win32con.PT_* values)


    """
    pass


def CreateRoundRectRgn(LeftRect:'typing.Any',TopRect:'typing.Any',RightRect:'typing.Any',BottomRect:'typing.Any',WidthEllipse:'typing.Any',HeightEllipse:'typing.Any') -> 'typing.Any':
    """
    Create a rectangular region with elliptically rounded corners,

Args:

      LeftRect(typing.Any):Position of left edge of rectangle
      TopRect(typing.Any):Position of top edge of rectangle
      RightRect(typing.Any):Position of right edge of rectangle
      BottomRect(typing.Any):Position of bottom edge of rectangle
      WidthEllipse(typing.Any):Width of ellipse
      HeightEllipse(typing.Any):Height of ellipse

Returns:

      typing.Any

    """
    pass


def CreateRectRgnIndirect(rc:'win32typing.PyRECT') -> 'typing.Any':
    """
    Creates a rectangular region,

Args:

      rc(win32typing.PyRECT):Coordinates of rectangle

Returns:

      typing.Any

    """
    pass


def CreateEllipticRgnIndirect(rc:'win32typing.PyRECT') -> 'typing.Any':
    """
    Creates an ellipse region,

Args:

      rc(win32typing.PyRECT):Coordinates of bounding rectangle in logical units

Returns:

      typing.Any

    """
    pass


def CreateWindowEx(dwExStyle:'typing.Any',className:'typing.Union[str, typing.Any]',windowTitle:'str',style:'typing.Any',x:'typing.Any',y:'typing.Any',width:'typing.Any',height:'typing.Any',parent:'typing.Any',menu:'typing.Any',hinstance:'typing.Any',reserved:'typing.Any') -> 'typing.Any':
    """
    Creates a new window with Extended Style.

Args:

      dwExStyle(typing.Any):extended window style
      className(typing.Union[str, typing.Any]):
      windowTitle(str):
      style(typing.Any):The style for the window.
      x(typing.Any):
      y(typing.Any):
      width(typing.Any):
      height(typing.Any):
      parent(typing.Any):Handle to the parent window.
      menu(typing.Any):Handle to the menu to use for this window.
      hinstance(typing.Any):
      reserved(typing.Any):Must be None

Returns:

      typing.Any

    """
    pass


def GetParent(child:'typing.Any') -> 'typing.Any':
    """
    Retrieves a handle to the specified child window's parent window.

Args:

      child(typing.Any):handle to child window

Returns:

      typing.Any

    """
    pass


def SetParent(child:'typing.Any',child1:'typing.Any') -> 'typing.Any':
    """
    changes the parent window of the specified child window.

Args:

      child(typing.Any):handle to window whose parent is changing
      child1(typing.Any):handle to new parent window

Returns:

      typing.Any

    """
    pass


def GetCursorPos() -> 'tuple[typing.Any, typing.Any]':
    """
    retrieves the cursor's position, in screen coordinates.

Args:



Returns:

      tuple[typing.Any, typing.Any]

    """
    pass


def GetDesktopWindow() -> 'typing.Any':
    """
    returns the desktop window

Args:



Returns:

      typing.Any

    """
    pass


def GetWindow(hWnd:'typing.Any',uCmd:'typing.Any') -> 'typing.Any':
    """
    returns a window that has the specified relationship (Z order or owner) to the specified window.

Args:

      hWnd(typing.Any):handle to original window
      uCmd(typing.Any):relationship flag

Returns:

      typing.Any

    """
    pass


def GetWindowDC(hWnd:'typing.Any') -> 'typing.Any':
    """
    returns the device context (DC) for the entire window, including title bar, menus, and scroll bars.

Args:

      hWnd(typing.Any):handle of window

Returns:

      typing.Any

    """
    pass


def IsIconic(hWnd:'typing.Any') -> 'None':
    """
    determines whether the specified window is minimized (iconic).

Args:

      hWnd(typing.Any):handle to window

Returns:

      None

    """
    pass


def IsWindow(hWnd:'typing.Any') -> 'None':
    """
    determines whether the specified window handle identifies an existing window.

Args:

      hWnd(typing.Any):handle to window

Returns:

      None

    """
    pass


def IsChild(hWndParent:'typing.Any',hWnd:'typing.Any') -> 'None':
    """
    Tests whether a window is a child window or descendant window of a specified parent window

Args:

      hWndParent(typing.Any):handle to parent window
      hWnd(typing.Any):handle to window to test

Returns:

      None

    """
    pass


def ReleaseCapture() -> 'None':
    """
    Releases the moust capture for a window.

Args:



Returns:

      None

    """
    pass


def GetCapture() -> 'typing.Any':
    """
    Returns the window with the mouse capture.

Args:



Returns:

      typing.Any

    """
    pass


def SetCapture() -> 'None':
    """
    Captures the mouse for the specified window.

Args:



Returns:

      None

    """
    pass


def _TrackMouseEvent(tme:'win32typing.TRACKMOUSEEVENT') -> 'None':
    """
    Posts messages when the mouse pointer leaves a window or hovers over a window for a specified amount of time.

Args:

      tme(win32typing.TRACKMOUSEEVENT):

Returns:

      None

    """
    pass


def ReleaseDC(hWnd:'typing.Any',hDC:'typing.Any') -> 'typing.Any':
    """
    Releases a device context.

Args:

      hWnd(typing.Any):handle to window
      hDC(typing.Any):handle to device context

Returns:

      typing.Any

    """
    pass


def CreateCaret(hWnd:'typing.Any',hBitmap:'win32typing.PyGdiHANDLE',nWidth:'typing.Any',nHeight:'typing.Any') -> 'None':
    """
    Creates a new caret for a window

Args:

      hWnd(typing.Any):handle to owner window
      hBitmap(win32typing.PyGdiHANDLE):handle to bitmap for caret shape
      nWidth(typing.Any):caret width
      nHeight(typing.Any):caret height

Returns:

      None

    """
    pass


def DestroyCaret() -> 'None':
    """
    Destroys caret for current task

Args:



Returns:

      None

    """
    pass


def ScrollWindowEx(hWnd:'typing.Any',dx:'typing.Any',dy:'typing.Any',rcScroll:'win32typing.PyRECT',rcClip:'win32typing.PyRECT',hrgnUpdate:'typing.Any',flags:'typing.Any') -> 'tuple[typing.Any, win32typing.PyRECT]':
    """
    scrolls the content of the specified window's client area.

Args:

      hWnd(typing.Any):handle to window to scroll
      dx(typing.Any):Amount of horizontal scrolling, in device units
      dy(typing.Any):Amount of vertical scrolling, in device units
      rcScroll(win32typing.PyRECT):Scroll rectangle, can be None for entire client area
      rcClip(win32typing.PyRECT):Clipping rectangle, can be None
      hrgnUpdate(typing.Any):Handle to region which will be updated with area invalidated by scroll operation, can be None
      flags(typing.Any):Scrolling flags, combination of SW_ERASE,SW_INVALIDATE,SW_SCROLLCHILDREN,SW_SMOOTHSCROLL. If SW_SMOOTHSCROLL is specified, use upper 16 bits to specify time in milliseconds.Return ValueReturns the type of region invalidated by scrolling, and a rectangle defining the affected area.

Returns:

      tuple[typing.Any, win32typing.PyRECT]:Scrolling flags, combination of SW_ERASE,SW_INVALIDATE,SW_SCROLLCHILDREN,SW_SMOOTHSCROLL.

If SW_SMOOTHSCROLL is specified, use upper 16 bits to specify time in milliseconds.Return ValueReturns the type of region invalidated by scrolling, and a rectangle defining the affected area.


    """
    pass


def SetScrollInfo(hwnd:'int',nBar:'typing.Any',scollInfo:'win32typing.PySCROLLINFO',bRedraw:'typing.Any'=1) -> 'None':
    """
    Sets information about a scroll-bar

Args:

      hwnd(typing.Any):The handle to the window.
      nBar(typing.Any):Identifies the bar.
      scollInfo(win32typing.PySCROLLINFO):Scollbar info.
      bRedraw(typing.Any):Should the bar be redrawn?Return ValueReturns an int with the current position of the scroll box.

Returns:

      None:Should the bar be redrawn?
Return ValueReturns an int with the current position of the scroll box.


    """
    pass


def GetScrollInfo(hwnd:'int',nBar:'typing.Any',mask:'typing.Any') -> 'win32typing.PySCROLLINFO':
    """
    Returns information about a scroll bar

Args:

      hwnd(typing.Any):The handle to the window.
      nBar(typing.Any):The scroll bar to examine.  Can be one of win32con.SB_CTL, win32con.SB_VERT or win32con.SB_HORZ
      mask(typing.Any):The mask for attributes to retrieve.

Returns:

      win32typing.PySCROLLINFO

    """
    pass


def GetClassName(hwnd:'int') -> 'str':
    """
    Retrieves the name of the class to which the specified window belongs.

Args:

      hwnd(int):The handle to the window

Returns:

      str

    """
    pass


def WindowFromPoint(point:'tuple[typing.Any, typing.Any]') -> 'typing.Any':
    """
    Retrieves a handle to the window that contains the specified point.

Args:

      point(tuple[typing.Any, typing.Any]):The point.

Returns:

      typing.Any

    """
    pass


def ChildWindowFromPoint(hwndParent:'typing.Any',point:'tuple[typing.Any, typing.Any]') -> 'typing.Any':
    """
    Determines which, if any, of the child windows belonging to a parent window contains the specified point.

Args:

      hwndParent(typing.Any):The parent.
      point(tuple[typing.Any, typing.Any]):The point.

Returns:

      typing.Any

    """
    pass


def ChildWindowFromPoint(hwndParent:'typing.Any',point:'tuple[typing.Any, typing.Any]') -> 'typing.Any':
    """
    Determines which, if any, of the child windows belonging to a parent window contains the specified point.

Args:

      hwndParent(typing.Any):The parent.
      point(tuple[typing.Any, typing.Any]):The point.

Returns:

      typing.Any

    """
    pass


def ListView_SortItems(hwnd:'int',callback:'typing.Any',param:'typing.Any'=None) -> 'None':
    """
    Uses an application-defined comparison function to sort the items of a list view control.

Args:

      hwnd(typing.Any):The handle to the window
      callback(typing.Any):A callback object, taking 3 params.
      param(typing.Any):The third param to the callback function.

Returns:

      None

    """
    pass


def ListView_SortItemsEx(hwnd:'int',callback:'typing.Any',param:'typing.Any'=None) -> 'None':
    """
    Uses an application-defined comparison function to sort the items of a list view control.

Args:

      hwnd(typing.Any):The handle to the window
      callback(typing.Any):A callback object, taking 3 params.
      param(typing.Any):The third param to the callback function.

Returns:

      None

    """
    pass


def CreateDC(Driver:'str',Device:'str',InitData:'win32typing.PyDEVMODE') -> 'typing.Any':
    """
    Creates a device context for a printer or display device

Args:

      Driver(str):Name of display or print provider, usually DISPLAY or WINSPOOL
      Device(str):Name of specific device, eg printer name returned from GetDefaultPrinter
      InitData(win32typing.PyDEVMODE):A PyDEVMODE that specifies printing parameters, use None for printer defaults

Returns:

      typing.Any

    """
    pass


def GetSaveFileNameW(hwndOwner:'int'=None,hInstance:'int'=None,Filter:'typing.Any'=None,CustomFilter:'typing.Any'=None,FilterIndex:'typing.Any'=0,File:'typing.Any'=None,MaxFile:'typing.Any'=1024,InitialDir:'typing.Any'=None,Title:'typing.Any'=None,Flags:'typing.Any'=0,DefExt:'typing.Any'=None,TemplateName:'win32typing.PyResourceId'=None) -> 'tuple[typing.Any, typing.Any, typing.Any]':
    """
    Creates a dialog for user to specify location to save a file or files

Args:

      hwndOwner(int):Handle to window that owns dialog
      hInstance(int):Handle to module that contains dialog template
      Filter(typing.Any):Contains pairs of descriptions and filespecs separated by NULLS, with a final trailing NULL. Example: 'Python Scripts\\0*.py;*.pyw;*.pys\\0Text files\\0*.txt\\0'
      CustomFilter(typing.Any):Description to be used for filter that user selected or typed, can also contain a filespec as above
      FilterIndex(typing.Any):Specifies which of the filters is initially selected, use 0 for CustomFilter
      File(typing.Any):The file name initially displayed
      MaxFile(typing.Any):Number of characters to allocate for selected filename(s), override if large number of files expected
      InitialDir(typing.Any):The starting directory
      Title(typing.Any):The title of the dialog box
      Flags(typing.Any):Combination of win32con.OFN_* constants
      DefExt(typing.Any):The default extension to use
      TemplateName(win32typing.PyResourceId):Name or resource id of dialog box templateCommentsAccepts keyword arguments, all arguments optionalReturn ValueReturns a tuple of 3 values (PyUNICODE, PyUNICODE, int): First is the selected file(s). If multiple files are selected, returned string will be the directory followed by files names separated by nulls, otherwise it will be the full path.  In other words, if you use the OFN_ALLOWMULTISELECT flag you should split this value on \\0 characters and if the length of the result list is 1, it will be the full path, otherwise element 0 will be the directory and the rest of the elements will be filenames in this directory. Second is a unicode string containing user-selected filter, will be None if CustomFilter was not specified Third item contains flags pertaining to users input, such as OFN_READONLY and OFN_EXTENSIONDIFFERENT If the user presses cancel or an error occurs, a win32gui.error is raised.  If the user pressed cancel, the error number (ie, the winerror attribute of the exception) will be zero.

Returns:

      tuple[typing.Any, typing.Any, typing.Any]:Name or resource id of dialog box template
Comments

Accepts keyword arguments, all arguments optional
Return ValueReturns a tuple of 3 values (PyUNICODE, PyUNICODE, int):

First is the selected file(s). If multiple files are selected, returned string will be the directory followed by files names

separated by nulls, otherwise it will be the full path.  In other words, if you use the OFN_ALLOWMULTISELECT flag

you should split this value on \\0 characters and if the length of the result list is 1, it will be

the full path, otherwise element 0 will be the directory and the rest of the elements will be filenames in

this directory.

Second is a unicode string containing user-selected filter, will be None if CustomFilter was not specified

Third item contains flags pertaining to users input, such as OFN_READONLY and OFN_EXTENSIONDIFFERENT

If the user presses cancel or an error occurs, a

win32gui.error is raised.  If the user pressed cancel, the error number (ie, the winerror attribute of the exception) will be zero.


    """
    pass


def GetOpenFileNameW(hwndOwner:'int'=None,hInstance:'int'=None,Filter:'typing.Any'=None,CustomFilter:'typing.Any'=None,FilterIndex:'typing.Any'=0,File:'typing.Any'=None,MaxFile:'typing.Any'=1024,InitialDir:'typing.Any'=None,Title:'typing.Any'=None,Flags:'typing.Any'=0,DefExt:'typing.Any'=None,TemplateName:'win32typing.PyResourceId'=None) -> 'tuple[typing.Any, typing.Any, typing.Any]':
    """
    Creates a dialog to allow user to select file(s) to open

Args:

      hwndOwner(int):Handle to window that owns dialog
      hInstance(int):Handle to module that contains dialog template
      Filter(typing.Any):Contains pairs of descriptions and filespecs separated by NULLS, with a final trailing NULL. Example: 'Python Scripts\\0*.py;*.pyw;*.pys\\0Text files\\0*.txt\\0'
      CustomFilter(typing.Any):Description to be used for filter that user selected or typed, can also contain a filespec as above
      FilterIndex(typing.Any):Specifies which of the filters is initially selected, use 0 for CustomFilter
      File(typing.Any):The file name initially displayed
      MaxFile(typing.Any):Number of characters to allocate for selected filename, override if large number of files expected
      InitialDir(typing.Any):The starting directory
      Title(typing.Any):The title of the dialog box
      Flags(typing.Any):Combination of win32con.OFN_* constants
      DefExt(typing.Any):The default extension to use
      TemplateName(win32typing.PyResourceId):Name or resource id of dialog box templateCommentsAccepts keyword arguments, all arguments optional Input parameters and return values are identical to win32gui::GetSaveFileNameW

Returns:

      tuple[typing.Any, typing.Any, typing.Any]

    """
    pass


def SystemParametersInfo(Action:'typing.Any',Param:'typing.Any'=None,WinIni:'typing.Any'=0) -> 'None':
    """
    Queries or sets system-wide parameters. This function can also update the user profile while setting a parameter.

Args:

      Action(typing.Any):System parameter to query or set, one of the SPI_GET* or SPI_SET* constants
      Param(typing.Any):depends on action to be taken
      WinIni(typing.Any):Flags specifying whether change should be permanent, and if all windows should be notified of change. Combination of SPIF_UPDATEINIFILE, SPIF_SENDCHANGE, SPIF_SENDWININICHANGEActionInput/return typeSPI_GETDESKWALLPAPERReturns the path to the bmp used as wallpaperSPI_SETDESKWALLPAPERParam should be a string specifying a .bmp fileSPI_GETDROPSHADOWReturns a booleanSPI_GETFLATMENUReturns a booleanSPI_GETFONTSMOOTHINGReturns a booleanSPI_GETICONTITLEWRAPReturns a booleanSPI_GETSNAPTODEFBUTTONReturns a booleanSPI_GETBEEPReturns a booleanSPI_GETBLOCKSENDINPUTRESETSReturns a booleanSPI_GETMENUUNDERLINESReturns a booleanSPI_GETKEYBOARDCUESReturns a booleanSPI_GETKEYBOARDPREFReturns a booleanSPI_GETSCREENSAVEACTIVEReturns a booleanSPI_GETSCREENSAVERRUNNINGReturns a booleanSPI_GETMENUDROPALIGNMENTReturns a boolean (True indicates left aligned, False right aligned)SPI_GETMENUFADEReturns a booleanSPI_GETLOWPOWERACTIVEReturns a booleanSPI_GETPOWEROFFACTIVEReturns a booleanSPI_GETCOMBOBOXANIMATIONReturns a booleanSPI_GETCURSORSHADOWReturns a booleanSPI_GETGRADIENTCAPTIONSReturns a booleanSPI_GETHOTTRACKINGReturns a booleanSPI_GETLISTBOXSMOOTHSCROLLINGReturns a booleanSPI_GETMENUANIMATIONReturns a booleanSPI_GETSELECTIONFADEReturns a booleanSPI_GETTOOLTIPANIMATIONReturns a booleanSPI_GETTOOLTIPFADEReturns a boolean (TRUE=fade, False=slide)SPI_GETUIEFFECTSReturns a booleanSPI_GETACTIVEWINDOWTRACKINGReturns a booleanSPI_GETACTIVEWNDTRKZORDERReturns a booleanSPI_GETDRAGFULLWINDOWSReturns a booleanSPI_GETSHOWIMEUIReturns a booleanSPI_GETMOUSECLICKLOCKReturns a booleanSPI_GETMOUSESONARReturns a booleanSPI_GETMOUSEVANISHReturns a booleanSPI_GETSCREENREADERReturns a booleanSPI_GETSHOWSOUNDSReturns a booleanSPI_SETDROPSHADOWParam must be a booleanSPI_SETDROPSHADOWParam must be a booleanSPI_SETMENUUNDERLINESParam must be a booleanSPI_SETKEYBOARDCUESParam must be a booleanSPI_SETMENUFADEParam must be a booleanSPI_SETCOMBOBOXANIMATIONParam must be a booleanSPI_SETCURSORSHADOWParam must be a booleanSPI_SETGRADIENTCAPTIONSParam must be a booleanSPI_SETHOTTRACKINGParam must be a booleanSPI_SETLISTBOXSMOOTHSCROLLINGParam must be a booleanSPI_SETMENUANIMATIONParam must be a booleanSPI_SETSELECTIONFADEParam must be a booleanSPI_SETTOOLTIPANIMATIONParam must be a booleanSPI_SETTOOLTIPFADEParam must be a booleanSPI_SETUIEFFECTSParam must be a booleanSPI_SETACTIVEWINDOWTRACKINGParam must be a booleanSPI_SETACTIVEWNDTRKZORDERParam must be a booleanSPI_SETMOUSESONARParam must be a booleanSPI_SETMOUSEVANISHParam must be a booleanSPI_SETMOUSECLICKLOCKParam must be a booleanSPI_SETFONTSMOOTHINGParam should specify a booleanSPI_SETICONTITLEWRAPParam should specify a booleanSPI_SETSNAPTODEFBUTTONParam is a booleanSPI_SETBEEPParam is a booleanSPI_SETBLOCKSENDINPUTRESETSParam is a booleanSPI_SETKEYBOARDPREFParam is a booleanSPI_SETMOUSEBUTTONSWAPParam is a booleanSPI_SETSCREENSAVEACTIVEParam is a booleanSPI_SETMENUDROPALIGNMENTParam is a boolean (True=left aligned, False=right aligned)SPI_SETLOWPOWERACTIVEParam is a booleanSPI_SETPOWEROFFACTIVEParam is a booleanSPI_SETDRAGFULLWINDOWSParam is a booleanSPI_SETSHOWIMEUIParam is a booleanSPI_SETSCREENREADERParam is a booleanSPI_SETSHOWSOUNDSParam is a booleanSPI_SETMOUSETRAILSParam should be an int specifying the nbr of cursors in the trail (0 or 1 means disabled)SPI_SETWHEELSCROLLLINESParam is an int specifying nbr of linesSPI_SETKEYBOARDDELAYParam is an int in the range 0 - 3SPI_SETKEYBOARDSPEEDParam is an int in the range 0 - 31SPI_SETDOUBLECLICKTIMEParam is an int (in milliseconds),  Use win32gui::GetDoubleClickTime to retrieve the value.SPI_SETDOUBLECLKWIDTHParam is an int.  Use win32api.GetSystemMetrics(SM_CXDOUBLECLK) to retrieve the value.SPI_SETDOUBLECLKHEIGHTParam is an int,  Use win32api.GetSystemMetrics(SM_CYDOUBLECLK) to retrieve the value.SPI_SETMOUSEHOVERHEIGHTParam is an intSPI_SETMOUSEHOVERWIDTHParam is an intSPI_SETMOUSEHOVERTIMEParam is an intSPI_SETSCREENSAVETIMEOUTParam is an int specifying the timeout in secondsSPI_SETMENUSHOWDELAYParam is an int specifying the shortcut menu delay in millisecondsSPI_SETLOWPOWERTIMEOUTParam is an int (in seconds)SPI_SETPOWEROFFTIMEOUTParam is an int (in seconds)SPI_SETDRAGHEIGHTParam is an int. Use win32api.GetSystemMetrics(SM_CYDRAG) to retrieve the value.SPI_SETDRAGWIDTHParam is an int. Use win32api.GetSystemMetrics(SM_CXDRAG) to retrieve the value.SPI_SETBORDERParam is an intSPI_GETFONTSMOOTHINGCONTRASTReturns an intSPI_GETFONTSMOOTHINGTYPEReturns an intSPI_GETMOUSETRAILSReturns an int specifying the nbr of cursor images in the trail, 0 or 1 indicates disabledSPI_GETWHEELSCROLLLINESReturns the nbr of lines to scroll for the mouse wheelSPI_GETKEYBOARDDELAYReturns an intSPI_GETKEYBOARDSPEEDReturns an intSPI_GETMOUSESPEEDReturns an intSPI_GETMOUSEHOVERHEIGHTReturns an intSPI_GETMOUSEHOVERWIDTHReturns an intSPI_GETMOUSEHOVERTIMEReturns an intSPI_GETSCREENSAVETIMEOUTReturns an int (idle time in seconds)SPI_GETMENUSHOWDELAYReturns an int (shortcut delay in milliseconds)SPI_GETLOWPOWERTIMEOUTReturns an int (in seconds)SPI_GETPOWEROFFTIMEOUTReturns an int (in seconds)SPI_GETACTIVEWNDTRKTIMEOUTReturns an int (milliseconds)SPI_GETBORDERReturns an intSPI_GETCARETWIDTHReturns an intSPI_GETFOREGROUNDFLASHCOUNTReturns an intSPI_GETFOREGROUNDLOCKTIMEOUTReturns an intSPI_GETFOCUSBORDERHEIGHTReturns an intSPI_GETFOCUSBORDERWIDTHReturns an intSPI_GETMOUSECLICKLOCKTIMEReturns an int (in milliseconds)SPI_SETFONTSMOOTHINGCONTRASTParam should be an int in the range 1000 to 2200SPI_SETFONTSMOOTHINGTYPEParam should be one of the FE_FONTSMOOTHING* constantsSPI_SETMOUSESPEEDParam should be an int in the range 1 - 20SPI_SETACTIVEWNDTRKTIMEOUTParam is an int (in milliseconds)SPI_SETCARETWIDTHParam is an int (in pixels)SPI_SETFOREGROUNDFLASHCOUNTParam is an intSPI_SETFOREGROUNDLOCKTIMEOUTParam is an int (in milliseconds)SPI_SETFOCUSBORDERHEIGHTReturns an intSPI_SETFOCUSBORDERWIDTHReturns an intSPI_SETMOUSECLICKLOCKTIMEParam is an int (in milliseconds)SPI_GETICONTITLELOGFONTReturns a PyLOGFONT,SPI_SETICONTITLELOGFONTParam must be a PyLOGFONT,SPI_SETLANGTOGGLEParam is ignored. Sets the language toggle hotkey from registry key HKCU\\keyboard layout\\toggleSPI_SETICONSReloads the system icons.  Param is not usedSPI_GETMOUSEReturns a tuple of 3 ints containing the x and y mouse thresholds and the acceleration factor.SPI_SETMOUSEParam should be a sequence of 3 intsSPI_GETDEFAULTINPUTLANGReturns an int (locale id for default language)SPI_SETDEFAULTINPUTLANGParam is an int containing a locale idSPI_GETANIMATIONReturns an intSPI_SETANIMATIONParam is an intSPI_ICONHORIZONTALSPACINGFunctions as both a get and set operation.  If Param is None, functions as a get operation, otherwise Param is an int to be set as the new valueSPI_ICONVERTICALSPACINGFunctions as both a get and set operation.  If Param is None, functions as a get operation, otherwise Param is an int to be set as the new valueSPI_GETNONCLIENTMETRICSParam must be None.  The result is a dict.SPI_SETNONCLIENTMETRICSParam is a dict in the form of a NONCLIENTMETRICS struct, as returned by SPI_GETNONCLIENTMETRICS operationSPI_GETMINIMIZEDMETRICSReturns a dict representing a MINIMIZEDMETRICS struct.  Param is not used.SPI_SETMINIMIZEDMETRICSParam should be a MINIMIZEDMETRICS dict as returned by SPI_GETMINIMIZEDMETRICS actionSPI_SETDESKPATTERNUnsupported (obsolete)SPI_GETFASTTASKSWITCHUnsupported (obsolete)SPI_SETFASTTASKSWITCHUnsupported (obsolete)SPI_SETSCREENSAVERRUNNINGUnsupported (documented as internal use only)SPI_SCREENSAVERRUNNINGSame as SPI_SETSCREENSAVERRUNNINGSPI_SETPENWINDOWSUnsupported (only relevant for win95)SPI_GETWINDOWSEXTENSIONUnsupported (only relevant for win95)SPI_GETGRIDGRANULARITYUnsupported (obsolete)SPI_SETGRIDGRANULARITYUnsupported (obsolete)SPI_LANGDRIVERUnsupported (use is not documented)SPI_GETFONTSMOOTHINGORIENTATIONUnsupported (use is not documented)SPI_SETFONTSMOOTHINGORIENTATIONUnsupported (use is not documented)SPI_SETHANDHELDUnsupported (use is not documented)SPI_GETICONMETRICSNot implemented yetSPI_SETICONMETRICSNot implemented yetSPI_GETWORKAREANot implemented yetSPI_SETWORKAREANot implemented yetSPI_GETSERIALKEYSNot implemented yetSPI_SETSERIALKEYSNot implemented yetSPI_SETMOUSEKEYSNot implemented yetSPI_GETMOUSEKEYSNot implemented yetSPI_GETHIGHCONTRASTNot implemented yetSPI_SETHIGHCONTRASTNot implemented yetSPI_GETSOUNDSENTRYNot implemented yetSPI_SETSOUNDSENTRYNot implemented yetSPI_GETSTICKYKEYSNot implemented yetSPI_SETSTICKYKEYSNot implemented yetSPI_GETTOGGLEKEYSNot implemented yetSPI_SETTOGGLEKEYSNot implemented yetSPI_GETACCESSTIMEOUTNot implemented yetSPI_SETACCESSTIMEOUTNot implemented yetSPI_GETFILTERKEYSNot implemented yetSPI_SETFILTERKEYSNot implemented yetCommentsParam and WinIni are not used with any of the SPI_GET operations Boolean parameters can be any object that can be evaluated as True or FalseReturn ValueSPI_SET functions all return None on success.  Types returned by SPI_GET functions are dependent on the operation

Returns:

      None:Flags specifying whether change should be permanent, and if all windows should be notified of change. Combination of SPIF_UPDATEINIFILE, SPIF_SENDCHANGE, SPIF_SENDWININICHANGE



Action


Input/return type



SPI_GETDESKWALLPAPERReturns the path to the bmp used as wallpaper
SPI_SETDESKWALLPAPERParam should be a string specifying a .bmp file
SPI_GETDROPSHADOWReturns a boolean
SPI_GETFLATMENUReturns a boolean
SPI_GETFONTSMOOTHINGReturns a boolean
SPI_GETICONTITLEWRAPReturns a boolean
SPI_GETSNAPTODEFBUTTONReturns a boolean
SPI_GETBEEPReturns a boolean
SPI_GETBLOCKSENDINPUTRESETSReturns a boolean
SPI_GETMENUUNDERLINESReturns a boolean
SPI_GETKEYBOARDCUESReturns a boolean
SPI_GETKEYBOARDPREFReturns a boolean
SPI_GETSCREENSAVEACTIVEReturns a boolean
SPI_GETSCREENSAVERRUNNINGReturns a boolean
SPI_GETMENUDROPALIGNMENTReturns a boolean (True indicates left aligned, False right aligned)
SPI_GETMENUFADEReturns a boolean
SPI_GETLOWPOWERACTIVEReturns a boolean
SPI_GETPOWEROFFACTIVEReturns a boolean
SPI_GETCOMBOBOXANIMATIONReturns a boolean
SPI_GETCURSORSHADOWReturns a boolean
SPI_GETGRADIENTCAPTIONSReturns a boolean
SPI_GETHOTTRACKINGReturns a boolean
SPI_GETLISTBOXSMOOTHSCROLLINGReturns a boolean
SPI_GETMENUANIMATIONReturns a boolean
SPI_GETSELECTIONFADEReturns a boolean
SPI_GETTOOLTIPANIMATIONReturns a boolean
SPI_GETTOOLTIPFADEReturns a boolean (TRUE=fade, False=slide)
SPI_GETUIEFFECTSReturns a boolean
SPI_GETACTIVEWINDOWTRACKINGReturns a boolean
SPI_GETACTIVEWNDTRKZORDERReturns a boolean
SPI_GETDRAGFULLWINDOWSReturns a boolean
SPI_GETSHOWIMEUIReturns a boolean
SPI_GETMOUSECLICKLOCKReturns a boolean
SPI_GETMOUSESONARReturns a boolean
SPI_GETMOUSEVANISHReturns a boolean
SPI_GETSCREENREADERReturns a boolean
SPI_GETSHOWSOUNDSReturns a boolean
SPI_SETDROPSHADOWParam must be a boolean
SPI_SETDROPSHADOWParam must be a boolean
SPI_SETMENUUNDERLINESParam must be a boolean
SPI_SETKEYBOARDCUESParam must be a boolean
SPI_SETMENUFADEParam must be a boolean
SPI_SETCOMBOBOXANIMATIONParam must be a boolean
SPI_SETCURSORSHADOWParam must be a boolean
SPI_SETGRADIENTCAPTIONSParam must be a boolean
SPI_SETHOTTRACKINGParam must be a boolean
SPI_SETLISTBOXSMOOTHSCROLLINGParam must be a boolean
SPI_SETMENUANIMATIONParam must be a boolean
SPI_SETSELECTIONFADEParam must be a boolean
SPI_SETTOOLTIPANIMATIONParam must be a boolean
SPI_SETTOOLTIPFADEParam must be a boolean
SPI_SETUIEFFECTSParam must be a boolean
SPI_SETACTIVEWINDOWTRACKINGParam must be a boolean
SPI_SETACTIVEWNDTRKZORDERParam must be a boolean
SPI_SETMOUSESONARParam must be a boolean
SPI_SETMOUSEVANISHParam must be a boolean
SPI_SETMOUSECLICKLOCKParam must be a boolean
SPI_SETFONTSMOOTHINGParam should specify a boolean
SPI_SETICONTITLEWRAPParam should specify a boolean
SPI_SETSNAPTODEFBUTTONParam is a boolean
SPI_SETBEEPParam is a boolean
SPI_SETBLOCKSENDINPUTRESETSParam is a boolean
SPI_SETKEYBOARDPREFParam is a boolean
SPI_SETMOUSEBUTTONSWAPParam is a boolean
SPI_SETSCREENSAVEACTIVEParam is a boolean
SPI_SETMENUDROPALIGNMENTParam is a boolean (True=left aligned, False=right aligned)
SPI_SETLOWPOWERACTIVEParam is a boolean
SPI_SETPOWEROFFACTIVEParam is a boolean
SPI_SETDRAGFULLWINDOWSParam is a boolean
SPI_SETSHOWIMEUIParam is a boolean
SPI_SETSCREENREADERParam is a boolean
SPI_SETSHOWSOUNDSParam is a boolean
SPI_SETMOUSETRAILSParam should be an int specifying the nbr of cursors in the trail (0 or 1 means disabled)
SPI_SETWHEELSCROLLLINESParam is an int specifying nbr of lines
SPI_SETKEYBOARDDELAYParam is an int in the range 0 - 3
SPI_SETKEYBOARDSPEEDParam is an int in the range 0 - 31
SPI_SETDOUBLECLICKTIMEParam is an int (in milliseconds),  Use win32gui::GetDoubleClickTime to retrieve the value.
SPI_SETDOUBLECLKWIDTHParam is an int.  Use win32api.GetSystemMetrics(SM_CXDOUBLECLK) to retrieve the value.
SPI_SETDOUBLECLKHEIGHTParam is an int,  Use win32api.GetSystemMetrics(SM_CYDOUBLECLK) to retrieve the value.
SPI_SETMOUSEHOVERHEIGHTParam is an int
SPI_SETMOUSEHOVERWIDTHParam is an int
SPI_SETMOUSEHOVERTIMEParam is an int
SPI_SETSCREENSAVETIMEOUTParam is an int specifying the timeout in seconds
SPI_SETMENUSHOWDELAYParam is an int specifying the shortcut menu delay in milliseconds
SPI_SETLOWPOWERTIMEOUTParam is an int (in seconds)
SPI_SETPOWEROFFTIMEOUTParam is an int (in seconds)
SPI_SETDRAGHEIGHTParam is an int. Use win32api.GetSystemMetrics(SM_CYDRAG) to retrieve the value.
SPI_SETDRAGWIDTHParam is an int. Use win32api.GetSystemMetrics(SM_CXDRAG) to retrieve the value.
SPI_SETBORDERParam is an int
SPI_GETFONTSMOOTHINGCONTRASTReturns an int
SPI_GETFONTSMOOTHINGTYPEReturns an int
SPI_GETMOUSETRAILSReturns an int specifying the nbr of cursor images in the trail, 0 or 1 indicates disabled
SPI_GETWHEELSCROLLLINESReturns the nbr of lines to scroll for the mouse wheel
SPI_GETKEYBOARDDELAYReturns an int
SPI_GETKEYBOARDSPEEDReturns an int
SPI_GETMOUSESPEEDReturns an int
SPI_GETMOUSEHOVERHEIGHTReturns an int
SPI_GETMOUSEHOVERWIDTHReturns an int
SPI_GETMOUSEHOVERTIMEReturns an int
SPI_GETSCREENSAVETIMEOUTReturns an int (idle time in seconds)
SPI_GETMENUSHOWDELAYReturns an int (shortcut delay in milliseconds)
SPI_GETLOWPOWERTIMEOUTReturns an int (in seconds)
SPI_GETPOWEROFFTIMEOUTReturns an int (in seconds)
SPI_GETACTIVEWNDTRKTIMEOUTReturns an int (milliseconds)
SPI_GETBORDERReturns an int
SPI_GETCARETWIDTHReturns an int
SPI_GETFOREGROUNDFLASHCOUNTReturns an int
SPI_GETFOREGROUNDLOCKTIMEOUTReturns an int
SPI_GETFOCUSBORDERHEIGHTReturns an int
SPI_GETFOCUSBORDERWIDTHReturns an int
SPI_GETMOUSECLICKLOCKTIMEReturns an int (in milliseconds)
SPI_SETFONTSMOOTHINGCONTRASTParam should be an int in the range 1000 to 2200
SPI_SETFONTSMOOTHINGTYPEParam should be one of the FE_FONTSMOOTHING* constants
SPI_SETMOUSESPEEDParam should be an int in the range 1 - 20
SPI_SETACTIVEWNDTRKTIMEOUTParam is an int (in milliseconds)
SPI_SETCARETWIDTHParam is an int (in pixels)
SPI_SETFOREGROUNDFLASHCOUNTParam is an int
SPI_SETFOREGROUNDLOCKTIMEOUTParam is an int (in milliseconds)
SPI_SETFOCUSBORDERHEIGHTReturns an int
SPI_SETFOCUSBORDERWIDTHReturns an int
SPI_SETMOUSECLICKLOCKTIMEParam is an int (in milliseconds)
SPI_GETICONTITLELOGFONTReturns a PyLOGFONT,
SPI_SETICONTITLELOGFONTParam must be a PyLOGFONT,
SPI_SETLANGTOGGLEParam is ignored. Sets the language toggle hotkey from registry key HKCU\\keyboard layout\\toggle
SPI_SETICONSReloads the system icons.  Param is not used
SPI_GETMOUSEReturns a tuple of 3 ints containing the x and y mouse thresholds and the acceleration factor.
SPI_SETMOUSEParam should be a sequence of 3 ints
SPI_GETDEFAULTINPUTLANGReturns an int (locale id for default language)
SPI_SETDEFAULTINPUTLANGParam is an int containing a locale id
SPI_GETANIMATIONReturns an int
SPI_SETANIMATIONParam is an int
SPI_ICONHORIZONTALSPACINGFunctions as both a get and set operation.  If Param is None, functions as a get operation, otherwise Param is an int to be set as the new value
SPI_ICONVERTICALSPACINGFunctions as both a get and set operation.  If Param is None, functions as a get operation, otherwise Param is an int to be set as the new value
SPI_GETNONCLIENTMETRICSParam must be None.  The result is a dict.
SPI_SETNONCLIENTMETRICSParam is a dict in the form of a NONCLIENTMETRICS struct, as returned by SPI_GETNONCLIENTMETRICS operation
SPI_GETMINIMIZEDMETRICSReturns a dict representing a MINIMIZEDMETRICS struct.  Param is not used.
SPI_SETMINIMIZEDMETRICSParam should be a MINIMIZEDMETRICS dict as returned by SPI_GETMINIMIZEDMETRICS action
SPI_SETDESKPATTERNUnsupported (obsolete)
SPI_GETFASTTASKSWITCHUnsupported (obsolete)
SPI_SETFASTTASKSWITCHUnsupported (obsolete)
SPI_SETSCREENSAVERRUNNINGUnsupported (documented as internal use only)
SPI_SCREENSAVERRUNNINGSame as SPI_SETSCREENSAVERRUNNING
SPI_SETPENWINDOWSUnsupported (only relevant for win95)
SPI_GETWINDOWSEXTENSIONUnsupported (only relevant for win95)
SPI_GETGRIDGRANULARITYUnsupported (obsolete)
SPI_SETGRIDGRANULARITYUnsupported (obsolete)
SPI_LANGDRIVERUnsupported (use is not documented)
SPI_GETFONTSMOOTHINGORIENTATIONUnsupported (use is not documented)
SPI_SETFONTSMOOTHINGORIENTATIONUnsupported (use is not documented)
SPI_SETHANDHELDUnsupported (use is not documented)
SPI_GETICONMETRICSNot implemented yet
SPI_SETICONMETRICSNot implemented yet
SPI_GETWORKAREANot implemented yet
SPI_SETWORKAREANot implemented yet
SPI_GETSERIALKEYSNot implemented yet
SPI_SETSERIALKEYSNot implemented yet
SPI_SETMOUSEKEYSNot implemented yet
SPI_GETMOUSEKEYSNot implemented yet
SPI_GETHIGHCONTRASTNot implemented yet
SPI_SETHIGHCONTRASTNot implemented yet
SPI_GETSOUNDSENTRYNot implemented yet
SPI_SETSOUNDSENTRYNot implemented yet
SPI_GETSTICKYKEYSNot implemented yet
SPI_SETSTICKYKEYSNot implemented yet
SPI_GETTOGGLEKEYSNot implemented yet
SPI_SETTOGGLEKEYSNot implemented yet
SPI_GETACCESSTIMEOUTNot implemented yet
SPI_SETACCESSTIMEOUTNot implemented yet
SPI_GETFILTERKEYSNot implemented yet
SPI_SETFILTERKEYSNot implemented yet
Comments

Param and WinIni are not used with any of the SPI_GET operations

Boolean parameters can be any object that can be evaluated as True or False
Return ValueSPI_SET functions all return None on success.  Types returned by SPI_GET functions are dependent on the operation


    """
    pass


def SetLayeredWindowAttributes(hwnd:'int',Key:'typing.Any',Alpha:'typing.Any',Flags:'typing.Any') -> 'None':
    """
    Sets the opacity and transparency color key of a layered window.

Args:

      hwnd(int):handle to the layered window
      Key(typing.Any):Specifies the color key.  Use win32api::RGB to generate value.
      Alpha(typing.Any):Opacity, in the range 0-255
      Flags(typing.Any):Combination of win32con.LWA_* valuesCommentsThis function only exists on Win2k and laterAccepts keyword arguments

Returns:

      None

    """
    pass


def GetLayeredWindowAttributes(hwnd:'int') -> 'tuple[typing.Any, typing.Any, typing.Any]':
    """
    Retrieves the layering parameters of a window with the WS_EX_LAYERED extended style

Args:

      hwnd(int):Handle to a layered windowCommentsThis function only exists on WinXP and later.Accepts keyword arguments.Return ValueReturns a tuple of (color key, alpha, flags)

Returns:

      tuple[typing.Any, typing.Any, typing.Any]:Handle to a layered windowComments

This function only exists on WinXP and later.

Accepts keyword arguments.
Return ValueReturns a tuple of (color key, alpha, flags)


    """
    pass


def UpdateLayeredWindow(hwnd:'int',arg:'tuple[int, int, int, int]',hdcDst:'int'=None,ptDst:'tuple[typing.Any, typing.Any]'=None,size:'tuple[typing.Any, typing.Any]'=None,hdcSrc:'typing.Any'=None,ptSrc:'tuple[typing.Any, typing.Any]'=None,Key:'typing.Any'=0,Flags:'typing.Any'=0) -> 'None':
    """
    Updates the position, size, shape, content, and translucency of a layered window.

Args:

      hwnd(int):handle to layered window
      arg(tuple[int, int, int, int]):PyBLENDFUNCTION specifying alpha blending parameters
      hdcDst(int):handle to screen DC, can be None.  *Must* be None if hdcSrc is None
      ptDst(tuple[typing.Any, typing.Any]):New screen position, can be None.
      size(tuple[typing.Any, typing.Any]):New size of the layered window, can be None.  *Must* be None if hdcSrc is None.
      hdcSrc(typing.Any):handle to surface DC for the window, can be None
      ptSrc(tuple[typing.Any, typing.Any]):layer position, can be None.  *Must* be None if hdcSrc is None.
      Key(typing.Any):Color key, generate using win32api::RGB
      Flags(typing.Any):One of the win32con.ULW_* values.  Use 0 if hdcSrc is None.CommentsThis function is only available on Windows 2000 and laterAccepts keyword arguments.

Returns:

      None

    """
    pass


def AnimateWindow(hwnd:'int',Time:'typing.Any',Flags:'typing.Any') -> 'None':
    """
    Enables you to produce special effects when showing or hiding windows. There are three types of animation: roll, slide, and alpha-blended fade.

Args:

      hwnd(int):handle to window
      Time(typing.Any):Duration of animation in ms
      Flags(typing.Any):Animation type, combination of win32con.AW_* flagsCommentsThis function is available on Win2k and laterAccepts keyword args

Returns:

      None

    """
    pass


def CreateBrushIndirect(lb:'win32typing.PyLOGBRUSH') -> 'win32typing.PyGdiHANDLE':
    """
    Creates a GDI brush from a LOGBRUSH struct

Args:

      lb(win32typing.PyLOGBRUSH):Dict containing brush creation parameters

Returns:

      win32typing.PyGdiHANDLE

    """
    pass


def ExtCreatePen(PenStyle:'typing.Any',Width:'typing.Any',lb:'win32typing.PyLOGBRUSH',Style:'tuple[typing.Any, ...]'=None) -> 'int':
    """
    Creates a GDI pen object

Args:

      PenStyle(typing.Any):Combination of win32con.PS_*.  Must contain either PS_GEOMETRIC or PS_COSMETIC.
      Width(typing.Any):Width of pen in logical units.  Must be 1 for PS_COSMETIC.
      lb(win32typing.PyLOGBRUSH):Dict containing brush creation parameters
      Style(tuple[typing.Any, ...]):Sequence containing lengths of dashes and spaces  Used only with PS_USERSTYLE, otherwise must be None.

Returns:

      int

    """
    pass


def DrawTextW(hDC:'int',String:'str',Count:'typing.Any',Rect:'win32typing.PyRECT',Format:'typing.Any') -> 'tuple[typing.Any, win32typing.PyRECT]':
    """
    Draws Unicode text on a device context.

Args:

      hDC(int):Handle to a device context
      String(str):Text to be drawn
      Count(typing.Any):Number of characters to draw, use -1 for entire null terminated string
      Rect(win32typing.PyRECT):Rectangle in which to draw text
      Format(typing.Any):Formatting flags, combination of win32con.DT_* valuesCommentsAccepts keyword args.Return ValueReturns the height of the drawn text, and the rectangle coordinates

Returns:

      tuple[typing.Any, win32typing.PyRECT]:Formatting flags, combination of win32con.DT_* valuesComments

Accepts keyword args.
Return ValueReturns the height of the drawn text, and the rectangle coordinates


    """
    pass


def EnumPropsEx(hWnd:'int',EnumFunc:'typing.Any',Param:'typing.Any') -> 'None':
    """
    None

Args:

      hWnd(int):Handle to a window
      EnumFunc(typing.Any):Callback function
      Param(typing.Any):Arbitrary object to be passed to callback function

Returns:

      None

    """
    pass


def RegisterDeviceNotification(handle:'int',_filter:'typing.Any',flags:'typing.Any') -> 'win32typing.PyHDEVNOTIFY':
    """
    Registers the device or type of device for which a window will receive notifications.

Args:

      handle(int):The handle to a window or a service
      _filter(typing.Any):A buffer laid out like one of the DEV_BROADCAST_* structures, generally built by one of the win32gui_struct helpers.
      flags(typing.Any):Win32 API References

Returns:

      win32typing.PyHDEVNOTIFY

    """
    pass


def UnregisterDeviceNotification() -> 'None':
    """
    Unregisters a Device Notification handle.

It is generally not necessary to call this function manually, but in some cases,

handle values may be extracted via the struct module and need to be closed explicitly.

Args:



Returns:

      None

    """
    pass


def RegisterHotKey(hWnd:'int',_id:'typing.Any',Modifiers:'typing.Any',vk:'typing.Any') -> 'None':
    """
    Registers a hotkey for a window

Args:

      hWnd(int):Handle to window that will receive WM_HOTKEY messages
      _id(typing.Any):Unique id to be used for the hot key
      Modifiers(typing.Any):Control keys, combination of win32con.MOD_*
      vk(typing.Any):Virtual key codeWin32 API References

Returns:

      None

    """
    pass

CLR_NONE = ...
ILC_COLOR = ...
ILC_COLOR16 = ...
ILC_COLOR24 = ...
ILC_COLOR32 = ...
ILC_COLOR4 = ...
ILC_COLOR8 = ...
ILC_COLORDDB = ...
ILC_MASK = ...
ILD_BLEND = ...
ILD_BLEND25 = ...
ILD_BLEND50 = ...
ILD_FOCUS = ...
ILD_MASK = ...
ILD_NORMAL = ...
ILD_SELECTED = ...
ILD_TRANSPARENT = ...
IMAGE_BITMAP = ...
IMAGE_CURSOR = ...
IMAGE_ICON = ...
LR_CREATEDIBSECTION = ...
LR_DEFAULTCOLOR = ...
LR_DEFAULTSIZE = ...
LR_LOADFROMFILE = ...
LR_LOADMAP3DCOLORS = ...
LR_LOADTRANSPARENT = ...
LR_MONOCHROME = ...
LR_SHARED = ...
LR_VGACOLOR = ...
NIF_ICON = ...
NIF_INFO = ...
NIF_MESSAGE = ...
NIF_STATE = ...
NIF_TIP = ...
NIIF_ERROR = ...
NIIF_ICON_MASK = ...
NIIF_INFO = ...
NIIF_NONE = ...
NIIF_NOSOUND = ...
NIIF_WARNING = ...
NIM_ADD = ...
NIM_DELETE = ...
NIM_MODIFY = ...
NIM_SETFOCUS = ...
NIM_SETVERSION = ...
TPM_BOTTOMALIGN = ...
TPM_CENTERALIGN = ...
TPM_LEFTALIGN = ...
TPM_LEFTBUTTON = ...
TPM_NONOTIFY = ...
TPM_RETURNCMD = ...
TPM_RIGHTALIGN = ...
TPM_RIGHTBUTTON = ...
TPM_TOPALIGN = ...
TPM_VCENTERALIGN = ...
