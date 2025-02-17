class Product {
  final String barcode;
  final String productName;
  final int price;
  final int quantity;

  Product({
    required this.barcode,
    required this.productName,
    required this.price,
    required this.quantity,
  });

  factory Product.fromJson(Map<String, String> json) {
    return Product(
      barcode: json['barcode']!,
      productName: json['product_name']!,
      price: int.parse(json['price']!),
      quantity: int.parse(json['quantity']!),
    );
  }

  Map<String, String> toJson() => {
        'barcode': barcode,
        'product_name': productName,
        'price': price.toString(),
        'quantity': quantity.toString(),
      };
}