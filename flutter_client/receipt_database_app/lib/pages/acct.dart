import 'package:flutter/material.dart';

class MyAccountSetup extends StatefulWidget {
  const MyAccountSetup({super.key});

  @override
  State<MyAccountSetup> createState() => _MyAccountSetupState();
}

class _MyAccountSetupState extends State<MyAccountSetup> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: ElevatedButton(
          
          onPressed: () {
            Navigator.pop(context);
          },
          child: const Text('Go back!'),
        ),
      )
    );
  }
}