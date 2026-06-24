import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/network/api_client.dart';
import '../../features/auth/presentation/pages/create_account_page.dart';
import '../../features/auth/presentation/pages/login_page.dart';
import '../../features/home/presentation/pages/home_page.dart';

/// Centralized route names (typed access, no stringly-typed routes).
class AppRoutes {
  AppRoutes._();

  static const String createAccount = '/create-account';
  static const String login = '/login';
  static const String home = '/';
}

final appRouterProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    initialLocation: AppRoutes.home,
    redirect: (context, state) async {
      final tokenStorage = TokenStorage();
      final accessToken = await tokenStorage.getAccessToken();
      
      final isLoggingIn = state.matchedLocation == AppRoutes.login;
      final isCreatingAccount = state.matchedLocation == AppRoutes.createAccount;
      final isHome = state.matchedLocation == AppRoutes.home;

      // Allow access to auth pages AND home (Explore) if not authenticated
      if (accessToken == null) {
        if (isLoggingIn || isCreatingAccount || isHome) {
          return null;
        }
        return AppRoutes.login;
      }
      
      // If authenticated, prevent access to auth pages
      if (isLoggingIn || isCreatingAccount) {
        return AppRoutes.home;
      }
      
      return null;
    },
    routes: [
      GoRoute(
        path: AppRoutes.home,
        name: 'home',
        builder: (context, state) => const HomePage(),
      ),
      GoRoute(
        path: AppRoutes.createAccount,
        name: 'createAccount',
        builder: (context, state) => const CreateAccountPage(),
      ),
      GoRoute(
        path: AppRoutes.login,
        name: 'login',
        builder: (context, state) => const LoginPage(),
      ),
    ],
  );
});
