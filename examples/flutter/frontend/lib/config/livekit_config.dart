import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:flutter/foundation.dart';

/// LiveKit configuration for Flutter app
class LiveKitConfig {
  // Static room name to ensure consistency throughout the session
  static String? _cachedRoomName;
  // Static participant name to ensure consistency throughout the session
  static String? _cachedParticipantName;
  
  // LiveKit server configuration - can be overridden by environment variables
  static String get serverUrl => 
      _getEnvVar('LIVEKIT_SERVER_URL') ?? 
      'wss://demo.livekit.cloud';  // Using demo server for testing
  
  // Token configuration
  // Option 1: Direct token (for testing) - can be overridden by environment variables
  static String? get directToken => 
      _getEnvVar('LIVEKIT_TOKEN');
  
  // Option 2: Token generation endpoint (recommended for production)
  static String? get tokenEndpoint => 
      _getEnvVar('LIVEKIT_TOKEN_ENDPOINT') ?? 
      'http://localhost:3000/token';
  
  // Room configuration - can be overridden by environment variables
  // Use cached room name to ensure consistency throughout the session
  static String get roomName {
    final envRoom = _getEnvVar('LIVEKIT_ROOM_NAME');
    if (envRoom != null && envRoom.isNotEmpty) {
      print('🏠 Using environment room name: $envRoom');
      return envRoom;
    }
    
    // Generate random room name only once and cache it
    // This ensures the same room name is used throughout the session
    if (_cachedRoomName == null) {
      _cachedRoomName = 'room-${_generateRandomString(12)}';
      print('🏠 Generated random room name: $_cachedRoomName');
    }
    
    return _cachedRoomName!;
  }
  
  static String get participantName {
    final envParticipant = _getEnvVar('LIVEKIT_PARTICIPANT_NAME');
    if (envParticipant != null && envParticipant.isNotEmpty) {
      print('👤 Using environment participant name: $envParticipant');
      return envParticipant;
    }
    
    // Generate random participant name only once and cache it
    // This ensures the same participant name is used throughout the session
    if (_cachedParticipantName == null) {
      final timestamp = DateTime.now().millisecondsSinceEpoch;
      final random = timestamp % 10000;
      _cachedParticipantName = 'user-$random';
      print('👤 Generated random participant name: $_cachedParticipantName');
    }
    
    return _cachedParticipantName!;
  }
  
  /// Get environment variable safely across platforms
  static String? _getEnvVar(String key) {
    try {
      if (kIsWeb) {
        // On web, try URL parameters first, then fallback to compile-time constants
        final urlValue = _getWebConfig(key);
        if (urlValue != null) return urlValue;
        
        // Fallback to compile-time constants for web
        return _getCompileTimeValue(key);
      } else {
        // On mobile/desktop, we can access environment variables
        return Platform.environment[key];
      }
    } catch (e) {
      // If there's any error, return null to use defaults
      return null;
    }
  }
  
  /// Get compile-time values (set during build)
  static String? _getCompileTimeValue(String key) {
    // These values can be set during build using --dart-define
    switch (key) {
      case 'LIVEKIT_SERVER_URL':
        return const String.fromEnvironment('LIVEKIT_SERVER_URL');
      case 'LIVEKIT_TOKEN_ENDPOINT':
        return const String.fromEnvironment('LIVEKIT_TOKEN_ENDPOINT');
      case 'LIVEKIT_TOKEN':
        return const String.fromEnvironment('LIVEKIT_TOKEN');
      case 'LIVEKIT_ROOM_NAME':
        return const String.fromEnvironment('LIVEKIT_ROOM_NAME');
      case 'LIVEKIT_PARTICIPANT_NAME':
        return const String.fromEnvironment('LIVEKIT_PARTICIPANT_NAME');
      default:
        return null;
    }
  }
  
  /// Get configuration from web sources (URL params or localStorage)
  static String? _getWebConfig(String key) {
    // Support both explicit env-style keys and friendly aliases.
    final params = Uri.base.queryParameters;
    
    // Debug: print URL parameters
    if (params.isNotEmpty) {
      print('🔍 Web URL Parameters: $params');
    }
    
    switch (key) {
      case 'LIVEKIT_SERVER_URL':
        return params['LIVEKIT_SERVER_URL'] ?? params['serverUrl'];
      case 'LIVEKIT_TOKEN_ENDPOINT':
        return params['LIVEKIT_TOKEN_ENDPOINT'] ?? params['tokenEndpoint'];
      case 'LIVEKIT_TOKEN':
        return params['LIVEKIT_TOKEN'] ?? params['token'];
      case 'LIVEKIT_ROOM_NAME':
        return params['LIVEKIT_ROOM_NAME'] ?? params['room'];
      case 'LIVEKIT_PARTICIPANT_NAME':
        return params['LIVEKIT_PARTICIPANT_NAME'] ?? params['participant'] ?? params['identity'];
      default:
        return params[key];
    }
  }
  
  // Media configuration
  static const bool enableCamera = true;
  static const bool enableMicrophone = true;
  static const bool enableSpeaker = true;
  
  // Video configuration
  static const int videoWidth = 1280;
  static const int videoHeight = 720;
  static const int videoFps = 30;
  static const int videoBitrate = 1000000; // 1 Mbps
  
  // Audio configuration
  static const int audioBitrate = 64000; // 64 kbps
  static const int audioSampleRate = 48000;
  static const int audioChannels = 1;
  
  // Connection configuration
  static const Duration connectionTimeout = Duration(minutes: 5);  // Increased to 5 minutes
  static const Duration reconnectionTimeout = Duration(seconds: 30);  // Increased to 30 seconds
  static const int maxReconnectionAttempts = 10;  // Increased retry attempts
  
  // Debug configuration
  static const bool enableDebugLogs = true;
  static const bool enableStats = true;
  
  /// Get the appropriate token for connection
  static Future<String> getToken() async {
    print('🔑 Getting token for room: $roomName, participant: $participantName');
    
    // 1. Try using direct token first
    if (directToken != null && directToken!.isNotEmpty) {
      print('🔑 Using direct token');
      return directToken!;
    }
    
    // 2. Try getting token from endpoint
    if (tokenEndpoint != null && tokenEndpoint!.isNotEmpty) {
      try {
        print('🔑 Using token endpoint: $tokenEndpoint');
        final token = await _generateTokenFromEndpoint();
        print('🔑 ✅ Token obtained successfully from endpoint');
        return token;
      } catch (e) {
        print('🔑 ❌ Token server failed: $e');
        print('🔑 ❌ Please ensure:');
        print('   1. Token server is running at: $tokenEndpoint');
        print('   2. CORS is properly configured');
        print('   3. LiveKit credentials are valid');
        print('   4. Backend .env file is properly configured');
        
        // Don't fall back to test token, throw error instead
        throw Exception(
          'Failed to get token from endpoint: $tokenEndpoint\n'
          'Error: $e\n\n'
          'Please either:\n'
          '1. Start the token server: cd backend && python token_server.py\n'
          '2. Provide a direct token via LIVEKIT_TOKEN environment variable\n'
          '3. Check backend/.env file has valid LIVEKIT_API_KEY and LIVEKIT_API_SECRET'
        );
      }
    }
    
    // 3. No token configuration found
    throw Exception(
      'No token configuration found.\n\n'
      'Please either:\n'
      '1. Set LIVEKIT_TOKEN_ENDPOINT environment variable (recommended)\n'
      '   Example: export LIVEKIT_TOKEN_ENDPOINT="http://localhost:3000/token"\n'
      '2. Set LIVEKIT_TOKEN environment variable (for testing only)\n'
      '   Example: export LIVEKIT_TOKEN="eyJhbGciOiJIUz..."\n'
      '3. Start the token server:\n'
      '   cd backend\n'
      '   python token_server.py\n\n'
      'See FLUTTER_ISSUES_ANALYSIS.md for detailed setup instructions.'
    );
  }
  
  /// Generate token from backend endpoint
  static Future<String> _generateTokenFromEndpoint() async {
    try {
      print('🔑 Requesting token for room: $roomName, participant: $participantName');
      print('🔑 Token endpoint: $tokenEndpoint');
      
      final response = await http.post(
        Uri.parse('$tokenEndpoint'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'room': roomName,
          'participant': participantName,
        }),
      );
      
      print('🔑 Token response status: ${response.statusCode}');
      print('🔑 Token response body: ${response.body}');
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        print('🔑 Token generated successfully for room: ${data['room']}');
        return data['token'];
      } else {
        throw Exception('HTTP ${response.statusCode}: ${response.body}');
      }
    } catch (e) {
      print('🔑 Token generation failed: $e');
      throw Exception('Failed to generate token: $e');
    }
  }
  
  /// Validate configuration
  static bool validate() {
    if (serverUrl.isEmpty) {
      return false;
    }
    
    if (directToken == null && tokenEndpoint == null) {
      return false;
    }
    
    if (roomName.isEmpty || participantName.isEmpty) {
      return false;
    }
    
    return true;
  }
  
  /// Generate random alphanumeric string
  static String _generateRandomString(int length) {
    const chars = 'abcdefghijklmnopqrstuvwxyz0123456789';
    final random = DateTime.now().millisecondsSinceEpoch;
    final buffer = StringBuffer();
    
    for (int i = 0; i < length; i++) {
      final index = (random + i * 7919) % chars.length; // Use prime number for better distribution
      buffer.write(chars[index]);
    }
    
    return buffer.toString();
  }
  
  /// Get configuration summary for debugging
  static Map<String, dynamic> getConfigSummary() {
    return {
      'serverUrl': serverUrl,
      'hasDirectToken': directToken != null && directToken!.isNotEmpty,
      'hasTokenEndpoint': tokenEndpoint != null && tokenEndpoint!.isNotEmpty,
      'roomName': roomName,
      'participantName': participantName,
      'enableCamera': enableCamera,
      'enableMicrophone': enableMicrophone,
      'videoResolution': '${videoWidth}x${videoHeight}',
      'videoFps': videoFps,
      'videoBitrate': videoBitrate,
      'audioBitrate': audioBitrate,
      'connectionTimeout': connectionTimeout.inSeconds,
      'maxReconnectionAttempts': maxReconnectionAttempts,
      'platform': kIsWeb ? 'web' : 'mobile/desktop',
      'environmentVariables': {
        'LIVEKIT_SERVER_URL': _getEnvVar('LIVEKIT_SERVER_URL'),
        'LIVEKIT_TOKEN': _getEnvVar('LIVEKIT_TOKEN') != null ? '***' : null,
        'LIVEKIT_TOKEN_ENDPOINT': _getEnvVar('LIVEKIT_TOKEN_ENDPOINT'),
        'LIVEKIT_ROOM_NAME': _getEnvVar('LIVEKIT_ROOM_NAME'),
        'LIVEKIT_PARTICIPANT_NAME': _getEnvVar('LIVEKIT_PARTICIPANT_NAME'),
      },
      'webParams': kIsWeb ? Uri.base.queryParameters : null,
      'compileTimeValues': kIsWeb ? {
        'LIVEKIT_SERVER_URL': _getCompileTimeValue('LIVEKIT_SERVER_URL'),
        'LIVEKIT_TOKEN_ENDPOINT': _getCompileTimeValue('LIVEKIT_TOKEN_ENDPOINT'),
        'LIVEKIT_ROOM_NAME': _getCompileTimeValue('LIVEKIT_ROOM_NAME'),
        'LIVEKIT_PARTICIPANT_NAME': _getCompileTimeValue('LIVEKIT_PARTICIPANT_NAME'),
      } : null,
    };
  }
}

