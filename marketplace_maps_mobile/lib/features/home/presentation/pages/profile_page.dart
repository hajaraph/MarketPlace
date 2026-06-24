import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../app/router/app_router.dart';
import '../../../../app/theme/app_colors.dart';
import '../../../../app/theme/app_spacing.dart';
import '../../../auth/presentation/providers/auth_provider.dart';

/// Profile / Account Management page.
class ProfilePage extends ConsumerWidget {
  const ProfilePage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final textTheme = Theme.of(context).textTheme;
    final authState = ref.watch(authStateProvider);

    return Scaffold(
      backgroundColor: AppColors.background,
      body: CustomScrollView(
        slivers: [
          SliverToBoxAdapter(
            child: _Header(
              onBack: () {},
              title: 'Compte',
              isAuthenticated: authState.isAuthenticated,
              onLogin: () => context.push(AppRoutes.login),
            ),
          ),
          if (!authState.isAuthenticated)
            SliverFillRemaining(
              hasScrollBody: false,
              child: Center(
                child: Padding(
                  padding: const EdgeInsets.all(AppSpacing.xl),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(
                        Icons.account_circle_outlined,
                        size: 80,
                        color: AppColors.outline.withValues(alpha: 0.2),
                      ),
                      const SizedBox(height: AppSpacing.lg),
                      Text(
                        'Connectez-vous pour voir votre profil',
                        style: textTheme.headlineSmall?.copyWith(
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      const SizedBox(height: AppSpacing.sm),
                      Text(
                        'Gérez vos commandes, vos favoris et plus encore.',
                        textAlign: TextAlign.center,
                        style: textTheme.bodyMedium?.copyWith(
                          color: AppColors.onSurfaceVariant,
                        ),
                      ),
                      const SizedBox(height: AppSpacing.xl),
                      FilledButton(
                        onPressed: () => context.push(AppRoutes.login),
                        child: const Text('Se connecter'),
                      ),
                    ],
                  ),
                ),
              ),
            )
          else
            SliverPadding(
              padding: const EdgeInsets.symmetric(horizontal: AppSpacing.safeMargin),
              sliver: SliverList(
                delegate: SliverChildListDelegate([
                  const SizedBox(height: AppSpacing.lg),
                  const _ProfileCard(
                    name: 'Julian Alexander',
                    email: 'julian.a@marketplace.com',
                    badgeLabel: 'BRONZE',
                    membershipTag: 'MEMBRE DEPUIS 2023',
                  ),
                  const SizedBox(height: 32),
                  const _SectionTitle(label: 'Activité et préférences'),
                  const SizedBox(height: AppSpacing.md),
                  _CardContainer(
                    children: [
                      _MenuItem(
                        icon: Icons.shopping_bag_outlined,
                        iconBg: AppColors.primary.withValues(alpha: 0.05),
                        iconColor: AppColors.primary,
                        title: 'Mes commandes',
                        subtitle: 'Gérez vos achats récents',
                        onTap: () {},
                      ),
                      const _Divider(),
                      _MenuItem(
                        icon: Icons.payments_outlined,
                        iconBg: AppColors.secondary.withValues(alpha: 0.05),
                        iconColor: AppColors.secondary,
                        title: 'Moyens de paiement',
                        subtitle: 'Visa se terminant par 4242',
                        onTap: () {},
                      ),
                      const _Divider(),
                      _MenuItem(
                        icon: Icons.bookmarks_outlined,
                        iconBg: AppColors.tertiary.withValues(alpha: 0.05),
                        iconColor: AppColors.tertiary,
                        title: 'Marchés enregistrés',
                        subtitle: '12 lieux suivis',
                        onTap: () {},
                      ),
                    ],
                  ),
                  const SizedBox(height: 32),
                  const _SectionTitle(label: 'Application'),
                  const SizedBox(height: AppSpacing.md),
                  _CardContainer(
                    children: [
                      _MenuItem(
                        icon: Icons.settings_outlined,
                        iconBg: AppColors.surfaceContainerHighest,
                        iconColor: AppColors.onSurfaceVariant,
                        title: 'Paramètres',
                        subtitle: 'Configuration de l\'application et confidentialité',
                        onTap: () {},
                      ),
                    ],
                  ),
                  const SizedBox(height: 40),
                  FilledButton.tonal(
                    onPressed: () {},
                    style: FilledButton.styleFrom(
                      backgroundColor: AppColors.errorContainer,
                      foregroundColor: AppColors.onErrorContainer,
                      minimumSize: const Size(double.infinity, 56),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(AppRadius.xl2),
                      ),
                      textStyle: textTheme.labelLarge?.copyWith(fontWeight: FontWeight.w600),
                    ),
                    child: const Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.logout, size: 20),
                        SizedBox(width: AppSpacing.sm),
                        Text('Se déconnecter'),
                      ],
                    ),
                  ),
                  const SizedBox(height: AppSpacing.lg),
                  Center(
                    child: Text(
                      'Version 2.4.1 (Build 882)',
                      style: textTheme.labelMedium?.copyWith(
                        color: AppColors.outline.withValues(alpha: 0.6),
                      ),
                    ),
                  ),
                  const SizedBox(height: AppSpacing.xl + 20),
                ]),
              ),
            ),
        ],
      ),
    );
  }
}

class _Header extends StatelessWidget {
  const _Header({
    required this.title,
    required this.onBack,
    required this.isAuthenticated,
    required this.onLogin,
  });
  final String title;
  final VoidCallback onBack;
  final bool isAuthenticated;
  final VoidCallback onLogin;

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: SizedBox(
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
                  icon: const Icon(Icons.arrow_back, color: AppColors.primary),
                  splashRadius: 22,
                ),
              ),
              const SizedBox(width: AppSpacing.sm),
              Expanded(
                child: Text(
                  title,
                  style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                        color: AppColors.onSurface,
                        fontWeight: FontWeight.w600,
                      ),
                ),
              ),
              if (!isAuthenticated)
                TextButton(
                  onPressed: onLogin,
                  child: const Text('Se connecter'),
                )
              else
                Container(
                  width: 40,
                  height: 40,
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(AppRadius.full),
                    border: Border.all(color: AppColors.primary.withValues(alpha: 0.1), width: 2),
                    color: AppColors.surfaceContainerHigh,
                  ),
                  child: ClipOval(
                    child: Center(
                      child: Icon(Icons.person, size: 22, color: AppColors.onSurfaceVariant),
                    ),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }
}
class _ProfileCard extends StatelessWidget {
  const _ProfileCard({
    required this.name,
    required this.email,
    required this.badgeLabel,
    required this.membershipTag,
  });
  final String name;
  final String email;
  final String badgeLabel;
  final String membershipTag;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    return Container(
      padding: const EdgeInsets.all(AppSpacing.lg),
      decoration: BoxDecoration(
        color: AppColors.surfaceContainerLowest,
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
            color: const Color(0x1A000000),
            offset: const Offset(0, 10),
            blurRadius: 40,
            spreadRadius: -15,
          ),
        ],
        border: Border.all(color: AppColors.outlineVariant.withValues(alpha: 0.25)),
      ),
      child: Row(
        children: [
          Stack(
            clipBehavior: Clip.none,
            children: [
              Container(
                width: 80,
                height: 80,
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(16),
                  color: AppColors.surfaceContainerHigh,
                  boxShadow: [BoxShadow(color: const Color(0x1A000000), offset: const Offset(0, 2), blurRadius: 8)],
                ),
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(16),
                  child: Center(child: Icon(Icons.person, size: 40, color: AppColors.onSurfaceVariant)),
                ),
              ),
              Positioned(
                bottom: -8,
                right: -8,
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: AppSpacing.sm + 2, vertical: AppSpacing.xs + 2),
                  decoration: BoxDecoration(
                    color: AppColors.secondaryContainer,
                    borderRadius: BorderRadius.circular(AppRadius.full),
                    border: Border.all(color: AppColors.surfaceContainerLowest, width: 1.5),
                    boxShadow: [BoxShadow(color: const Color(0x1A000000), offset: const Offset(0, 1), blurRadius: 4)],
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(Icons.star, size: 12, color: AppColors.onSecondaryContainer),
                      const SizedBox(width: 2),
                      Text(
                        badgeLabel,
                        style: textTheme.labelMedium?.copyWith(
                          color: AppColors.onSecondaryContainer,
                          fontWeight: FontWeight.w700,
                          fontSize: 10,
                          letterSpacing: 0.4,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(width: AppSpacing.lg),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(name, style: textTheme.headlineSmall?.copyWith(color: AppColors.onSurface, fontWeight: FontWeight.w600)),
                const SizedBox(height: AppSpacing.xs),
                Text(email, style: textTheme.bodyMedium?.copyWith(color: AppColors.outline)),
                const SizedBox(height: AppSpacing.sm),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: AppSpacing.sm, vertical: 2),
                  decoration: BoxDecoration(
                    color: AppColors.primary.withValues(alpha: 0.05),
                    borderRadius: BorderRadius.circular(AppRadius.lg),
                  ),
                  child: Text(
                    membershipTag,
                    style: textTheme.labelMedium?.copyWith(
                      color: AppColors.primary,
                      fontWeight: FontWeight.w700,
                      fontSize: 10,
                      letterSpacing: 0.8,
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

class _SectionTitle extends StatelessWidget {
  const _SectionTitle({required this.label});
  final String label;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(left: AppSpacing.xs),
      child: Text(
        label.toUpperCase(),
        style: Theme.of(context).textTheme.labelMedium?.copyWith(
          color: AppColors.outline,
          fontWeight: FontWeight.w500,
          letterSpacing: 1.5,
        ),
      ),
    );
  }
}

class _CardContainer extends StatelessWidget {
  const _CardContainer({required this.children});
  final List<Widget> children;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: AppColors.surfaceContainerLowest,
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
            color: const Color(0x1A000000),
            offset: const Offset(0, 10),
            blurRadius: 40,
            spreadRadius: -15,
          ),
        ],
        border: Border.all(color: AppColors.outlineVariant.withValues(alpha: 0.25)),
      ),
      child: Column(children: children),
    );
  }
}

class _MenuItem extends StatelessWidget {
  const _MenuItem({
    required this.icon,
    required this.iconBg,
    required this.iconColor,
    required this.title,
    required this.subtitle,
    required this.onTap,
  });
  final IconData icon;
  final Color iconBg;
  final Color iconColor;
  final String title;
  final String subtitle;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(24),
      child: Padding(
        padding: const EdgeInsets.all(AppSpacing.lg),
        child: Row(
          children: [
            Container(
              width: 44,
              height: 44,
              decoration: BoxDecoration(
                color: iconBg,
                borderRadius: BorderRadius.circular(16),
              ),
              child: Icon(icon, color: iconColor, size: 22),
            ),
            const SizedBox(width: AppSpacing.md),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(title, style: textTheme.bodyLarge?.copyWith(color: AppColors.onSurface, fontWeight: FontWeight.w600)),
                  const SizedBox(height: 2),
                  Text(subtitle, style: textTheme.labelMedium?.copyWith(color: AppColors.outline)),
                ],
              ),
            ),
            const Icon(Icons.chevron_right, color: AppColors.outline, size: 24),
          ],
        ),
      ),
    );
  }
}

class _Divider extends StatelessWidget {
  const _Divider();

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: AppSpacing.lg),
      height: 1,
      color: AppColors.outlineVariant.withValues(alpha: 0.3),
    );
  }
}
