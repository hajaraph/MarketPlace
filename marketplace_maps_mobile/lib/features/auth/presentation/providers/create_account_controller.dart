import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../domain/repositories/auth_repository.dart';
import 'auth_provider.dart';

/// UI state for the Create Account screen.
class CreateAccountState {
  const CreateAccountState({
    this.email = '',
    this.password = '',
    this.obscurePassword = true,
    this.isSubmitting = false,
    this.isSuccess = false,
    this.errorMessage,
  });

  final String email;
  final String password;
  final bool obscurePassword;
  final bool isSubmitting;
  final bool isSuccess;
  final String? errorMessage;

  CreateAccountState copyWith({
    String? email,
    String? password,
    bool? obscurePassword,
    bool? isSubmitting,
    bool? isSuccess,
    String? errorMessage,
    bool clearError = false,
  }) {
    return CreateAccountState(
      email: email ?? this.email,
      password: password ?? this.password,
      obscurePassword: obscurePassword ?? this.obscurePassword,
      isSubmitting: isSubmitting ?? this.isSubmitting,
      isSuccess: isSuccess ?? this.isSuccess,
      errorMessage: clearError ? null : (errorMessage ?? this.errorMessage),
    );
  }
}

class CreateAccountController extends StateNotifier<CreateAccountState> {
  final AuthRepository _repository;

  CreateAccountController(this._repository) : super(const CreateAccountState());

  void setEmail(String value) =>
      state = state.copyWith(email: value, clearError: true);

  void setPassword(String value) =>
      state = state.copyWith(password: value, clearError: true);

  void togglePasswordVisibility() =>
      state = state.copyWith(obscurePassword: !state.obscurePassword);

  Future<void> submit() async {
    if (state.isSubmitting) return;
    state = state.copyWith(isSubmitting: true, clearError: true);
    
    final result = await _repository.signUpWithEmail(
      email: state.email,
      password: state.password,
    );

    result.fold(
      (failure) => state = state.copyWith(
        isSubmitting: false,
        errorMessage: failure.message,
      ),
      (user) => state = state.copyWith(
        isSubmitting: false,
        isSuccess: true,
      ),
    );
  }
}

final createAccountControllerProvider = StateNotifierProvider.autoDispose<
    CreateAccountController, CreateAccountState>(
  (ref) => CreateAccountController(ref.watch(authRepositoryProvider)),
);
