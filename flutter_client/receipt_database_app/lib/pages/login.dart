// ignore_for_file: prefer_const_constructors
import "package:flutter/material.dart";
import "package:receipt_database_app/components/page_transitions.dart";
import "package:receipt_database_app/pages/database_page.dart";

class LoginState extends StatefulWidget {
  const LoginState({super.key});

  @override
  State<LoginState> createState() => _LoginStateState();
}

class _LoginStateState extends State<LoginState> {
  TextEditingController myController = TextEditingController();
  TextEditingController myController2 = TextEditingController();

  Map userData = {};
  final _formkey = GlobalKey<FormState>();

  @override
  Widget build(BuildContext context) {
    return SafeArea(
        child: Scaffold(
      backgroundColor: const Color.fromARGB(255, 174, 201, 214),

      appBar: AppBar(        
      backgroundColor: const Color.fromARGB(255, 174, 201, 214),
        leading: IconButton(
          icon: Icon(Icons.arrow_back),
          onPressed: () {
            Navigator.pop(context);
          },
        ),
      ),

      body: Column(
        children: [
          SizedBox(
            height: 50,
          ),
          Form(
            key: _formkey,
            child: Column(
              children: [
                Text("Username:"),
                Padding(
                  padding:
                      const EdgeInsets.only(left: 25, right: 25, bottom: 10),
                  child: TextFormField(
                    validator: (value) {
                      if (value == null || value.isEmpty) {
                        return 'Please enter some text';
                      }
                      return null;
                    },
                    decoration: InputDecoration(
                      border: OutlineInputBorder(),
                      labelText: "Username",
                      hintText: 'Username:',
                    ),
                    controller: myController,
                  ),
                ),
                Text("Password:"),
                Padding(
                  padding:
                      const EdgeInsets.only(left: 25, right: 25, bottom: 10),
                  child: TextFormField(
                    validator: (value) {
                      if (value == null || value.isEmpty) {
                        return 'Please enter some text';
                      }
                        //TALK TO SERVER TO CHECK IF CORRECT.
                      return null;
                    },
                    decoration: InputDecoration(
                      border: OutlineInputBorder(),
                      labelText: "Password",
                      hintText: 'Enter your password',
                    ),
                    obscureText: true,
                    enableSuggestions: false,
                    autocorrect: false,
                    controller: myController2,
                  ),
                ),
                Center(
                  child: ElevatedButton(
                      onPressed: () {
                        if (_formkey.currentState!.validate()) {
                          print('form submiitted');
                          //THIS IS WHERE I WOULD CALL BACKEND THEN SEND TO NEXT PAGE.
                          Navigator.push(
                    context,
                    customPageRoute(
                      page: const DatabasePage(title: "Main Ting", ),
                      beginOffset: const Offset(1.0, 0.0),
                      endOffset: Offset.zero,
                      curve: Curves.easeInOut,
                    ),
                  );
                        }
                      },
                      style: ButtonStyle(
                        backgroundColor: MaterialStateProperty.all(Colors.red),
                        minimumSize: MaterialStateProperty.all(Size(225, 40)),
                        elevation: MaterialStateProperty.all(6),
                        shape: MaterialStateProperty.all(RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(18.0),
                        )),
                      ),
                      child: Text("Sign In",
                          style: TextStyle(
                              fontFamily: 'Aleo',
                              fontStyle: FontStyle.normal,
                              fontWeight: FontWeight.bold,
                              fontSize: 25.0,
                              color: Colors.white))),
                ),
              ],
            ),
          ),
        ],
      ),
    ));
  }
}
