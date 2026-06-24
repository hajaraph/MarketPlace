# Architecture

Senior-grade Flutter scaffolding using **Feature-First + Clean Architecture**, **Riverpod**, **go_router** and a **Material 3** theme system whose design tokens are extracted from the original `code.html` design spec.

## Folder layout

```
lib/
  main.dart                          # Entry point: ProviderScope + MarketplaceApp
  app/
    app.dart                         # Root MaterialApp.router
    router/
      app_router.dart                # GoRouter + AppRoutes constants
    theme/
      app_colors.dart                # Material 3 color tokens (from spec)
      app_typography.dart            # Inter typography scale
      app_spacing.dart               # Spacing + border radius scales
      app_theme.dart                 # ThemeData composition
  core/
    errors/
      exceptions.dart                # Data-layer exceptions
      failures.dart                  # Domain-layer failures (Equatable)
    extensions/
      context_extensions.dart        # BuildContext sugar (theme/mq)
    utils/
      app_logger.dart                # Logger singleton
      validators.dart                # Reusable form validators
  features/
    auth/
      data/                          # (datasources / models / repositories impl)
      domain/
        entities/auth_user.dart
        repositories/auth_repository.dart
      presentation/
        pages/create_account_page.dart
        providers/create_account_controller.dart
        widgets/                     # Feature-scoped UI pieces
    home/
      presentation/
        pages/
          home_page.dart             # Shell with IndexedStack + AppNavBar
          explore_page.dart          # Tab 0 — Explore landing
          favorites_page.dart        # Tab 1 — Saved items
          orders_page.dart           # Tab 2 — Order history
          profile_page.dart          # Tab 3 — Account management
  shared/
    widgets/
      app_nav_bar.dart               # Bottom navbar (design spec extracted)
      app_text_field.dart            # Floating-label M3 text field
      primary_button.dart            # Filled primary CTA with brand shadow
      secondary_button.dart          # Outlined surface button (Google/Apple)
      labeled_divider.dart           # "OR" separator
```

## Conventions

- **State**: `StateNotifier` + `Provider` from `flutter_riverpod`. UI widgets read state via `ref.watch`, intents via `ref.read(provider.notifier)`.
- **Errors**: data layer throws `Exception`s, repositories convert them into `Either<Failure, T>` (dartz) at the domain boundary.
- **Routing**: typed route names in `AppRoutes`. Add new routes in `app_router.dart`.
- **Theming**: never hardcode colors/sizes in widgets. Always go through `AppColors` / `AppSpacing` / `AppRadius` / `Theme.of(context).textTheme`.
- **Widgets**: feature-specific widgets live under `features/<f>/presentation/widgets/`; cross-feature reusables live under `shared/widgets/`.

## Bootstrapping

```bash
flutter pub get
flutter run
```

## Implemented screens

`Create Account` (route: `/create-account`) faithfully reproduces the design spec from `code.html` (header, gradient, floating-label fields, primary CTA, social buttons, footer). Navigation to `Home` is triggered on successful submit.

`Home` (route: `/home`) hosts the bottom navigation bar extracted from the same spec:
- `Explore`, `Favorites`, `Orders`, `Profile` tabs managed by an `IndexedStack` so each tab preserves its own scroll position and state.
- Selected tab uses a tinted pill background (`primaryFixed` at 50 % opacity) and `primary` foreground.
- Unselected tabs use `outline` foreground with hover/transition feedback.

The auth flow intentionally keeps the bottom navigation bar hidden; it only appears once the user lands on `Home`.
