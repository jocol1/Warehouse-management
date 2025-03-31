import 'package:flutter/material.dart';
import 'package:barcode_scan2/barcode_scan2.dart';
import '../models/product.dart';
import '../services/product_service.dart';

class ProductListPage extends StatefulWidget {
  const ProductListPage({super.key});

  @override
  _ProductListPageState createState() => _ProductListPageState();
}

class _ProductListPageState extends State<ProductListPage> {
  final ProductService _productService = ProductService();
  List<Product> _allProducts = [];
  List<Product> _filteredProducts = [];
  final TextEditingController _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _initializeProductService();
  }

  Future<void> _initializeProductService() async {
    await _productService.initialize(context);
    _fetchProducts();
  }

  Future<void> _fetchProducts() async {
    final products = await _productService.fetchProducts();
    setState(() {
      _allProducts = products;
      _filteredProducts = _allProducts;
    });
  }

  void _filterProducts(String query) {
    setState(() {
      _filteredProducts = query.isEmpty
          ? _allProducts
          : _allProducts
              .where((product) => product.productName
                  .toLowerCase()
                  .contains(query.toLowerCase()))
              .toList();
    });
  }

  void _editProduct(Product product) {
    final nameController = TextEditingController(text: product.productName);
    final priceController =
        TextEditingController(text: product.price.toString());
    final quantityController =
        TextEditingController(text: product.quantity.toString());

    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text("Edit Product"),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: nameController,
                decoration: const InputDecoration(labelText: "Product Name"),
              ),
              TextField(
                controller: priceController,
                decoration: const InputDecoration(labelText: "Price"),
                keyboardType: TextInputType.number,
              ),
              TextField(
                controller: quantityController,
                decoration: const InputDecoration(labelText: "Quantity"),
                keyboardType: TextInputType.number,
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text("Cancel"),
            ),
            ElevatedButton(
              onPressed: () async {
                final updatedProduct = Product(
                  barcode: product.barcode,
                  productName: nameController.text,
                  price: int.parse(priceController.text),
                  quantity: int.parse(quantityController.text),
                );

                final success =
                    await _productService.updateProduct(updatedProduct);

                if (success) {
                  setState(() {
                    _fetchProducts();
                  });
                  Navigator.of(context).pop();
                } else {
                  ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text("Failed to update product")));
                }
              },
              child: const Text("Save"),
            ),
          ],
        );
      },
    );
  }

  void _addProduct() async {
    String? barcode;
    try {
      var result = await BarcodeScanner.scan();
      barcode = result.rawContent;
    } catch (e) {
      barcode = null;
    }

    if (barcode == null || barcode.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Barcode scan cancelled or failed")),
      );
      return;
    }

    Product? existingProduct;
    try {
      existingProduct = _allProducts.firstWhere(
        (product) => product.barcode == barcode,
      );
    } catch (e) {
      existingProduct = null;
    }

    if (existingProduct != null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
            content:
                Text("Barcode already exists: ${existingProduct.productName}")),
      );
      _editProduct(existingProduct);
      return;
    }

    final nameController = TextEditingController();
    final priceController = TextEditingController();
    final quantityController = TextEditingController();

    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text("Add New Product"),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text("Scanned Barcode: $barcode"),
              TextField(
                controller: nameController,
                decoration: const InputDecoration(labelText: "Product Name"),
              ),
              TextField(
                controller: priceController,
                decoration: const InputDecoration(labelText: "Price"),
                keyboardType: TextInputType.number,
              ),
              TextField(
                controller: quantityController,
                decoration: const InputDecoration(labelText: "Quantity"),
                keyboardType: TextInputType.number,
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text("Cancel"),
            ),
            ElevatedButton(
              onPressed: () async {
                final newProduct = Product(
                  barcode: barcode!,
                  productName: nameController.text,
                  price: int.parse(priceController.text),
                  quantity: int.parse(quantityController.text),
                );

                final success = await _productService.addProduct(newProduct);

                if (success) {
                  setState(() {
                    _fetchProducts();
                  });
                  Navigator.of(context).pop();
                } else {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text("Failed to add product")),
                  );
                }
              },
              child: const Text("Add"),
            ),
          ],
        );
      },
    );
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Product List")),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: TextField(
              controller: _searchController,
              decoration: InputDecoration(
                labelText: 'Search',
                hintText: 'Enter product name',
                prefixIcon: const Icon(Icons.search),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8.0),
                ),
              ),
              onChanged: _filterProducts,
            ),
          ),
          Expanded(
            child: _filteredProducts.isEmpty
                ? const Center(child: Text('No products found'))
                : ListView.builder(
                    itemCount: _filteredProducts.length,
                    itemBuilder: (context, index) {
                      final product = _filteredProducts[index];
                      return ListTile(
                        title: Text(product.productName),
                        subtitle: Text(
                            'Price: ${product.price} - Quantity: ${product.quantity}'),
                        trailing: IconButton(
                          icon: const Icon(Icons.edit),
                          onPressed: () => _editProduct(product),
                        ),
                      );
                    },
                  ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _addProduct,
        tooltip: 'Add Product',
        child: const Icon(Icons.add),
      ),
    );
  }
}