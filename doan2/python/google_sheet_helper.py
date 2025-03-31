import gspread
from dataclasses import dataclass
import datetime
@dataclass
class Product:
    barcode: str
    name: str
    price: int
  

def get_products_from_google_sheet(api_file, sheet_key):
    """
    Lấy danh sách sản phẩm từ Google Sheet.
    
    Parameters:
        api_file (str): Đường dẫn tới file API Google Service Account.
        sheet_key (str): Key của Google Sheet.

    Returns:
        dict: Danh sách sản phẩm với mã vạch làm key và đối tượng Product làm giá trị.
    """
    products = {}
    try:
        # Kết nối Google Sheets
        gs = gspread.service_account(api_file)
        sheet = gs.open_by_key(sheet_key)
        worksheet = sheet.sheet1
        rows = worksheet.get_all_values()
        print("ket noi thnh cong")
        # Bỏ qua dòng tiêu đề và thêm sản phẩm vào danh sách
        for row in rows[1:]:
            barcode, name, price, _ = row  # Bỏ qua cột quantity
            products[barcode] = Product(barcode, name, int(price))

    except Exception as e:
        print(f"Không thể lấy dữ liệu từ Google Sheet: {e}")

    return products
def update_product_quantity(api_file, sheet_key, barcode, sold_quantity):
    """
    Cập nhật số lượng sản phẩm trong Google Sheet sau khi bán hàng.
    
    Parameters:
        api_file (str): Đường dẫn tới file API Google Service Account.
        sheet_key (str): Key của Google Sheet.
        barcode (str): Mã vạch của sản phẩm.
        sold_quantity (int): Số lượng sản phẩm đã bán.
    """
    try:
        # Kết nối Google Sheets
        gs = gspread.service_account(api_file)
        sheet = gs.open_by_key(sheet_key)
        worksheet = sheet.sheet1
        rows = worksheet.get_all_values()
        # Tìm hàng có mã vạch cần cập nhật
        for index, row in enumerate(rows):
            if row[0] == barcode:  # Giả sử cột 0 chứa mã vạch
                initial_quantity = int(row[3])  # Giả sử cột 3 (index 3) chứa số lượng ban đầu
                new_quantity = initial_quantity - sold_quantity  # Tính toán số lượng còn lại
                if new_quantity < 0:
                    print(f"Lỗi: Số lượng bán vượt quá số lượng tồn kho ({initial_quantity}).")
                    return
                
                # Cập nhật Google Sheet
                worksheet.update_cell(index + 1, 4, new_quantity)  # Giả sử cột 4 chứa số lượng
                print(f"Đã cập nhật số lượng sản phẩm: {barcode}. Số lượng mới: {new_quantity}")
                break
    except Exception as e:
        print(f"Lỗi khi cập nhật Google Sheet: {e}")

def hoadon(api_file, sheet_key, product, quantity, price):
    """
    Ghi thông tin hóa đơn vào Google Sheet.
    
    Parameters:
        api_file (str): Đường dẫn tới file API Google Service Account.
        sheet_key (str): Key của Google Sheet.
        product (str): Tên sản phẩm.
        quantity (int): Số lượng sản phẩm đã bán.
        price (int): Thành tiền.
    """
    try:
        # Kết nối Google Sheets
        gs = gspread.service_account(api_file)
        sheet = gs.open_by_key(sheet_key)
        sheet_hoadon = sheet.worksheet("Hóa đơn")  # Worksheet "Hóa đơn"
        
        # Thêm dòng mới vào worksheet
        new_row = [datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), product, quantity, price]
        sheet_hoadon.append_row(new_row)
        
        print(f"Đã ghi hóa đơn: {product} - SL: {quantity} - Giá: {price}")
    except Exception as e:
        print(f"Lỗi khi ghi hóa đơn vào Google Sheet: {e}")
