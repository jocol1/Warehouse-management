import 'package:flutter/services.dart';
import 'package:gsheets/gsheets.dart';
import '../models/product.dart';
import 'package:flutter/material.dart';
class ProductService {
  static const _spreadsheetId = '1sWueZ_zcA9D-lyU5Ejfb8I5phTQVV6w03lgJx1sdZ5k';
  late GSheets _gsheets;
  late Worksheet _sheet;

  Future<void> initialize(BuildContext context) async {
    final credentials = await DefaultAssetBundle.of(context)
        .loadString('assets/credentials.json');
    _gsheets = GSheets(credentials);
    final spreadsheet = await _gsheets.spreadsheet(_spreadsheetId);
    _sheet = spreadsheet.sheets.first;
  }

  Future<List<Product>> fetchProducts() async {
    final rows = await _sheet.values.allRows();
    return rows.skip(1).map((row) => Product.fromJson({
      'barcode': row[0],
      'product_name': row[1],
      'price': row[2],
      'quantity': row[3],
    })).toList();
  }

  Future<bool> updateProduct(Product product) async {
    final rows = await _sheet.values.allRows();
    final index = rows.indexWhere((row) => row[0] == product.barcode);

    if (index != -1) {
      await _sheet.values.insertRow(index + 1, product.toJson().values.toList());
      return true;
    }
    return false;
  }

  Future<bool> addProduct(Product product) async {
    return await _sheet.values.appendRow(product.toJson().values.toList());
  }
}