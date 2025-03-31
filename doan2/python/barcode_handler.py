from pyzbar.pyzbar import decode


def detect_barcode(img):
    """Phát hiện mã vạch trong hình ảnh và trả về dữ liệu mã vạch"""
    barcodes = decode(img)
    for barcode in barcodes:
        barcode_data = barcode.data.decode("utf-8")
        return barcode_data
    return None
