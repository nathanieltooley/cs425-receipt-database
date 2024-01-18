import 'package:flutter/material.dart';
import 'dart:typed_data';

class ReceiptDetailPage extends StatelessWidget {
  final String title;
  final Uint8List imageData; // Assuming your receipt image data is of type Uint8List

  ReceiptDetailPage({required this.title, required this.imageData});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(title),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(title),
            Image.memory(imageData),
            // Add other details of the receipt as needed
          ],
        ),
      ),
    );
  }
}
