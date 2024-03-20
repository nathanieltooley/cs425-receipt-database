import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import '/components/api.dart';
import '/pages/image_cache.dart' as MyImageCache; // Updated import statement
import '/pages/view_receipt.dart';
import 'dart:typed_data';
import 'package:image/image.dart' as img;

class MyListView extends StatefulWidget {
  const MyListView({super.key});

  @override
  _MyListViewState createState() => _MyListViewState();
}



class _MyListViewState extends State<MyListView> {
  List<Map<String, dynamic>> receiptDataList = [];
  List<Map<String, dynamic>> filteredReceipts = [];
  final MyImageCache.ImageCache imageCache = MyImageCache.ImageCache();
  final TextEditingController _searchController = TextEditingController();

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
      final List<Map<String, dynamic>> receipts =
          await apiService.fetchManyReceipts();

      // Iterate through the receipts and add them to receiptDataList
      for (final receipt in receipts) {
        // Store in cache using the ImageCache instance
        await imageCache.storeBytesInCache(
            receipt['imageData'], receipt['title']);
      }

      // Set the state to update the UI with the new data
      setState(() {
        receiptDataList.addAll(receipts);
        filteredReceipts.addAll(receipts);
      });
    } catch (e) {
      // Handle errors
      print('Error fetching and setting receipt data: $e');
    }
  }

 void _filterReceipts(String query) {
    setState(() {
      filteredReceipts = receiptDataList.where((receipt) {
        final String title = receipt['title'].toLowerCase();
        final List<String> tags = receipt['tags'];

        // Check if the title contains the query
        final bool titleMatches = title.contains(query.toLowerCase());

        // Check if any tag contains the query
        final bool tagsMatch = tags.any((tag) => tag.toLowerCase().contains(query.toLowerCase()));

        // Return true if either title or tags match the query
        return titleMatches || tagsMatch;
      }).toList();
      filteredReceipts = receiptDataList
          .where((receipt) =>
              receipt['title'].toLowerCase().contains(query.toLowerCase()))
          .toList();
    });
  }

Future<Uint8List?> generateThumbnail(Uint8List? imageData) async {
  try {
    if (imageData == null || imageData.isEmpty) {
      print('Image data is empty or null.');
      return null;
    }

    img.Image? image = img.decodeImage(imageData);
    if (image == null) {
      print('Error decoding image.');
      return null;
    }

    img.Image thumbnail = img.copyResize(image, width: 100, height: 100);
    return Uint8List.fromList(img.encodePng(thumbnail));
  } catch (e) {
    print('Error generating thumbnail: $e');
    return null;
  }
}


  Future<void> _confirmAndDeleteReceipt(int id) async {
    // Show confirmation dialog before deleting the receipt
    bool confirmDelete = await showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: Text('Delete Receipt'),
          content: Text('Are you sure you want to delete this receipt?'),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.of(context).pop(false); // Cancel deletion
              },
              child: Text('Cancel'),
            ),
            TextButton(
              onPressed: () {
                Navigator.of(context).pop(true); // Confirm deletion
              },
              child: Text('Delete'),
            ),
          ],
        );
      },
    );

    // If user confirms deletion, call deleteReceipt function
    if (confirmDelete == true) {
      Api apiService = Api();
      await apiService.deleteReceipt(id);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Padding(
          padding: const EdgeInsets.all(8.0),
          child: TextField(
            controller: _searchController,
            onChanged: _filterReceipts,
            decoration: InputDecoration(
              hintText: 'Search by name or tag...',
            ),
          ),
        ),
        Expanded(
          child: ListView.builder(
            itemCount: filteredReceipts.length,
            itemBuilder: (context, index) {
            final title = filteredReceipts[index]['title'] as String;
            final List<String> tags = filteredReceipts[index]['tags'] as List<String>;
            final id = filteredReceipts[index]['id'] as int;
            final imageData =
                  filteredReceipts[index]['imageData'] as Uint8List;

              return Card(
                elevation: 5,
                margin: const EdgeInsets.all(8),
                child: ListTile(
                  title: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(title),
                    SizedBox(height: 4),
                    Wrap(
                      spacing: 4,
                      runSpacing: 4,
                      children: tags.map((tag) => Chip(label: Text(tag))).toList(),
                    ),
                  ],
                ),
                  onTap: () {
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
                  leading: FutureBuilder<Uint8List?>(
                    future: generateThumbnail(imageData),
                    builder: (context, snapshot) {
                      if (snapshot.connectionState == ConnectionState.waiting) {
                        return const CircularProgressIndicator();
                      } else if (snapshot.hasError || snapshot.data == null) {
                        return const Icon(Icons.error_outline);
                      } else {
                        return Image.memory(
                          snapshot.data!,
                          fit: BoxFit.cover,
                          width: 80, // Set the width for the thumbnail
                          height: 80, // Set the height for the thumbnail
                        );
                      }
                    },
                  ),
                  trailing: IconButton(
                    icon: Icon(Icons.delete),
                    onPressed: () => _confirmAndDeleteReceipt(id),
                  ),
                ),
              );
            },
          ),
        ),
      ],
    );
  }
}

class DatabasePage extends StatefulWidget {
  const DatabasePage({Key? key, required this.title}) : super(key: key);

  final String title;

  @override
  State<DatabasePage> createState() => _DatabasePageState();
}

class _DatabasePageState extends State<DatabasePage> {
  String _filePath = '';
  String _fileName = ''; 
  String _tag = ''; 
  TextEditingController _searchController = TextEditingController();
  TextEditingController _nameController = TextEditingController();
  TextEditingController _tagController = TextEditingController();

  // Method to show upload receipt dialog
  Future<void> _showUploadReceiptDialog() async {
    return showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: Text('Upload Receipt'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: _nameController,
                decoration: InputDecoration(
                  labelText: 'Name',
                ),
              ),
              TextField(
                controller: _tagController,
                decoration: InputDecoration(
                  labelText: 'Tag (optional)',
                ),
              ),
              ElevatedButton(
                onPressed: () async {
                  Navigator.of(context).pop(); // Close the dialog
                  await _pickAndUploadFile();
                },
                child: Text('Upload'),
              ),
            ],
          ),
        );
      },
    );
  }

  // Allows user to pick a file to upload
  Future<void> _pickAndUploadFile() async {
    String? filePath = await FilePicker.platform.pickFiles().then((result) {
      if (result != null) {
        return result.files.single.path;
      } else {
        return null;
      }
    });

    if (filePath != null) {
      _fileName = _nameController.text;
      _tag = _tagController.text;
      setState(() {
        _filePath = filePath;
      });

      try {
         await Api.uploadFile(_filePath, _fileName, _tag);
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
            onPressed: _showUploadReceiptDialog,
            child: Text('Upload Receipt'),
          ),
          SizedBox(height: 20),
          Expanded(
            child: MyListView(),
          ),
        ],
      ),
    );
  }
}
