// api.dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:connectivity/connectivity.dart';


class Api {
  static Future<void> uploadFile(String filePath) async {

    try {
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
}