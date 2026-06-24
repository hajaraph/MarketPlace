/// Exceptions thrown by data sources. They are caught at the repository
/// boundary and converted into [Failure]s.
class ServerException implements Exception {
  const ServerException([this.message = 'Server exception']);
  final String message;
}

class NetworkException implements Exception {
  const NetworkException([this.message = 'Network exception']);
  final String message;
}

class CacheException implements Exception {
  const CacheException([this.message = 'Cache exception']);
  final String message;
}
