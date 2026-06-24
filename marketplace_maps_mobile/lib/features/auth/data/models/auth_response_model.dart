import 'user_model.dart';

class AuthResponseModel {
  const AuthResponseModel({
    required this.refresh,
    required this.access,
    required this.user,
  });

  final String refresh;
  final String access;
  final UserModel user;

  factory AuthResponseModel.fromJson(Map<String, dynamic> json) {
    return AuthResponseModel(
      refresh: json['refresh'],
      access: json['access'],
      user: UserModel.fromJson(json['user']),
    );
  }
}
