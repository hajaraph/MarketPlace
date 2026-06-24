import 'package:flutter/material.dart';

/// Material 3 design tokens extracted from the design spec (code.html).
/// Centralized to keep the palette source-of-truth in a single location.
class AppColors {
  AppColors._();

  // Primary
  static const Color primary = Color(0xFF0058BE);
  static const Color onPrimary = Color(0xFFFFFFFF);
  static const Color primaryContainer = Color(0xFF2170E4);
  static const Color onPrimaryContainer = Color(0xFFFEFCFF);
  static const Color primaryFixed = Color(0xFFD8E2FF);
  static const Color primaryFixedDim = Color(0xFFADC6FF);
  static const Color onPrimaryFixed = Color(0xFF001A42);
  static const Color onPrimaryFixedVariant = Color(0xFF004395);
  static const Color inversePrimary = Color(0xFFADC6FF);

  // Secondary
  static const Color secondary = Color(0xFF006C49);
  static const Color onSecondary = Color(0xFFFFFFFF);
  static const Color secondaryContainer = Color(0xFF6CF8BB);
  static const Color onSecondaryContainer = Color(0xFF00714D);
  static const Color secondaryFixed = Color(0xFF6FFBBE);
  static const Color secondaryFixedDim = Color(0xFF4EDEA3);
  static const Color onSecondaryFixed = Color(0xFF002113);
  static const Color onSecondaryFixedVariant = Color(0xFF005236);

  // Tertiary
  static const Color tertiary = Color(0xFF4648D4);
  static const Color onTertiary = Color(0xFFFFFFFF);
  static const Color tertiaryContainer = Color(0xFF6063EE);
  static const Color onTertiaryContainer = Color(0xFFFFFBFF);
  static const Color tertiaryFixed = Color(0xFFE1E0FF);
  static const Color tertiaryFixedDim = Color(0xFFC0C1FF);
  static const Color onTertiaryFixed = Color(0xFF07006C);
  static const Color onTertiaryFixedVariant = Color(0xFF2F2EBE);

  // Error
  static const Color error = Color(0xFFBA1A1A);
  static const Color onError = Color(0xFFFFFFFF);
  static const Color errorContainer = Color(0xFFFFDAD6);
  static const Color onErrorContainer = Color(0xFF93000A);

  // Surface
  static const Color background = Color(0xFFF9F9FF);
  static const Color onBackground = Color(0xFF191B23);
  static const Color surface = Color(0xFFF9F9FF);
  static const Color onSurface = Color(0xFF191B23);
  static const Color surfaceVariant = Color(0xFFE1E2EC);
  static const Color onSurfaceVariant = Color(0xFF424754);
  static const Color surfaceBright = Color(0xFFF9F9FF);
  static const Color surfaceDim = Color(0xFFD8D9E3);
  static const Color surfaceTint = Color(0xFF005AC2);

  // Surface containers
  static const Color surfaceContainerLowest = Color(0xFFFFFFFF);
  static const Color surfaceContainerLow = Color(0xFFF2F3FD);
  static const Color surfaceContainer = Color(0xFFECEDF7);
  static const Color surfaceContainerHigh = Color(0xFFE6E7F2);
  static const Color surfaceContainerHighest = Color(0xFFE1E2EC);

  // Outline
  static const Color outline = Color(0xFF727785);
  static const Color outlineVariant = Color(0xFFC2C6D6);

  // Inverse
  static const Color inverseSurface = Color(0xFF2E3038);
  static const Color inverseOnSurface = Color(0xFFEFF0FA);
}
