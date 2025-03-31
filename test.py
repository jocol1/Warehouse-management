import gspread

# Định nghĩa lớp Product
class Product:
    def __init__(self, barcode, name, price, quantity):
        """
        Khởi tạo một sản phẩm với các thuộc tính cơ bản.
        """
        self.barcode = barcode
        self.name = name
        self.price = float(price)  # Chuyển đổi giá về dạng số thực
        self.quantity = int(quantity)  # Chuyển đổi số lượng về dạng số nguyên

    def display_info(self):
        """
        Hiển thị thông tin sản phẩm.
        """
        return f"Barcode: {self.barcode}, Tên: {self.name}, Giá: {self.price} VND, Số lượng: {self.quantity}"


# Kết nối tới Google Sheet
def get_products_from_sheet(api_file, sheet_key):
    """
    Lấy dữ liệu từ Google Sheet và trả về một danh sách các đối tượng Product.
    """
    # Kết nối tới Google Sheets
    gs = gspread.service_account(api_file)
    sheet = gs.open_by_key(sheet_key)
    worksheet = sheet.sheet1

    # Lấy toàn bộ dữ liệu từ trang tính
    rows = worksheet.get_all_values()

    # Bỏ qua dòng tiêu đề và tạo danh sách Product
    products = []
    for row in rows[1:]:  # Bỏ qua dòng đầu tiên
        barcode, name, price, quantity = row
        products.append(Product(barcode, name, price, quantity))

    return products


# Sử dụng hàm
if __name__ == "__main__":
    # Thông tin file API và Google Sheet
    API_FILE = "api.json"
    SHEET_KEY = "1sWueZ_zcA9D-lyU5Ejfb8I5phTQVV6w03lgJx1sdZ5k"

    # Lấy danh sách sản phẩm
    products = get_products_from_sheet(API_FILE, SHEET_KEY)

    # Hiển thị thông tin từng sản phẩm
    for product in products:
        print(product.display_info())
    
