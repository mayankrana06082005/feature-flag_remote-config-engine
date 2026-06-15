// lib/src/widgets.dart

import 'package:flutter/widgets.dart';
import 'client.dart';
import 'models.dart';

/// A Provider that injects the FeatureFlagClient into the Flutter widget tree.
/// We use InheritedWidget so your package doesn't force developers to install
/// heavy state management libraries like Provider or Riverpod.
class FeatureFlagProvider extends InheritedWidget {
  final FeatureFlagClient client;

  const FeatureFlagProvider({
    super.key,
    required this.client,
    required super.child,
  });

  /// Helper method to easily grab the client from anywhere in the app
  static FeatureFlagClient of(BuildContext context) {
    final provider = context.dependOnInheritedWidgetOfExactType<FeatureFlagProvider>();
    assert(provider != null, 'No FeatureFlagProvider found in context. Did you wrap your app in it?');
    return provider!.client;
  }

  @override
  bool updateShouldNotify(FeatureFlagProvider oldWidget) {
    return client != oldWidget.client;
  }
}

/// A smart builder that automatically rebuilds its UI when a specific flag changes.
class FlagBuilder extends StatelessWidget {
  final String flagId;
  final Widget Function(BuildContext context, bool isEnabled) builder;

  const FlagBuilder({
    super.key,
    required this.flagId,
    required this.builder,
  });

  @override
  Widget build(BuildContext context) {
    // 1. Grab the client from the Provider
    final client = FeatureFlagProvider.of(context);

    // 2. Wrap the UI in a StreamBuilder listening to our SSE updates
    return StreamBuilder<void>(
      stream: client.onUpdate,
      builder: (context, snapshot) {
        // 3. Every time the stream fires, fetch the latest boolean and redraw!
        final isEnabled = client.isEnabled(flagId);
        return builder(context, isEnabled);
      },
    );
  }
}

/// A smart builder for Remote Configs (strings, ints, floats)
class ConfigBuilder extends StatelessWidget {
  final String configId;
  final Widget Function(BuildContext context, RemoteConfig? config) builder;

  const ConfigBuilder({
    super.key,
    required this.configId,
    required this.builder,
  });

  @override
  Widget build(BuildContext context) {
    final client = FeatureFlagProvider.of(context);

    return StreamBuilder<void>(
      stream: client.onUpdate,
      builder: (context, snapshot) {
        final config = client.getConfig(configId);
        return builder(context, config);
      },
    );
  }
}