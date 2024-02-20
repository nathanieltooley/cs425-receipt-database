// api.dart
//import 'dart:convert';
import 'dart:typed_data';
import 'dart:convert';
import 'package:http/http.dart' as http;
//import 'package:connectivity/connectivity.dart';


class Api {
  static Future<void> uploadFile(String filePath) async {

    try {
      // need to change
      Uri uri = Uri.parse('http://127.0.0.1:5000/api/receipt/upload');
      var request = http.MultipartRequest('POST', uri);

      // Attach the file
      request.files.add(await http.MultipartFile.fromPath('file', filePath));
      
      // Send the request
      var response = await request.send();

      // Check the response
      if (response.statusCode == 200) {
        print('File uploaded successfully');
      } else {
        print('Failed to upload file. Status code: ${response.statusCode}');
      }
    } catch (e) {
        print('Error uploading file: $e');
    }
  }
//
  Future<Uint8List> fetchReceiptData(int fileKey) async {
    // need to change
    final response = await http.get(Uri.parse('http://127.0.0.1:5000/api/receipt/view/$fileKey'));

    if (response.statusCode == 200) {
      return response.bodyBytes;
    } else {
      throw Exception('Failed to load receipt');
    }
  }

  Future<List<String>> fetchTagsForReceipt(String receiptId) async {
    try {
      final response = await http.get(Uri.parse('http://127.0.0.1:5000/api/tag/'));

      if (response.statusCode == 200) {
        final List<dynamic> tagsJson = json.decode(response.body)['results'];
        final List<String> tags = [];

        for (final tag in tagsJson) {
          if (tag['id'] == receiptId) {
            tags.add(tag['name']);
          }
        }

        return tags;
      } else {
        throw Exception('Failed to fetch tags. Status code: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error fetching tags: $e');
    }
  }

  Future<List<Map<String, dynamic>>> fetchManyReceipts() async {
    try {
      // need to change
      final response = await http.get(Uri.parse('http://127.0.0.1:5000/api/receipt/fetch_many_keys'));
      if (response.statusCode == 200) {
        final List<dynamic> receiptsJson = json.decode(response.body)['results'];
        
        // Fetch details for each receipt and create a map
        final List<Map<String, dynamic>> receiptDataList = [];
        for (final receiptJson in receiptsJson) {
          int tempReceiptId = receiptJson['id'];
          final String receiptId = tempReceiptId.toString();
          final List<dynamic> tagsJson = receiptJson['metadata']['tags'];

          // Convert tag IDs to strings
          final List<String> tags = tagsJson.map((tag) => tag.toString()).toList();

          // Fetch image data for the receipt (assuming you have a method for this)
          final Uint8List imageData = await fetchReceiptData(tempReceiptId);

          // Create a map for the receipt data
          final Map<String, dynamic> receiptData = {
            'title': receiptId, 
            'imageData': imageData,
            'tags': tags,
            'imageUrl': 'placeholder_url', // placeholder
          };

          // Add the receiptData map to receiptDataList
          receiptDataList.add(receiptData);
        }

        return receiptDataList;
      } else {
        throw Exception('Failed to load many receipts. Status code: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error fetching many receipts: $e');
    }
  }

}