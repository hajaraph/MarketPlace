import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_dotenv/flutter_dotenv.dart';
import '../models/auth_response_model.dart';
import '../../../../core/errors/exceptions.dart';

abstract class AuthRemoteDataSource {
  Future<AuthResponseModel> login({
    required String username,
    required String password,
  });

  Future<AuthResponseModel> register({
    required String email,
    required String password,
    String? firstName,
    String? lastName,
  });
}

class AuthRemoteDataSourceImpl implements AuthRemoteDataSource {
  final http.Client client;
  final String baseUrl = dotenv.env['BASE_URL'] ?? 'http://10.0.2.2:8000';

  AuthRemoteDataSourceImpl({required this.client});

  @override
  Future<AuthResponseModel> login({
    required String username,
    required String password,
  }) async {
    final response = await client.post(
      Uri.parse('$baseUrl/api/auth/login/'),
      body: {
        'username': username,
        'password': password,
      },
    );

    if (response.statusCode == 200) {
      final jsonResponse = json.decode(response.body);
      return AuthResponseModel.fromJson(jsonResponse['data']);
    } else if (response.statusCode == 401) {
      throw ServerException('Identifiants invalides');
    } else {
      throw ServerException('Erreur serveur');
    }
  }

  @override
  Future<AuthResponseModel> register({
    required String email,
    required String password,
    String? firstName,
    String? lastName,
  }) async {
    final response = await client.post(
      Uri.parse('$baseUrl/api/auth/register/'),
      body: {
        'username': email,
        'email': email,
        'password': password,
        'first_name': firstName ?? '',
        'last_name': lastName ?? '',
      },
    );

    if (response.statusCode == 201) {
      final jsonResponse = json.decode(response.body);
      return AuthResponseModel.fromJson(jsonResponse['data']);
    } else {
      final jsonResponse = json.decode(response.body);
      final message = jsonResponse['error']?['message'] ?? 'Erreur lors de l\'inscription';
      throw ServerException(message);
    }
  }
}
