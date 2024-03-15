import 'package:flutter/material.dart';
import 'package:receipt_database_app/components/my_button.dart';
import 'package:receipt_database_app/components/page_transitions.dart';
import 'package:receipt_database_app/pages/acct.dart';
import 'package:receipt_database_app/pages/database_page.dart';
import 'package:receipt_database_app/pages/login.dart';

class InitialPage extends StatelessWidget {
  const InitialPage({super.key});
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color.fromARGB(255, 174, 201, 214),
      body: SafeArea(
          child: Center(

        child: Column(
          children: [
            const SizedBox(height: 100),

            //logo
            const Icon(
              Icons.star_half,
              size: 150,
            ),

            const SizedBox(
              height: 150.0,
            ),
            //Welcome back text??

            //Create new Account - Button

            Container(
              margin: const EdgeInsets.symmetric(horizontal: 25.0),
              height: 60,
              child: OutlinedButton(
                onPressed: () {
                  Navigator.push(
                    context,
                    customPageRoute(
                      page: const MyAccountSetup(),
                      beginOffset: const Offset(1.0, 0.0),
                      endOffset: Offset.zero,
                      curve: Curves.easeInOut,
                    ),
                  );
                },
                child: const Center(
                    child: Text(
                  "Create New Account",
                  style: TextStyle(
                    fontSize: 20.0,
                  ),
                )),
              ),
            ),

            const SizedBox(height: 10.0),

            //Sign in - Button

            //Continue with Google - Button
            OAuthButton(
              hintText: 'Continue with Google',
              imageUsed: Image.asset('lib/images/googleLogo.png'),
               myPage: DatabasePage(title: "Receipt Database"),
            ),

            const SizedBox(height: 10.0),
            //Continue with Apple - Button
            OAuthButton(
              hintText: 'Continue with Apple',
              imageUsed: Image.asset('lib/images/appleLogo.png'), 
              myPage: DatabasePage(title: "Receipt Database"),
            ),

            const SizedBox(
              height: 10.0,
            ),

            Container(
              margin: const EdgeInsets.symmetric(horizontal: 25.0),
              width: 900,
              height: 60,
              child: TextButton(
                onPressed: () {
                    Navigator.push(
                      context,
                      customPageRoute(
                        page: const LoginState(),
                        beginOffset: const Offset(1.0, 0.0),
                        endOffset: Offset.zero,
                        curve: Curves.easeInOut,
                      ),
                    );
                  },
                child: const Text(
                  "Login",
                  style: TextStyle(fontSize: 20.0),
                  ),
                ),
            )
          ],
        ),
      )),
    );
  }
}
