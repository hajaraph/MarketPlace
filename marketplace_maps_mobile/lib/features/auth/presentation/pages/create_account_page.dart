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
import '../providers/create_account_controller.dart';

/// Sign-up screen reproducing the design spec from `code.html`.
/// Note: the bottom navigation bar from the spec is intentionally omitted
/// (auth flows should not surface the main app navigation).
class CreateAccountPage extends ConsumerStatefulWidget {
  const CreateAccountPage({super.key});

  @override
  ConsumerState<CreateAccountPage> createState() => _CreateAccountPageState();
}

class _CreateAccountPageState extends ConsumerState<CreateAccountPage> {
  final _emailCtrl = TextEditingController();
  final _passwordCtrl = TextEditingController();

  @override
  void dispose() {
    _emailCtrl.dispose();
    _passwordCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(createAccountControllerProvider);
    final controller = ref.read(createAccountControllerProvider.notifier);
    final textTheme = Theme.of(context).textTheme;

    ref.listen(createAccountControllerProvider, (prev, next) {
      if (next.isSuccess && prev?.isSuccess != true) {
        context.go(AppRoutes.home);
      }
    });

    return Scaffold(
      backgroundColor: AppColors.background,
      body: Stack(
        children: [
          // Subtle vertical gradient (matches `.custom-gradient` in spec).
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
                            // Heading
                            Text(
                              'Créer un compte',
                              textAlign: TextAlign.center,
                              style: textTheme.headlineLarge,
                            ),
                            const SizedBox(height: AppSpacing.sm),
                            Text(
                              'Rejoignez notre marketplace globale et organisée.',
                              textAlign: TextAlign.center,
                              style: textTheme.bodyMedium?.copyWith(
                                color: AppColors.onSurfaceVariant,
                              ),
                            ),
                            const SizedBox(height: 40),

                            // Email
                            AppTextField(
                              label: 'Adresse e-mail',
                              controller: _emailCtrl,
                              keyboardType: TextInputType.emailAddress,
                              textInputAction: TextInputAction.next,
                              autofillHints: const [AutofillHints.email],
                              onChanged: controller.setEmail,
                            ),
                            const SizedBox(height: AppSpacing.md),

                            // Password
                            AppTextField(
                              label: 'Mot de passe',
                              controller: _passwordCtrl,
                              obscureText: state.obscurePassword,
                              textInputAction: TextInputAction.done,
                              autofillHints: const [AutofillHints.newPassword],
                              onChanged: controller.setPassword,
                              suffixIcon: IconButton(
                                onPressed: controller.togglePasswordVisibility,
                                icon: Icon(
                                  state.obscurePassword
                                      ? Icons.visibility_outlined
                                      : Icons.visibility_off_outlined,
                                  color: AppColors.outline,
                                ),
                              ),
                            ),
                            const SizedBox(height: AppSpacing.lg),

                            // CTA
                            PrimaryButton(
                              label: 'Continuer',
                              isLoading: state.isSubmitting,
                              onPressed: controller.submit,
                            ),
                            const SizedBox(height: AppSpacing.lg),

                            const LabeledDivider(label: 'ou'),
                            const SizedBox(height: AppSpacing.lg),

                            // Google
                            SecondaryButton(
                              label: 'Continuer avec Google',
                              leading: const _GoogleGlyph(),
                              onPressed: () {},
                            ),
                            const SizedBox(height: AppSpacing.md),

                            // Apple
                            SecondaryButton(
                              label: 'Continuer avec Apple',
                              background: AppColors.onSurface,
                              foreground: AppColors.surfaceContainerLowest,
                              borderColor: AppColors.onSurface,
                              leading: const Icon(
                                Icons.apple,
                                color: Colors.white,
                                size: 22,
                              ),
                              onPressed: () {},
                            ),

                            const SizedBox(height: 40),

                            // Footer
                            _FooterLinks(
                              onLogin: () {},
                              onTerms: () {},
                              onPrivacy: () {},
                              onHelp: () {},
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
  const _FooterLinks({
    required this.onLogin,
    required this.onTerms,
    required this.onPrivacy,
    required this.onHelp,
  });

  final VoidCallback onLogin;
  final VoidCallback onTerms;
  final VoidCallback onPrivacy;
  final VoidCallback onHelp;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    return Column(
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              'Already have an account? ',
              style: textTheme.bodyMedium?.copyWith(
                color: AppColors.onSurfaceVariant,
              ),
            ),
            GestureDetector(
              onTap: onLogin,
              child: Text(
                'Log in',
                style: textTheme.bodyMedium?.copyWith(
                  color: AppColors.primary,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: AppSpacing.xl),
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            _FooterLink(label: 'Terms', onTap: onTerms),
            const _FooterDot(),
            _FooterLink(label: 'Privacy', onTap: onPrivacy),
            const _FooterDot(),
            _FooterLink(label: 'Help', onTap: onHelp),
          ],
        ),
      ],
    );
  }
}

class _FooterLink extends StatelessWidget {
  const _FooterLink({required this.label, required this.onTap});

  final String label;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: AppSpacing.sm),
        child: Text(
          label,
          style: Theme.of(context).textTheme.labelMedium?.copyWith(
                color: AppColors.outline,
              ),
        ),
      ),
    );
  }
}

class _FooterDot extends StatelessWidget {
  const _FooterDot();

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 4,
      height: 4,
      decoration: const BoxDecoration(
        color: AppColors.outlineVariant,
        shape: BoxShape.circle,
      ),
    );
  }
}

/// Inline minimal Google "G" glyph rendered with [CustomPaint] so the screen
/// stays self-contained (no remote asset dependency).
class _GoogleGlyph extends StatelessWidget {
  const _GoogleGlyph();

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 20,
      height: 20,
      child: CustomPaint(painter: _GoogleGlyphPainter()),
    );
  }
}

class _GoogleGlyphPainter extends CustomPainter {
  static const _blue = Color(0xFF4285F4);
  static const _green = Color(0xFF34A853);
  static const _yellow = Color(0xFFFBBC05);
  static const _red = Color(0xFFEA4335);

  @override
  void paint(Canvas canvas, Size size) {
    final cx = size.width / 2;
    final cy = size.height / 2;
    final r = size.width / 2;
    final rect = Rect.fromCircle(center: Offset(cx, cy), radius: r);
    final stroke = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = size.width * 0.22
      ..strokeCap = StrokeCap.butt;

    // Four colored arcs forming the "G" ring.
    canvas.drawArc(rect, -0.6, 1.4, false, stroke..color = _blue);
    canvas.drawArc(rect, 0.85, 1.4, false, stroke..color = _green);
    canvas.drawArc(rect, 2.3, 1.4, false, stroke..color = _yellow);
    canvas.drawArc(rect, 3.75, 1.4, false, stroke..color = _red);

    // Horizontal bar of the "G".
    final bar = Paint()..color = _blue;
    canvas.drawRect(
      Rect.fromLTWH(cx, cy - size.height * 0.06, r * 0.85, size.height * 0.16),
      bar,
    );
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
