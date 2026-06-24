import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../app/router/app_router.dart';
import '../../../../app/theme/app_colors.dart';
import '../../../../app/theme/app_spacing.dart';
import '../../../../shared/widgets/app_text_field.dart';
import '../../../../shared/widgets/labeled_divider.dart';
import '../../../../shared/widgets/primary_button.dart';
import '../../../../shared/widgets/secondary_button.dart';

import '../providers/auth_provider.dart';

class LoginPage extends ConsumerStatefulWidget {
  const LoginPage({super.key});

  @override
  ConsumerState<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends ConsumerState<LoginPage> {
  final _emailCtrl = TextEditingController();
  final _passwordCtrl = TextEditingController();
  bool _obscurePassword = true;

  @override
  void dispose() {
    _emailCtrl.dispose();
    _passwordCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authStateProvider);
    final textTheme = Theme.of(context).textTheme;

    ref.listen(authStateProvider, (previous, next) {
      if (next.isAuthenticated) {
        context.go(AppRoutes.home);
      }
      if (next.errorMessage != null && next.errorMessage != previous?.errorMessage) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(next.errorMessage!)),
        );
      }
    });

    return Scaffold(
      backgroundColor: AppColors.background,
      body: Stack(
        children: [
          Positioned.fill(
            child: DecoratedBox(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [
                    AppColors.primaryFixed.withValues(alpha: 0.4),
                    AppColors.background.withValues(alpha: 0),
                  ],
                ),
              ),
            ),
          ),
          SafeArea(
            child: Column(
              children: [
                _Header(
                  onBack: () {
                    if (Navigator.of(context).canPop()) {
                      Navigator.of(context).pop();
                    } else {
                      context.go(AppRoutes.home);
                    }
                  },
                ),
                Expanded(
                  child: Center(
                    child: ConstrainedBox(
                      constraints: const BoxConstraints(maxWidth: 440),
                      child: SingleChildScrollView(
                        padding: const EdgeInsets.symmetric(
                          horizontal: AppSpacing.safeMargin,
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
                            const SizedBox(height: AppSpacing.lg),
                            Text(
                              'Bon retour',
                              textAlign: TextAlign.center,
                              style: textTheme.headlineLarge,
                            ),
                            const SizedBox(height: AppSpacing.sm),
                            Text(
                              'Connectez-vous à votre compte Marketplace.',
                              textAlign: TextAlign.center,
                              style: textTheme.bodyMedium?.copyWith(
                                color: AppColors.onSurfaceVariant,
                              ),
                            ),
                            const SizedBox(height: 40),

                            AppTextField(
                              label: 'E-mail ou numéro de téléphone',
                              controller: _emailCtrl,
                              keyboardType: TextInputType.text,
                              textInputAction: TextInputAction.next,
                              autofillHints: const [
                                AutofillHints.email,
                                AutofillHints.telephoneNumber,
                              ],
                            ),
                            const SizedBox(height: AppSpacing.md),

                            AppTextField(
                              label: 'Mot de passe',
                              controller: _passwordCtrl,
                              obscureText: _obscurePassword,
                              textInputAction: TextInputAction.done,
                              autofillHints: const [AutofillHints.password],
                              suffixIcon: IconButton(
                                onPressed: () => setState(() => _obscurePassword = !_obscurePassword),
                                icon: Icon(
                                  _obscurePassword
                                      ? Icons.visibility_outlined
                                      : Icons.visibility_off_outlined,
                                  color: AppColors.outline,
                                ),
                              ),
                            ),
                            const SizedBox(height: AppSpacing.lg),

                            PrimaryButton(
                              label: 'Se connecter',
                              isLoading: authState.isLoading,
                              onPressed: () {
                                ref.read(authStateProvider.notifier).login(
                                      _emailCtrl.text,
                                      _passwordCtrl.text,
                                    );
                              },
                            ),
                            const SizedBox(height: AppSpacing.lg),

                            const LabeledDivider(label: 'ou'),
                            const SizedBox(height: AppSpacing.lg),

                            SecondaryButton(
                              label: 'Continuer avec Google',
                              leading: const Icon(Icons.g_mobiledata, size: 24),
                              onPressed: () {},
                            ),
                            const SizedBox(height: 40),

                            _FooterLinks(
                              onSignUp: () => context.push(AppRoutes.createAccount),
                            ),
                            const SizedBox(height: AppSpacing.lg),
                          ],
                        ),
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _Header extends StatelessWidget {
  const _Header({required this.onBack});

  final VoidCallback onBack;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 64,
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: AppSpacing.safeMargin),
        child: Row(
          children: [
            SizedBox(
              width: 44,
              height: 44,
              child: IconButton(
                onPressed: onBack,
                icon: const Icon(Icons.arrow_back, color: AppColors.onSurface),
                splashRadius: 22,
              ),
            ),
            Expanded(
              child: Center(
                child: Text(
                  'Marketplace',
                  style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                        color: AppColors.primary,
                        fontWeight: FontWeight.w700,
                        letterSpacing: -0.5,
                      ),
                ),
              ),
            ),
            const SizedBox(width: 44),
          ],
        ),
      ),
    );
  }
}

class _FooterLinks extends StatelessWidget {
  const _FooterLinks({required this.onSignUp});

  final VoidCallback onSignUp;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Text(
          'Pas de compte ? ',
          style: textTheme.bodyMedium?.copyWith(
            color: AppColors.onSurfaceVariant,
          ),
        ),
        GestureDetector(
          onTap: onSignUp,
          child: Text(
            'S\'inscrire',
            style: textTheme.bodyMedium?.copyWith(
              color: AppColors.primary,
              fontWeight: FontWeight.w600,
            ),
          ),
        ),
      ],
    );
  }
}
