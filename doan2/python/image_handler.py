import datetime
import numpy as np
import cv2  # Thêm OpenCV để xử lý ảnh
from PyQt5.QtGui import QImage

def convert_qimage_to_cv2(qimage):
    """ Chuyển đổi QImage sang format OpenCV (giữ nguyên định dạng màu) """
    width, height = qimage.width(), qimage.height()
    ptr = qimage.bits()
    ptr.setsize(qimage.byteCount())
    
    # Kiểm tra định dạng và chuyển đổi
    if qimage.format() == QImage.Format_RGB32:
        arr = np.array(ptr).reshape((height, width, 4))  # 4 kênh (RGBA)
        arr = cv2.cvtColor(arr, cv2.COLOR_BGRA2BGR)  # Chuyển về BGR (3 kênh)
    elif qimage.format() == QImage.Format_RGB888:
        arr = np.array(ptr).reshape((height, width, 3))  # 3 kênh (RGB)
        arr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)  # Chuyển sang BGR để dùng OpenCV
    elif qimage.format() == QImage.Format_Grayscale8:
        arr = np.array(ptr).reshape((height, width))  # Grayscale (1 kênh)
    else:
        raise ValueError("Định dạng QImage không được hỗ trợ!")
    
    return arr


