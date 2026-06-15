import 'package:flutter/material.dart';
import 'package:feature_flag_client/feature_flag_client.dart';

void main() async {
  // Required so Flutter can use SharedPreferences before the app starts
  WidgetsFlutterBinding.ensureInitialized();

  // 1. Initialize your custom client
  final client = FeatureFlagClient(
    baseUrl: 'http://localhost:8000',
    userId: 'user_123', 
    context: {
      //'beta_tester': true},
      'groups': []
    }
  );

  // 2. Load the cache instantly, then sync with Python in the background
  await client.init();
  client.fetchAndCache();

  // 3. Open the SSE radio channel to listen for TUI dashboard updates!
  client.startListeningForUpdates();

  // 4. Wrap the app in your custom Provider
  runApp(
    FeatureFlagProvider(
      client: client,
      child: const MyApp(),
    ),
  );
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    // 5. Use FlagBuilder to dynamically change the theme based on your backend
    return FlagBuilder(
      flagId: 'dark_mode_beta',
      builder: (context, isDark) {
        return MaterialApp(
          debugShowCheckedModeBanner: false,
          title: 'Remote Config Demo',
          theme: isDark ? ThemeData.dark() : ThemeData.light(),
          home: const HomeScreen(),
        );
      },
    );
  }
}

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {

    final client = FeatureFlagProvider.of(context);

    final welcomeConfig = client.getConfig('welcome_message');
    final retriesConfig = client.getConfig('max_retries');
    final speedConfig = client.getConfig('animation_speed');

    // Unbox the values using your wrapper's getters
    final welcomeMsg = welcomeConfig?.asString;
    final retries = retriesConfig?.asInt;
    final speed = speedConfig?.asFloat;

    print('--- DATA TYPE TEST ---');
    print('Message: $welcomeMsg | Type: ${welcomeMsg.runtimeType}');
    print('Retries: $retries | Type: ${retries.runtimeType}');
    print('Speed: $speed | Type: ${speed.runtimeType}');
    print('----------------------');

    return Scaffold(
      appBar: AppBar(title: const Text('My Dynamic App')),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // 6. Use ConfigBuilder to pull the live welcome text
            ConfigBuilder(
              configId: 'welcome_message',
              builder: (context, config) {
                final message = config?.asString ?? 'Loading greeting...';
                return Text(
                  message,
                  style: const TextStyle(fontSize: 28, fontWeight: FontWeight.bold),
                );
              },
            ),
            
            const SizedBox(height: 40),
            
            // 7. Change button UI based on a feature flag
            FlagBuilder(
              flagId: 'new_checkout_flow',
              builder: (context, isEnabled) {
                if (isEnabled) {
                  return ElevatedButton.icon(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.green,
                      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 15),
                    ),
                    onPressed: () {},
                    icon: const Icon(Icons.shopping_cart, color: Colors.white),
                    label: const Text('NEW Checkout 2.0!', style: TextStyle(color: Colors.white)),
                  );
                }
                
                // Fallback UI if the flag is disabled
                return ElevatedButton(
                  onPressed: () {},
                  child: const Text('Standard Checkout'),
                );
              },
            ),
          ],
        ),
      ),
    );
  }
}