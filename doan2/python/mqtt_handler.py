import paho.mqtt.client as mqtt
import uuid
import unicodedata
import config
# Hàm xử lý khi kết nối tới broker
def on_connect(client, userdata, flags, rc, properties=None):
    print(f"Connected with result code {rc}")
    # Đăng ký nhận tin nhắn từ topic
    client.subscribe("esp32/client", qos=1)
    print("Subscribed to topic: esp32/client")

# Hàm gửi tin nhắn
def send_message(client, message, topic="esp32/client"):
    client.publish(topic, payload=message, qos=1)
    print(f"Sent message: {message} to topic: {topic}")

# Hàm loại bỏ dấu tiếng Việt
def remove_vietnamese_diacritics(text):
    normalized = unicodedata.normalize('NFD', text)
    return ''.join(char for char in normalized if not unicodedata.combining(char))

# Tạo hàm khởi tạo MQTT client
def create_mqtt_client():
    # Tạo client_id duy nhất
    client_id = f"esp32_{uuid.uuid4()}"

    # Cấu hình client
    client = mqtt.Client(client_id=client_id, protocol=mqtt.MQTTv5)
    client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS)
    client.username_pw_set(config.MQTT_USERNAME, config.MQTT_PASSWORD)

    # Đăng ký các callback
    client.on_connect = on_connect

    # Kết nối đến HiveMQ Cloud
    client.connect(config.MQTT_BROKER, 8883)
    return client
