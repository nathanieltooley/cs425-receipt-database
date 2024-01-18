import 'package:flutter/material.dart';
import 'package:receipt_database_app/pages/initial_page.dart';
import 'package:file_picker/file_picker.dart';
import 'components/api.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Receipt Database',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.lightBlue),
        useMaterial3: true,
      ),
      home: const InitialPage()
      );
  }
}