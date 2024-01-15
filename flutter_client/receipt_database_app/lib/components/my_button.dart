import 'package:flutter/material.dart';

import 'page_transitions.dart';

class OAuthButton extends StatelessWidget {
  final String hintText;
  final Image imageUsed;
  final Widget myPage;
  const OAuthButton({
    super.key,
    required this.hintText,
    required this.imageUsed,
    required this.myPage,
  });
  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 25.0),
      height: 60,
      child: OutlinedButton(
        onPressed: () {
          Navigator.push(
            context,
            customPageRoute(
              page: myPage,
              beginOffset: Offset(1.0, 0.0),
              endOffset: Offset.zero,
              curve: Curves.easeInOut,
            ),
          );
        },
        child: Row(
          children: [
            SizedBox(
              height: 60,
              width: 40,
              child: imageUsed,
            ),
             // Add some spacing between the image and text
            
            Expanded(child:Center(
              child: Text(
                  hintText,
                  textAlign: TextAlign.center, // Center the text horizontally
                  style: TextStyle(fontSize: 20), // Adjust the font size as needed
              ),
            ),
            ),

            SizedBox(
              height: 60,
              width: 40,
            ),
          ],
        ),
      ),
    );
  }
}

//--------------------------------------------------------------------------

//-------


