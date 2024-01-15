import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import '/components/api.dart';


class DatabasePage extends StatefulWidget {
  const DatabasePage({super.key, required this.title});

  final String title;

  @override
  State<DatabasePage> createState() => _DatabasePageState();
}

class _DatabasePageState extends State<DatabasePage> {
  String _filePath = '';

  // Allows user to pick a file to upload
  void _pickAndUploadFile() async {
    String? filePath = await FilePicker.platform.pickFiles().then((result) {
      if (result != null) {
        return result.files.single.path;
      } else {
        return null;
      }
    });

    if (filePath != null) {
      setState(() {
        _filePath = filePath;
      });

      try {
        await Api.uploadFile(_filePath);
        print('File uploaded successfully');
      } catch (e) {
        print('Error uploading file: $e');
      }
    } else {
      print('No file selected');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.title),
        backgroundColor: Colors.blue, // Added for consistency
         actions: [
          IconButton(
            icon: const Icon(Icons.search),
            onPressed: () {
              // Add search functionality here
              print('Search button pressed');
            },
          ),
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () {
              // Add settings functionality here
              print('Settings button pressed');
            },
          ),
        ],
      ),
      body: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: <Widget>[
          ElevatedButton(
            onPressed: _pickAndUploadFile,
            child: Text('Upload Receipt'),
          ),
          SizedBox(height: 20),
          _filePath.isNotEmpty
              ? Text('File Uploaded Successfully')
              : Container(),
        ],
      ),
    );
  }
}