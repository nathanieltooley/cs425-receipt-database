import 'dart:io';
import 'dart:typed_data';
import 'package:path_provider/path_provider.dart';

class ImageCache {
  Future<void> storeBytesInCache(Uint8List bytes, String fileName) async {
    final directory = await getTemporaryDirectory();
    final file = File('${directory.path}/$fileName');

    await file.writeAsBytes(bytes);
  }
}