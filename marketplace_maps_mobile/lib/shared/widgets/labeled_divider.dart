import 'package:flutter/material.dart';

import '../../app/theme/app_colors.dart';
import '../../app/theme/app_spacing.dart';

/// Horizontal divider with a centered uppercase label, e.g. "OR".
class LabeledDivider extends StatelessWidget {
  const LabeledDivider({super.key, required this.label});

  final String label;

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        const Expanded(
          child: Divider(color: AppColors.outlineVariant, height: 1),
        ),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: AppSpacing.md),
          child: Text(
            label.toUpperCase(),
            style: Theme.of(context).textTheme.labelMedium?.copyWith(
                  color: AppColors.outline,
                  letterSpacing: 2,
                ),
          ),
        ),
        const Expanded(
          child: Divider(color: AppColors.outlineVariant, height: 1),
        ),
      ],
    );
  }
}
