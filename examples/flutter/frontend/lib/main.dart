import 'package:flutter/material.dart';
import 'package:livekit_client/livekit_client.dart' as lk;
import 'package:livekit_components/livekit_components.dart';
import 'package:logging/logging.dart';

import 'config/livekit_config.dart';

// Create logger instance
final _logger = Logger('BitHumanFlutter');

/// bitHuman Flutter Integration using LiveKit Components
/// 
/// This app demonstrates how to integrate Flutter with LiveKit and bitHuman AI avatars
/// using the official livekit_components package for a cleaner, production-ready implementation.
/// 
/// Architecture:
/// Flutter App (livekit_components) ←→ LiveKit Cloud ←→ Python Agent ←→ bitHuman Avatar
void main() {
  // Initialize logger (show info level and above)
  Logger.root.level = Level.INFO;
  Logger.root.onRecord.listen((record) {
    print('${record.level.name}: ${record.time}: ${record.message}');
  });
  
  runApp(const BitHumanFlutterApp());
}

class BitHumanFlutterApp extends StatelessWidget {
  const BitHumanFlutterApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'bitHuman Flutter Integration',
      theme: LiveKitTheme().buildThemeData(context),
      themeMode: ThemeMode.dark,
      home: const ConnectionScreen(),
      debugShowCheckedModeBanner: false,
    );
  }
}

/// Connection screen - handles token generation and room joining
class ConnectionScreen extends StatefulWidget {
  const ConnectionScreen({super.key});

  @override
  State<ConnectionScreen> createState() => _ConnectionScreenState();
}

class _ConnectionScreenState extends State<ConnectionScreen> {
  final Logger _logger = Logger('ConnectionScreen');
  bool _isConnecting = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    // Auto-connect on startup
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _connect();
    });
  }

  Future<void> _connect() async {
    setState(() {
      _isConnecting = true;
      _error = null;
    });

    try {
      // Get configuration
      final serverUrl = LiveKitConfig.serverUrl;
      final roomName = LiveKitConfig.roomName;
      final participantName = LiveKitConfig.participantName;
      
      _logger.info('Connecting to room: $roomName as $participantName');
      _logger.info('Server: $serverUrl');
      
      // Get token from token server
      final token = await LiveKitConfig.getToken();
      _logger.info('Token obtained successfully');
      
      if (!mounted) return;
      
      // Navigate to video room using LiveKit Components
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(
          builder: (_) => VideoRoomScreen(
            url: serverUrl,
            token: token,
            roomName: roomName,
          ),
        ),
      );
    } catch (e) {
      _logger.severe('Connection failed: $e');
      setState(() {
        _error = e.toString();
        _isConnecting = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF1a1a1a),
      body: Center(
        child: Container(
          constraints: const BoxConstraints(maxWidth: 400),
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // Logo
              Container(
                width: 100,
                height: 100,
                decoration: BoxDecoration(
                  color: Colors.blue,
                  borderRadius: BorderRadius.circular(20),
                ),
                child: const Icon(
                  Icons.smart_toy,
                  size: 60,
                  color: Colors.white,
                ),
              ),
              const SizedBox(height: 32),
              
              // Title
              const Text(
                'bitHuman AI Avatar',
                style: TextStyle(
                  fontSize: 28,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
              const SizedBox(height: 8),
              const Text(
                'Flutter Integration',
                style: TextStyle(
                  fontSize: 16,
                  color: Colors.white70,
                ),
              ),
              const SizedBox(height: 48),
              
              // Connection status
              if (_isConnecting)
                const Column(
                  children: [
                    SizedBox(
                      width: 48,
                      height: 48,
                      child: CircularProgressIndicator(
                        strokeWidth: 3,
                        valueColor: AlwaysStoppedAnimation<Color>(Colors.blue),
                      ),
                    ),
                    SizedBox(height: 16),
                    Text(
                      'Connecting to AI Avatar...',
                      style: TextStyle(
                        color: Colors.white70,
                        fontSize: 16,
                      ),
                    ),
                  ],
                ),
              
              // Error message
              if (_error != null) ...[
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.red.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: Colors.red),
                  ),
                  child: Column(
                    children: [
                      const Icon(Icons.error, color: Colors.red, size: 48),
                      const SizedBox(height: 16),
                      Text(
                        _error!,
                        style: const TextStyle(color: Colors.red),
                        textAlign: TextAlign.center,
                      ),
                      const SizedBox(height: 16),
                      ElevatedButton(
                        onPressed: _connect,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.blue,
                        ),
                        child: const Text('Retry'),
                      ),
                    ],
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

/// Video display widget that caches the video renderer to prevent re-rendering
class _VideoDisplayWidget extends StatefulWidget {
  final RoomContext roomCtx;
  
  const _VideoDisplayWidget({required this.roomCtx});
  
  @override
  State<_VideoDisplayWidget> createState() => _VideoDisplayWidgetState();
}

class _VideoDisplayWidgetState extends State<_VideoDisplayWidget> {
  lk.VideoTrackRenderer? _cachedVideoRenderer;
  String? _lastVideoTrackId;
  
  @override
  void initState() {
    super.initState();
    // Listen for track published events
    widget.roomCtx.room.addListener(_onRoomChanged);
  }
  
  @override
  void dispose() {
    widget.roomCtx.room.removeListener(_onRoomChanged);
    super.dispose();
  }
  
  void _onRoomChanged() {
    // Force rebuild when room state changes (e.g., new tracks published)
    if (mounted) {
      setState(() {});
    }
  }
  
  @override
  Widget build(BuildContext context) {
    // Get remote participants
    final remoteParticipants = widget.roomCtx.room.remoteParticipants.values.toList();
    
    if (remoteParticipants.isEmpty) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularProgressIndicator(
              valueColor: AlwaysStoppedAnimation<Color>(Colors.blue),
            ),
            SizedBox(height: 16),
            Text(
              'Waiting for AI Avatar to join...',
              style: TextStyle(color: Colors.white70, fontSize: 16),
            ),
            SizedBox(height: 8),
            Text(
              'Make sure the backend agent is running',
              style: TextStyle(color: Colors.white54, fontSize: 12),
            ),
          ],
        ),
      );
    }
    
    // Find the first remote participant with video
    for (final participant in remoteParticipants) {
      _logger.fine('🔍 Checking participant: ${participant.identity}');
      _logger.fine('   Video tracks count: ${participant.videoTrackPublications.length}');
      
      // Check all video tracks, not just subscribed ones
      final videoTracks = participant.videoTrackPublications
          .where((pub) => pub.track != null)
          .toList();
      
      _logger.fine('   Available video tracks: ${videoTracks.length}');
      for (final pub in videoTracks) {
        _logger.fine('     Track: ${pub.sid}, enabled: ${pub.enabled}, subscribed: ${pub.subscribed}');
      }
      
      if (videoTracks.isNotEmpty) {
        final videoTrack = videoTracks.first.track as lk.VideoTrack;
        
        // Only recreate renderer if track ID changed
        if (_lastVideoTrackId != videoTrack.sid) {
          _logger.info('🎬 Creating new video renderer for ${participant.identity}');
          _cachedVideoRenderer = lk.VideoTrackRenderer(
            videoTrack,
            fit: lk.VideoViewFit.cover,
          );
          _lastVideoTrackId = videoTrack.sid;
        }
        
        return Container(
          color: Colors.black,
          child: _cachedVideoRenderer!,
        );
      }
    }
    
    return const Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.videocam_off,
            color: Colors.white54,
            size: 48,
          ),
          SizedBox(height: 16),
          Text(
            'AI Avatar connected but no video yet',
            style: TextStyle(color: Colors.white70, fontSize: 16),
          ),
          SizedBox(height: 8),
          Text(
            'Video will appear when AI starts speaking',
            style: TextStyle(color: Colors.white54, fontSize: 12),
          ),
        ],
      ),
    );
  }
}

/// Audio handler widget that manages audio without affecting video rendering
class _AudioHandlerWidget extends StatefulWidget {
  final RoomContext roomCtx;
  
  const _AudioHandlerWidget({required this.roomCtx});
  
  @override
  State<_AudioHandlerWidget> createState() => _AudioHandlerWidgetState();
}

class _AudioHandlerWidgetState extends State<_AudioHandlerWidget> {
  @override
  Widget build(BuildContext context) {
    // Get remote participants
    final remoteParticipants = widget.roomCtx.room.remoteParticipants.values.toList();
    
    for (final participant in remoteParticipants) {
      final audioTracks = participant.audioTrackPublications
          .where((pub) => pub.track != null && pub.subscribed)
          .toList();
      
      if (audioTracks.isNotEmpty) {
        _logger.fine('🔊 Audio track active for ${participant.identity}');
        // Audio is handled automatically by LiveKit Components
        // We just need to ensure the track is subscribed
        break;
      }
    }
    
    return const SizedBox.shrink();
  }
}


/// Loading overlay that shows only when no remote video is available
class _LoadingOverlay extends StatefulWidget {
  @override
  State<_LoadingOverlay> createState() => _LoadingOverlayState();
}

class _LoadingOverlayState extends State<_LoadingOverlay> {
  @override
  Widget build(BuildContext context) {
    // Get room context from LivekitRoom
    final roomContext = RoomContext.of(context);
    
    // Check if room context exists and has remote participants with video
    if (roomContext != null) {
      final remoteParticipants = roomContext.room.remoteParticipants.values;
      
      // Only log when state changes
      if (remoteParticipants.length != _lastParticipantCount) {
        _logger.fine('🔍 Loading overlay: ${remoteParticipants.length} remote participants');
        _lastParticipantCount = remoteParticipants.length;
      }
      
      final hasRemoteVideo = remoteParticipants.any((participant) {
        return participant.videoTrackPublications.isNotEmpty;
      });
      
      // If we have remote video, don't show loading
      if (hasRemoteVideo) {
        return const SizedBox.shrink();
      }
    }
    
    // Show loading indicator
    return Container(
      color: Colors.black,
      child: const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularProgressIndicator(
              valueColor: AlwaysStoppedAnimation<Color>(Colors.blue),
            ),
            SizedBox(height: 16),
            Text(
              'Waiting for AI Avatar...',
              style: TextStyle(color: Colors.white70, fontSize: 16),
            ),
          ],
        ),
      ),
    );
  }
  
  int _lastParticipantCount = 0;
}

/// Video room screen using LiveKit Components
class VideoRoomScreen extends StatelessWidget {
  final String url;
  final String token;
  final String roomName;

  const VideoRoomScreen({
    super.key,
    required this.url,
    required this.token,
    required this.roomName,
  });

  @override
  Widget build(BuildContext context) {
    // Use LiveKit Components' LivekitRoom widget
    return LivekitRoom(
      roomContext: RoomContext(
        url: url,
        token: token,
        connect: true,
        roomOptions: lk.RoomOptions(
          adaptiveStream: true,
          dynacast: true,
          // Enable microphone by default as per LiveKit docs
          defaultAudioPublishOptions: lk.AudioPublishOptions(
            dtx: true,
          ),
          defaultVideoPublishOptions: lk.VideoPublishOptions(
            simulcast: true,
          ),
        ),
      ),
      builder: (context, roomCtx) {
        // Enable microphone by default as per LiveKit docs
        WidgetsBinding.instance.addPostFrameCallback((_) {
          try {
            roomCtx.room.localParticipant?.setMicrophoneEnabled(true);
            _logger.fine('🎤 Microphone enabled by default');
          } catch (error) {
            _logger.warning('Could not enable microphone, error: $error');
          }
        });
        
        return Scaffold(
          appBar: AppBar(
            title: Text('Room: $roomName'),
            backgroundColor: const Color(0xFF1a1a1a),
            actions: [
              // Connection status indicator
              Padding(
                padding: const EdgeInsets.all(16),
                child: Row(
                  children: [
                    Icon(
                      roomCtx.room.connectionState == lk.ConnectionState.connected
                          ? Icons.circle
                          : Icons.circle_outlined,
                      color: roomCtx.room.connectionState == lk.ConnectionState.connected
                          ? Colors.green
                          : Colors.red,
                      size: 12,
                    ),
                    const SizedBox(width: 8),
                    Text(
                      roomCtx.room.connectionState.toString().split('.').last,
                      style: const TextStyle(fontSize: 12),
                    ),
                  ],
                ),
              ),
            ],
          ),
          backgroundColor: const Color(0xFF1a1a1a),
          body: Stack(
            children: [
              // Full-screen video for AI Avatar (remote participants only)
              Positioned.fill(
                child: Container(
                  color: Colors.black,
                  child: _VideoDisplayWidget(roomCtx: roomCtx),
                ),
              ),
              
              // Audio handling - separate from video to prevent re-rendering
              Positioned.fill(
                child: _AudioHandlerWidget(roomCtx: roomCtx),
              ),
              
              // Loading indicator overlay (only show when no remote video)
              Positioned.fill(
                child: _LoadingOverlay(),
              ),
              
              // Control bar at the bottom (floating over video)
              Positioned(
                left: 0,
                right: 0,
                bottom: 0,
                child: Container(
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      begin: Alignment.bottomCenter,
                      end: Alignment.topCenter,
                      colors: [
                        Colors.black.withOpacity(0.8),
                        Colors.transparent,
                      ],
                    ),
                  ),
                  padding: const EdgeInsets.only(bottom: 20, top: 40),
                  child: const ControlBar(),
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}
