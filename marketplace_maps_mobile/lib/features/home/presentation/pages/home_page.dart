import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../shared/widgets/app_nav_bar.dart';
import 'explore_page.dart';
import 'favorites_page.dart';
import 'orders_page.dart';
import 'profile_page.dart';

/// Current tab index exposed as a plain auto-dispose provider.
final navBarIndexProvider = StateProvider.autoDispose<int>((ref) => 0);

/// Main application shell that hosts the bottom navigation bar.
///
/// The body is an [IndexedStack] so that tab state is preserved across
/// tab switches.
class HomePage extends ConsumerWidget {
  const HomePage({super.key});

  static const List<Widget> _tabs = [
    ExplorePage(),
    FavoritesPage(),
    OrdersPage(),
    ProfilePage(),
  ];

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final currentIndex = ref.watch(navBarIndexProvider);

    return Scaffold(
      body: IndexedStack(
        index: currentIndex,
        children: _tabs,
      ),
      bottomNavigationBar: AppNavBar(
        currentIndex: currentIndex,
        onTap: (index) => ref.read(navBarIndexProvider.notifier).state = index,
      ),
    );
  }
}
