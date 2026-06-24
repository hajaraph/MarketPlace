import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:marketplace_maps/app/app.dart';

void main() {
  testWidgets('Create Account screen renders heading and CTA',
      (WidgetTester tester) async {
    await tester.pumpWidget(const ProviderScope(child: MarketplaceApp()));
    await tester.pumpAndSettle();

    expect(find.text('Create Account'), findsOneWidget);
    expect(find.text('Continue'), findsOneWidget);
    expect(find.text('Continue with Google'), findsOneWidget);
    expect(find.text('Continue with Apple'), findsOneWidget);
  });
}
