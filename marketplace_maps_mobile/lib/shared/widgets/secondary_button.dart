import 'package:flutter/material.dart';

import '../../app/theme/app_colors.dart';
import '../../app/theme/app_spacing.dart';

/// Outlined surface button used for secondary actions (e.g. social sign-in).
class SecondaryButton extends StatelessWidget {
  const SecondaryButton({
    super.key,
    required this.label,
    this.onPressed,
    this.leading,
    this.background = AppColors.surfaceContainerLowest,
    this.foreground = AppColors.onSurface,
    this.borderColor = AppColors.outlineVariant,
  });

  final String label;
  final VoidCallback? onPressed;
  final Widget? leading;
  final Color background;
  final Color foreground;
  final Color borderColor;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: double.infinity,
      height: 56,
      child: OutlinedButton(
        onPressed: onPressed,
        style: OutlinedButton.styleFrom(
          backgroundColor: background,
          foregroundColor: foreground,
          side: BorderSide(color: borderColor),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(AppRadius.xl2),
          ),
          textStyle: Theme.of(context).textTheme.labelLarge,
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            if (leading != null) ...[
              leading!,
              const SizedBox(width: AppSpacing.sm + 4),
            ],
            Text(label),
          ],
        ),
      ),
    );
  }
}
