// ignore_for_file: prefer_const_constructors
import "package:flutter/material.dart";
import "package:receipt_database_app/pages/acct.dart";

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
    return Scaffold(
      backgroundColor: Colors.blue,
      body: Column(
        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
        children: <Widget>[
          Icon(Icons.add_road_sharp),
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
                      return null;
                    },
                    /*
                    RequiredValidator( 
                        errorText: 'Please enter Password'), 
                    MinLengthValidator(8, 
                        errorText: 
                            'Password must be atlist 8 digit'), 
                    PatternValidator(r'(?=.*?[#!@$%^&*-])', 
                        errorText: 
                            'Password must be atlist one special character') 
                     ]), 
                      */
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


          Center(
            child: ElevatedButton(
              onPressed: () {
                Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => const MyAccountSetup()),
  );
              },
              style: ButtonStyle(
                  backgroundColor: MaterialStateProperty.all(Colors.red),
                  minimumSize: MaterialStateProperty.all(Size(225, 40)),
                  elevation: MaterialStateProperty.all(5),
                  shape: MaterialStateProperty.all(RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(18.0),
                  ))),
              child: Text(
                "Create Account",
                style: TextStyle(
                    fontFamily: 'Aleo',
                    fontStyle: FontStyle.normal,
                    fontWeight: FontWeight.bold,
                    fontSize: 25.0,
                    color: Colors.white),
              ),
            ),
          )
        ],
      ),
    );
  }
}
