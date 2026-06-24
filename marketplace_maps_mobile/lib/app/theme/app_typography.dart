import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

/// Typography scale derived from the design spec (Inter family).
class AppTypography {
  AppTypography._();

  static TextTheme textTheme(Color onSurface) {
    final base = GoogleFonts.interTextTheme();
    return base.copyWith(
      displayLarge: base.displayLarge?.copyWith(color: onSurface),
      headlineLarge: GoogleFonts.inter(
        fontSize: 30,
        height: 38 / 30,
        letterSpacing: -0.02 * 30,
        fontWeight: FontWeight.w700,
        color: onSurface,
      ),
      headlineMedium: GoogleFonts.inter(
        fontSize: 24,
        height: 32 / 24,
        letterSpacing: -0.01 * 24,
        fontWeight: FontWeight.w600,
        color: onSurface,
      ),
      headlineSmall: GoogleFonts.inter(
        fontSize: 20,
        height: 28 / 20,
        fontWeight: FontWeight.w600,
        color: onSurface,
      ),
      bodyLarge: GoogleFonts.inter(
        fontSize: 16,
        height: 24 / 16,
        fontWeight: FontWeight.w400,
        color: onSurface,
      ),
      bodyMedium: GoogleFonts.inter(
        fontSize: 14,
        height: 20 / 14,
        fontWeight: FontWeight.w400,
        color: onSurface,
      ),
      labelMedium: GoogleFonts.inter(
        fontSize: 12,
        height: 16 / 12,
        letterSpacing: 0.02 * 12,
        fontWeight: FontWeight.w500,
        color: onSurface,
      ),
      labelLarge: GoogleFonts.inter(
        fontSize: 16,
        height: 24 / 16,
        letterSpacing: 0.01 * 16,
        fontWeight: FontWeight.w600,
        color: onSurface,
      ),
    );
  }
}
