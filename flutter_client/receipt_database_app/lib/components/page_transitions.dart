import 'package:flutter/material.dart';

PageRouteBuilder<dynamic> customPageRoute({
  required Widget page,
  required Offset beginOffset,
  required Offset endOffset,
  required Curve curve,
}) {
  return PageRouteBuilder(
    pageBuilder: (context, animation, secondaryAnimation) => page,
    transitionsBuilder: (context, animation, secondaryAnimation, child) {
      var tween = Tween(begin: beginOffset, end: endOffset).chain(CurveTween(curve: curve));
      var offsetAnimation = animation.drive(tween);
      return SlideTransition(position: offsetAnimation, child: child);
    },
  );
}

