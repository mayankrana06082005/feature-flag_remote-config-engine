// lib/src/models.dart

class FeatureFlag {
  final String id;
  final bool enabled;

  FeatureFlag({required this.id, required this.enabled});

  factory FeatureFlag.fromJson(Map<String, dynamic> json) {
    return FeatureFlag(
      id: json['id'] as String,
      enabled: json['enabled'] as bool,
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'enabled': enabled,
  };
}

class RemoteConfig {
  final String id;
  final dynamic value;
  final String valueType;

  

  RemoteConfig({
    required this.id,
    required this.value,
    required this.valueType,
  });

  factory RemoteConfig.fromJson(Map<String, dynamic> json) {
    return RemoteConfig(
      id: json['id'] as String,
      value: json['value'],
      valueType: json['value_type'] as String,
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'value': value,
    'value_type': valueType,
  };

  // Helper methods to safely cast the value based on what your Python backend sent
  String get asString => value.toString();
  int get asInt => value is int ? value : int.tryParse(value.toString()) ?? 0;
  double get asFloat => value is double ? value : double.tryParse(value.toString()) ?? 0.0;
  bool get asBool {
    if (value is bool) return value;
    return value.toString().toLowerCase() == 'true';
  }
}