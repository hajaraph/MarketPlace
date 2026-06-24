import '../../domain/entities/auth_user.dart';

class UserModel extends AuthUser {
  const UserModel({
    required super.id,
    required super.email,
    required this.username,
  });

  final String username;

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['id'].toString(),
      email: json['email'],
      username: json['username'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'email': email,
      'username': username,
    };
  }
}
