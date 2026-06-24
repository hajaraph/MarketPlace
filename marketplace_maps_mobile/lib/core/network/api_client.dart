import 'dart:convert';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_dotenv/flutter_dotenv.dart';

/// Secure storage for JWT tokens.
class TokenStorage {
  static const _storage = FlutterSecureStorage();
  static const _accessTokenKey = 'access_token';
  static const _refreshTokenKey = 'refresh_token';

  Future<void> saveTokens(String access, String refresh) async {
    await _storage.write(key: _accessTokenKey, value: access);
    await _storage.write(key: _refreshTokenKey, value: refresh);
  }

  Future<String?> getAccessToken() => _storage.read(key: _accessTokenKey);
  Future<String?> getRefreshToken() => _storage.read(key: _refreshTokenKey);
  
  Future<void> clearTokens() async {
    await _storage.delete(key: _accessTokenKey);
    await _storage.delete(key: _refreshTokenKey);
  }
}

/// A custom HTTP client that automatically adds the Authorization header 
/// and handles token refreshing.
class AuthenticatedClient extends http.BaseClient {
  final http.Client _client = http.Client();
  final TokenStorage _tokenStorage = TokenStorage();
  final String _baseUrl = dotenv.env['BASE_URL'] ?? 'http://10.0.2.2:8000';

  @override
  Future<http.StreamedResponse> send(http.BaseRequest request) async {
    final token = await _tokenStorage.getAccessToken();
    if (token != null) {
      request.headers['Authorization'] = 'Bearer $token';
    }
    
    final response = await _client.send(request);

    // Si 401 Unauthorized, tenter de rafraîchir le token
    if (response.statusCode == 401) {
      final success = await _refreshToken();
      if (success) {
        // Retenter la requête originale avec le nouveau token
        final newRequest = _cloneRequest(request);
        final newToken = await _tokenStorage.getAccessToken();
        newRequest.headers['Authorization'] = 'Bearer $newToken';
        return _client.send(newRequest);
      }
    }
    return response;
  }

  Future<bool> _refreshToken() async {
    final refreshToken = await _tokenStorage.getRefreshToken();
    if (refreshToken == null) return false;

    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/api/auth/token/refresh/'),
        body: {'refresh': refreshToken},
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        await _tokenStorage.saveTokens(data['access'], refreshToken); // Refresh token often remains same
        return true;
      }
    } catch (e) {
      // Log error
    }
    
    await _tokenStorage.clearTokens();
    return false;
  }

  http.BaseRequest _cloneRequest(http.BaseRequest request) {
    // Note: This is a simplified clone. Full implementation requires 
    // copying all fields depending on request type.
    if (request is http.Request) {
      final newRequest = http.Request(request.method, request.url);
      newRequest.body = request.body;
      newRequest.headers.addAll(request.headers);
      return newRequest;
    }
    return request;
  }
}
