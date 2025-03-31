import sys
import datetime

import numpy as np
import config
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from google_sheet_helper import get_products_from_google_sheet, Product , update_product_quantity, hoadon

# Import WebSocketClient từ file mới
from my_websocket_client import WebSocketClient
from mqtt_handler import create_mqtt_client, send_message, remove_vietnamese_diacritics
from barcode_handler import detect_barcode
from image_handler import convert_qimage_to_cv2 

# Khởi tạo MQTT client
client = create_mqtt_client()












class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ESP32-CAM Viewer")
        self.setGeometry(100, 100, 320, 480)
        api_file = config.GOOGLE_SHEET_API_FILE
        sheet_key = config.GOOGLE_SHEET_KEY
        self.products = get_products_from_google_sheet(api_file, sheet_key)
        # Khung hiển thị hình ảnh
        self.label = QLabel(self)
        
        self.label.setAlignment(Qt.AlignCenter)

        # Bảng tính tiền
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["STT", "Auto-ID", "Tên sản phẩm", "Số lượng", "Đơn giá", "Thành tiền"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Nút Total
        self.total_button = QPushButton("Total")
        self.total_button.clicked.connect(self.calculate_total_price)

        # Nút Reset
        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset_for_next_customer)

      
        # Tập hợp để lưu các mã vạch đã quét
        self.scanned_barcodes = set()

        # Tổng tiền
        self.total_price = 0

        # Thiết lập layout
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.table)
        layout.addWidget(self.total_button)
        layout.addWidget(self.reset_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Khởi động WebSocket
        self.websocket_client = WebSocketClient(config.WEBSOCKET_URL)
        self.websocket_client.image_received.connect(self.update_image)
        self.websocket_client.start()

        # Theo dõi thay đổi trong bảng
        self.table.itemChanged.connect(self.update_row_total)
        client.loop_start()

    def reset_for_next_customer(self):
        """
        Reset các thông tin để chuẩn bị tính cho khách hàng tiếp theo.
        """
        self.clear_table()  # Xóa dữ liệu trong bảng
        self.total_price = 0  # Đặt lại tổng tiền về 0
        print("Đã reset, sẵn sàng tính tiền cho khách hàng tiếp theo.")


    
    def update_image(self, data):
        # Tạo QImage từ dữ liệu nhị phân, chuyển sang grayscale
        image = QImage.fromData(data).convertToFormat(QImage.Format_Grayscale8)
        pixmap = QPixmap.fromImage(image)
        self.label.setPixmap(pixmap)

        # Chuyển đổi QImage sang format OpenCV để xử lý mã vạch
        img =convert_qimage_to_cv2(image)
   
        # Kiểm tra và xử lý mã vạch
        barcode_data = detect_barcode(img)
        if barcode_data and barcode_data not in self.scanned_barcodes:
            print(f"Mã vạch: {barcode_data}")  # In ra mã vạch
            self.scanned_barcodes.add(barcode_data)  # Thêm mã vạch vào tập hợp đã quét
            self.add_to_table(barcode_data)
            self.capture_image()



    def clear_table(self):
        """
        Xóa tất cả các dòng trong bảng, bao gồm cả dòng "Tổng tiền".
        """
        self.table.setRowCount(0)  # Đặt số lượng dòng về 0
        self.scanned_barcodes.clear()  # Xóa danh sách mã vạch đã quét

    def add_to_table(self, barcode_data):
        product = self.products.get(barcode_data)
        if product:
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)

            self.table.setItem(row_position, 0, QTableWidgetItem(str(row_position + 1)))
            self.table.setItem(row_position, 1, QTableWidgetItem(product.barcode))
            self.table.setItem(row_position, 2, QTableWidgetItem(product.name))

            quantity_item = QTableWidgetItem("1")
            quantity_item.setFlags(quantity_item.flags() | Qt.ItemIsEditable)
            self.table.setItem(row_position, 3, quantity_item)

            self.table.setItem(row_position, 4, QTableWidgetItem(f"{product.price} VNĐ"))

            quantity = int(quantity_item.text())  # Chuyển đổi số lượng thành số nguyên
            total_price = product.price * quantity
            self.table.setItem(row_position, 5, QTableWidgetItem(f"{total_price} VNĐ"))



            # Gửi thông tin sản phẩm qua MQTT
            message = product.name +" "+ str(product.price)
            
            message = f"{product.name} {product.price}"
            mqtt_message = remove_vietnamese_diacritics(message)
            send_message(client, mqtt_message)

    def update_row_total(self, item):
        if item.column() == 3:  # Cột số lượng
            try:
                quantity = int(item.text())  # Lấy số lượng mới
                row = item.row()
                unit_price_item = self.table.item(row, 4)  # Lấy đơn giá
                total_price_item = self.table.item(row, 5)  # Lấy cột Thành tiền hiện tại

                if unit_price_item:
                    # Lấy giá trị đơn giá
                    unit_price = int(unit_price_item.text().replace(" VNĐ", ""))

                    # Tính giá trị mới cho Thành tiền
                    new_total_price = quantity * unit_price

                    # Cập nhật lại cột Thành tiền cho dòng hiện tại
                    if total_price_item is None:
                        total_price_item = QTableWidgetItem(f"{new_total_price} VNĐ")
                        self.table.setItem(row, 5, total_price_item)
                    else:
                        total_price_item.setText(f"{new_total_price} VNĐ")

            except ValueError:
                print("Số lượng không hợp lệ. Vui lòng nhập số nguyên.")





    def calculate_total_price(self):
        self.total_price = 0  # Reset tổng tiền

        # Lưu danh sách các dòng sản phẩm (tránh gọi lại item nhiều lần)
        rows_to_update = []
        
        # Tính tổng tiền cho tất cả các sản phẩm
        for row in range(self.table.rowCount()):
            item_product_name = self.table.item(row, 4)  # Tên sản phẩm ở cột 5 (Tên sản phẩm)
            
            # Bỏ qua dòng "Tổng tiền"
            if item_product_name and item_product_name.text() == "Tổng tiền":
                continue

            # Lấy giá trị thành tiền và cộng dồn
            item_total_price = self.table.item(row, 5)  # Thành tiền ở cột 5
            if item_total_price and item_total_price.text():
                price = int(item_total_price.text().replace(" VNĐ", ""))
                self.total_price += price
                rows_to_update.append(row)

        # Kiểm tra xem dòng "Tổng tiền" đã có chưa
        last_row = self.table.rowCount() - 1
        total_row_exists = False
        if last_row >= 0 and self.table.item(last_row, 4) and self.table.item(last_row, 4).text() == "Tổng tiền":
            total_row_exists = True

        # Cập nhật lại cột Thành tiền hoặc thêm dòng mới
        if total_row_exists:
            self.table.setItem(last_row, 5, QTableWidgetItem(f"{self.total_price} VNĐ"))
        else:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            self.table.setItem(row_position, 4, QTableWidgetItem("Tổng tiền"))
            self.table.setItem(row_position, 5, QTableWidgetItem(f"{self.total_price} VNĐ"))

        # Gửi thông điệp MQTT
        message = f"tổng tiền {self.total_price} vnd"
        mqtt_message = remove_vietnamese_diacritics(message)
        send_message(client, mqtt_message)

        # Cập nhật số lượng trong Google Sheet
        api_file = config.GOOGLE_SHEET_API_FILE
        sheet_key = config.GOOGLE_SHEET_KEY
        for row in rows_to_update:  # Chỉ cập nhật các dòng cần thiết
            barcode_item = self.table.item(row, 1)  # Mã vạch
            quantity_item = self.table.item(row, 3)  # Số lượng
            if barcode_item and quantity_item:
                barcode = barcode_item.text()
                quantity = int(quantity_item.text())
                update_product_quantity(api_file, sheet_key, barcode, quantity)
            # Ghi hóa đơn lên Google Sheet
        key_hoadon = config.sheet_hoadon
        try:
            for row in rows_to_update:
                product_name_item = self.table.item(row, 2)  # Tên sản phẩm
                quantity_item = self.table.item(row, 3)  # Số lượng
                price_item = self.table.item(row, 5)  # Thành tiền
                
                if product_name_item and quantity_item and price_item:
                    product_name = product_name_item.text()
                    quantity = int(quantity_item.text())
                    total_price = int(price_item.text().replace(" VNĐ", ""))
                    
                    # Gửi dữ liệu hóa đơn
                    hoadon(api_file, key_hoadon, product_name, quantity, total_price)
            
            print("Hóa đơn đã được gửi lên Google Sheet.")
        except Exception as e:
            print(f"Lỗi khi gửi hóa đơn lên Google Sheet: {e}")


    def capture_image(self):
        pixmap = self.label.pixmap()
        if pixmap:
            imestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"E:/doan2/doan2/images/img_{imestamp}.jpg"
            pixmap.save(filename)
            print(f"Hình ảnh đã được lưu: {filename}")


app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
