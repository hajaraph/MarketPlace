/// Spacing scale extracted from the design spec.
/// All numeric values are expressed in logical pixels.
class AppSpacing {
  AppSpacing._();

  static const double unit = 4;
  static const double xs = 4;
  static const double sm = 8;
  static const double md = 16;
  static const double lg = 24;
  static const double xl = 32;
  static const double gutter = 16;
  static const double safeMargin = 20;
  static const double touchTargetMin = 44;
}

/// Border radius scale.
class AppRadius {
  AppRadius._();

  static const double defaultRadius = 4; // 0.25rem
  static const double lg = 8; // 0.5rem
  static const double xl = 12; // 0.75rem
  static const double xl2 = 16; // 1rem
  static const double xl3 = 24; // 1.5rem
  static const double full = 9999;
}
