import numpy
import cv2

import win32ui
import win32gui
import win32con

def capture_region(hwnd, rect):
    """
    Captures an image of the region for a window matching the given
    parameters of the bounding box

    @param hwnd: Handle to the window being captured
    @param rect: The coordinates of the region
    @return: The image of the region in the window in BGRA format
    """
    
    width = rect.right - rect.left
    height = rect.bottom - rect.top
   
    wDC = win32gui.GetWindowDC(hwnd)
    dcObj = win32ui.CreateDCFromHandle(wDC)
    cDC = dcObj.CreateCompatibleDC()
    bmp = win32ui.CreateBitmap()
    bmp.CreateCompatibleBitmap(dcObj, width, height)
    cDC.SelectObject(bmp)
    cDC.BitBlt((0, 0), (width, height), dcObj, (rect.left, rect.top), win32con.SRCCOPY)
   
    img = bmp.GetBitmapBits(True)
    img = numpy.frombuffer(img, dtype='uint8')
    img.shape = (height, width, 4)
 
    dcObj.DeleteDC()
    cDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, wDC)
    win32gui.DeleteObject(bmp.GetHandle())
    
    return img
