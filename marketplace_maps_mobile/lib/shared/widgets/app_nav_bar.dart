import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../../app/theme/app_colors.dart';
import '../../app/theme/app_spacing.dart';

/// A highly creative "Floating Aurora" bottom navigation bar.
///
/// Features:
/// - Sliding fluid indicator with mesh-gradient-like effect.
/// - Icon scaling and morphing transitions.
/// - Haptic feedback integration.
/// - "Aurora" active indicator using primary/secondary blend.
class AppNavBar extends StatelessWidget {
  const AppNavBar({
    super.key,
    required this.currentIndex,
    required this.onTap,
  });

  final int currentIndex;
  final ValueChanged<int> onTap;

  static const List<_NavItemData> _items = [
    _NavItemData(
      label: 'Explorer',
      icon: Icons.explore_outlined,
      activeIcon: Icons.explore,
    ),
    _NavItemData(
      label: 'Favoris',
      icon: Icons.favorite_outline,
      activeIcon: Icons.favorite,
    ),
    _NavItemData(
      label: 'Commandes',
      icon: Icons.shopping_bag_outlined,
      activeIcon: Icons.shopping_bag,
    ),
    _NavItemData(
      label: 'Profil',
      icon: Icons.person_outline,
      activeIcon: Icons.person,
    ),
  ];

  @override
  Widget build(BuildContext context) {
    final double screenWidth = MediaQuery.of(context).size.width;
    final double horizontalPadding = AppSpacing.md;
    final double availableWidth = screenWidth - (horizontalPadding * 2);
    final double itemWidth = availableWidth / _items.length;

    return Container(
      decoration: const BoxDecoration(
        color: AppColors.surfaceContainerLowest,
        borderRadius: BorderRadius.only(
          topLeft: Radius.circular(32),
          topRight: Radius.circular(32),
        ),
        boxShadow: [
          BoxShadow(
            color: Color(0x0A000000),
            offset: Offset(0, -8),
            blurRadius: 30,
          ),
        ],
      ),
      child: SafeArea(
        child: Padding(
          padding: EdgeInsets.symmetric(
            horizontal: horizontalPadding,
            vertical: AppSpacing.sm,
          ),
          child: Stack(
            children: [
              // Fluid Indicator
              AnimatedPositioned(
                duration: const Duration(milliseconds: 400),
                curve: Curves.easeOutBack,
                left: currentIndex * itemWidth + (itemWidth * 0.1),
                top: 4,
                child: Container(
                  width: itemWidth * 0.8,
                  height: 40,
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      colors: [
                        AppColors.primary.withValues(alpha: 0.15),
                        AppColors.secondary.withValues(alpha: 0.1),
                      ],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                    borderRadius: BorderRadius.circular(20),
                  ),
                ),
              ),
              // Navigation Items
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: List.generate(_items.length, (index) {
                  final item = _items[index];
                  final isSelected = index == currentIndex;
                  return _NavBarItem(
                    data: item,
                    isSelected: isSelected,
                    width: itemWidth,
                    onTap: () {
                      if (!isSelected) {
                        HapticFeedback.mediumImpact();
                        onTap(index);
                      }
                    },
                  );
                }),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _NavItemData {
  const _NavItemData({
    required this.label,
    required this.icon,
    required this.activeIcon,
  });

  final String label;
  final IconData icon;
  final IconData activeIcon;
}

class _NavBarItem extends StatelessWidget {
  const _NavBarItem({
    required this.data,
    required this.isSelected,
    required this.width,
    required this.onTap,
  });

  final _NavItemData data;
  final bool isSelected;
  final double width;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: width,
      child: GestureDetector(
        onTap: onTap,
        behavior: HitTestBehavior.opaque,
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 4),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              AnimatedScale(
                scale: isSelected ? 1.2 : 1.0,
                duration: const Duration(milliseconds: 400),
                curve: Curves.easeOutBack,
                child: Icon(
                  isSelected ? data.activeIcon : data.icon,
                  color: isSelected ? AppColors.primary : AppColors.outline,
                  size: 24,
                ),
              ),
              const SizedBox(height: 4),
              AnimatedOpacity(
                opacity: isSelected ? 1.0 : 0.7,
                duration: const Duration(milliseconds: 200),
                child: Text(
                  data.label,
                  style: Theme.of(context).textTheme.labelSmall?.copyWith(
                        color: isSelected ? AppColors.primary : AppColors.outline,
                        fontWeight: isSelected ? FontWeight.bold : FontWeight.w500,
                        fontSize: 10,
                      ),
                ),
              ),
              const SizedBox(height: 2),
              // Active Dot
              AnimatedContainer(
                duration: const Duration(milliseconds: 300),
                width: isSelected ? 4 : 0,
                height: 4,
                decoration: const BoxDecoration(
                  color: AppColors.primary,
                  shape: BoxShape.circle,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
