/// Reusable input validators for form fields.
class Validators {
  Validators._();

  static final RegExp _emailRegex = RegExp(
    r"^[\w\.\-\+]+@([\w\-]+\.)+[\w\-]{2,}$",
  );

  static String? email(String? value) {
    if (value == null || value.trim().isEmpty) {
      return 'Email is required';
    }
    if (!_emailRegex.hasMatch(value.trim())) {
      return 'Enter a valid email address';
    }
    return null;
  }

  static String? password(String? value) {
    if (value == null || value.isEmpty) {
      return 'Password is required';
    }
    if (value.length < 8) {
      return 'Password must be at least 8 characters';
    }
    return null;
  }
}
