// api.dart
//import 'dart:convert';
import 'dart:typed_data';
import 'dart:convert';
import 'package:http/http.dart' as http;
//import 'package:connectivity/connectivity.dart';


class Api {
  static Future<void> uploadFile(String filePath, fileName, fileTag) async {

    try {
      Uri uri = Uri.parse('http://127.0.0.1:5000/api/receipt/');
      var request = http.MultipartRequest('POST', uri);

      // Attach the file
      request.files.add(await http.MultipartFile.fromPath('file', filePath));

      // Attach file name user sets
      request.files.add(await http.MultipartFile.fromString('name', fileName));

      // Attach tag- if left empty, do not attach tag
      request.files.add(await http.MultipartFile.fromString('tag', fileTag));
      
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
    final response = await http.get(Uri.parse('http://127.0.0.1:5000/api/receipt/$fileKey/image'));

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
        final List<dynamic> tagsJson = json.decode(response.body);
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

  Future<String> fetchTagName(int tagId) async {
    try {
      final response = await http.get(Uri.parse('http://127.0.0.1:5000/api/tag/$tagId'));
      if (response.statusCode == 200) {
        final Map<String, dynamic> tagJson = json.decode(response.body);
        final String tagName = tagJson['name'];
        return tagName;
      } else if (response.statusCode == 404) {
        throw Exception('Tag not found');
      } else {
        throw Exception('Failed to fetch tag. Status code: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error fetching tag: $e');
    }
  }

  Future<List<Map<String, dynamic>>> fetchManyReceipts() async {
    try {
      final response = await http.get(Uri.parse('http://127.0.0.1:5000/api/receipt/'));
      if (response.statusCode == 200) {
        final List<dynamic> receiptsJson = json.decode(response.body);
        
        // Fetch details for each receipt and create a map
        final List<Map<String, dynamic>> receiptDataList = [];
        for (final receiptJson in receiptsJson) {
          final int tempReceiptId = receiptJson['id'];
          final String receiptId = receiptJson['name'];
          final List<dynamic> tagIds = receiptJson['tags'];

          // Fetch tag names associated with tag IDs
          final List<Future<String>> tagFutures = tagIds.map((tagId) => fetchTagName(tagId)).toList();
          final List<String> tags = await Future.wait(tagFutures);

           print('Tag names for receipt $receiptId: $tags');

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