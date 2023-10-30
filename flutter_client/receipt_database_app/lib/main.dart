import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import '/api.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Receipt Database',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.lightBlue),
        useMaterial3: true,
      ),
      home: const MyHomePage(title: 'Receipt Database Homepage'),
    );
  }
}

class MyHomePage extends StatefulWidget {
  const MyHomePage({super.key, required this.title});

  final String title;

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {

  @override
  Widget build(BuildContext context) {

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

    return Scaffold(
      appBar: AppBar(
        title: Text(widget.title),
      ),

      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            ElevatedButton(
              onPressed: _pickAndUploadFile,
              child: Text('Upload Receipt'),
            ),
            SizedBox(height: 20),
            _filePath.isNotEmpty
              ? Text('Selected File: $_filePath')
              : Container(),
          ]
        )
      ),
    );
  }
}
