import 'package:flutter/material.dart';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:file_picker/file_picker.dart';
import '/components/api.dart';
import '/pages/image_cache.dart' as MyImageCache; // Updated import statement
import '/pages/view_receipt.dart';
import 'dart:typed_data';

class MyListView extends StatefulWidget {
  const MyListView({super.key});

  @override
  _MyListViewState createState() => _MyListViewState();
}

class _MyListViewState extends State<MyListView> {
  List<Map<String, dynamic>> receiptDataList = [];
  final MyImageCache.ImageCache imageCache = MyImageCache.ImageCache();

  @override
  void initState() {
    super.initState();
    // Populate the receiptDataList with data from the API or cache
    fetchAndSetReceiptData();
  }


  Future<void> fetchAndSetReceiptData() async {
  try {
    // Make the API call using fetchManyReceipts
    final apiService = Api();
    final List<Map<String, dynamic>> receipts = await apiService.fetchManyReceipts();

    // Iterate through the receipts and add them to receiptDataList
    for (final receipt in receipts) {
      // Store in cache using the ImageCache instance
      await imageCache.storeBytesInCache(receipt['imageData'], receipt['title']);
    }

    // Set the state to update the UI with the new data
    setState(() {
      receiptDataList.addAll(receipts);
    });
  } catch (e) {
    // Handle errors
    print('Error fetching and setting receipt data: $e');
  }
}


  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      itemCount: receiptDataList.length,
      itemBuilder: (context, index) {
        final title = receiptDataList[index]['title'] as String;
        final imageData = receiptDataList[index]['imageData'] as Uint8List;

        return Card(
          elevation: 5,
          margin: const EdgeInsets.all(8),
          child: ListTile(
            title: Text(title),
            onTap: () {
              // Navigate to ReceiptDetailPage when ListTile is tapped
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => ReceiptDetailPage(
                    title: title,
                    imageData: imageData,
                  ),
                ),
              );
            },
            leading: CachedNetworkImage(
              imageUrl: receiptDataList[index]['imageUrl'] as String,
              placeholder: (context, url) => CircularProgressIndicator(),
              errorWidget: (context, url, error) => Icon(Icons.error),
            ),
          ),
        );
      },
    );
  }
}

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
        backgroundColor: Colors.blue,
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
        mainAxisAlignment: MainAxisAlignment.start,
        children: <Widget>[
          ElevatedButton(
            onPressed: _pickAndUploadFile,
            child: Text('Upload Receipt'),
          ),
          SizedBox(height: 20),
          _filePath.isNotEmpty
              ? Text('File Uploaded Successfully')
              : Container(),
          Expanded(
            child: MyListView(),
          ),
        ],
      ),
    );
  }
}
