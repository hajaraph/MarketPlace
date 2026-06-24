import 'package:dartz/dartz.dart';

import '../../../../core/errors/failures.dart';
import '../entities/auth_user.dart';

/// Authentication repository contract (domain layer).
abstract class AuthRepository {
  Future<Either<Failure, AuthUser>> signUpWithEmail({
    required String email,
    required String password,
  });

  Future<Either<Failure, AuthUser>> signInWithEmail({
    required String username,
    required String password,
  });

  Future<Either<Failure, AuthUser>> signInWithGoogle();

  Future<Either<Failure, AuthUser>> signInWithApple();
}
