// lib/src/client.dart

import 'dart:async';
import 'dart:convert';
import 'dart:developer';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter_client_sse/constants/sse_request_type_enum.dart';
import 'package:flutter_client_sse/flutter_client_sse.dart';
import 'models.dart';

// import 'dart:convert';
// import 'package:http/http.dart' as http;

class FeatureFlagClient {
  final String baseUrl;
  final String userId;
  final Map<String, dynamic> context;

  final Map<String, FeatureFlag> _flags = {};
  final Map<String, RemoteConfig> _configs = {};
  // Stores the last evaluated state to prevent telemetry spam
  final Map<String, bool> _lastTrackedValue = {};
  
  static const String _cacheKeyFlags = 'ff_client_cache_flags';
  static const String _cacheKeyConfigs = 'ff_client_cache_configs';

  // NEW: A stream controller to notify the Flutter UI when data changes
  final StreamController<void> _updateController = StreamController<void>.broadcast();
  Stream<void> get onUpdate => _updateController.stream;

  FeatureFlagClient({
    required this.baseUrl,
    required this.userId,
    this.context = const {},
  });

  /// Initializes the client by loading cached values from disk.
  Future<void> init() async {
    await _loadFromCache();
  }

  /// Evaluates current flags and configs from the FastAPI backend.
  Future<void> fetchAndCache() async {
    try {
      final url = Uri.parse('$baseUrl/evaluate');
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'user_id': userId,
          'context': context,
        }),
      ).timeout(const Duration(seconds: 5));

      if (response.statusCode == 200) {
        final Map<String, dynamic> data = jsonDecode(response.body);
        
        final Map<String, dynamic> flagsJson = data['flags'] ?? {};
        final Map<String, dynamic> configsJson = data['configs'] ?? {};

        _flags.clear();
        flagsJson.forEach((key, value) {
          _flags[key] = FeatureFlag.fromJson({'id': key, 'enabled': value});
        });

        _configs.clear();
        configsJson.forEach((key, value) {
          if (value is Map<String, dynamic>) {
            _configs[key] = RemoteConfig.fromJson({
              'id': key,
              'value': value['value'],
              'value_type': value['value_type']
            });
          } else {
            _configs[key] = RemoteConfig(id: key, value: value, valueType: 'string');
          }
        });

        await _saveToCache(flagsJson, configsJson);

        _updateController.add(null);
      }
    } catch (e) {
      log('FeatureFlagClient syncing failure: $e');
    }
  }

  // ==========================================
  // NEW: SSE Real-time Listener Logic
  // ==========================================

  /// Connects to the backend SSE stream to listen for real-time updates.
  void startListeningForUpdates() {
    final streamUrl = '$baseUrl/stream';
    
    SSEClient.subscribeToSSE(
      method: SSERequestType.GET,
      url: streamUrl,
      header: {'Accept': 'text/event-stream'},
    ).listen((event) async {
      if (event.data != null && event.data!.isNotEmpty && event.data != 'keep-alive') {
        log('SSE Update received from backend: ${event.data}');
        
        // When the backend says data changed, fetch the fresh rules for this user!
        await fetchAndCache();
        
        // Notify any Flutter widgets listening to redraw themselves
        _updateController.add(null);
      }
    }, onError: (error) {
      log('SSE Connection Error: $error');
    });
  }

  /// Clean up connections when the app closes
  void dispose() {
    SSEClient.unsubscribeFromSSE();
    _updateController.close();
  }

  // ==========================================
  // Data Accessors
  // ==========================================

  bool isEnabled(String flagId, {bool defaultValue = false}) {
    final flag = _flags[flagId];
    
    // 1. Only fire telemetry if we have real data from the server
    if (flag != null) {
      final currentValue = flag.enabled;
      
      // 2. Only fire if this is the first time we've seen it, OR if the TUI flipped the state
      if (_lastTrackedValue[flagId] != currentValue) {
        _trackEvaluation(flagId, currentValue);
        _lastTrackedValue[flagId] = currentValue; // Update our tracker
      }
      
      return currentValue;
    }
    
    // 3. If no data has arrived yet, return the safe default without tracking
    return defaultValue;
  }

  RemoteConfig? getConfig(String configId) {
    final config = _configs[configId];
    
    // 1. Only fire telemetry if we have real data from the server
    if (config != null) {
      final currentValue = config.asBool;
      
      // 2. Only fire if this is the first time we've seen it, OR if the TUI flipped the state
      if (_lastTrackedValue[configId] != currentValue) {
        _trackEvaluation(configId, currentValue);
        _lastTrackedValue[configId] = currentValue; // Update our tracker
      }
    }
    
    return config;
  }

  // ==========================================
  // Local Cache Engine
  // ==========================================

  Future<void> _saveToCache(Map<String, dynamic> flags, Map<String, dynamic> configs) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_cacheKeyFlags, jsonEncode(flags));
    await prefs.setString(_cacheKeyConfigs, jsonEncode(configs));
  }

  Future<void> _loadFromCache() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final flagsStr = prefs.getString(_cacheKeyFlags);
      final configsStr = prefs.getString(_cacheKeyConfigs);

      if (flagsStr != null) {
        final Map<String, dynamic> flagsJson = jsonDecode(flagsStr);
        flagsJson.forEach((key, value) {
          _flags[key] = FeatureFlag.fromJson({'id': key, 'enabled': value});
        });
      }

      if (configsStr != null) {
        final Map<String, dynamic> configsJson = jsonDecode(configsStr);
        configsJson.forEach((key, value) {
          if (value is Map<String, dynamic>) {
            _configs[key] = RemoteConfig.fromJson({
              'id': key,
              'value': value['value'],
              'value_type': value['value_type']
            });
          } else {
            _configs[key] = RemoteConfig(id: key, value: value, valueType: 'string');
          }
        });
      }
    } catch (e) {
      log('Error reading from SharedPreferences storage engine: $e');
    }
  }

  Future<void> _trackEvaluation(String flagId, bool result) async {
    try {
      final url = Uri.parse('$baseUrl/flags/metrics'); // Adjust path if your router prefix is different
      
      // Fire and forget! We don't await this in the main UI thread 
      // because we never want analytics to slow down the app.
      http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'user_id': userId,
          'flag_id': flagId,
          'evaluation_result': result,
          'timestamp': DateTime.now().toUtc().toIso8601String(),
        }),
      );
    } catch (e) {
      // Silently swallow analytics errors. Analytics should never crash the app.
      log('Telemetry failed to send: $e');
    }
  }
}