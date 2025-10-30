import 'package:flutter/material.dart';
import 'package:livekit_client/livekit_client.dart' as lk;

import '../theme/app_theme.dart';

/// Widget for displaying local video track (user's camera)
class LocalVideoView extends StatefulWidget {
  final lk.LocalVideoTrack track;
  final BoxFit fit;
  final bool mirror;

  const LocalVideoView({
    super.key,
    required this.track,
    this.fit = BoxFit.cover,
    this.mirror = true, // Mirror local video by default
  });

  @override
  State<LocalVideoView> createState() => _LocalVideoViewState();
}

class _LocalVideoViewState extends State<LocalVideoView> {
  @override
  Widget build(BuildContext context) {
    return _buildVideoRenderer();
  }

  Widget _buildVideoRenderer() {
    return Container(
      decoration: BoxDecoration(
        color: AppTheme.videoBackgroundColor,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: Colors.white.withOpacity(0.3),
          width: 2,
        ),
      ),
      child: Stack(
        children: [
          // LiveKit video renderer
          Positioned.fill(
            child: lk.VideoTrackRenderer(
              widget.track,
              fit: lk.VideoViewFit.contain,
            ),
          ),
          // Overlay with track info
          Positioned(
            bottom: 8,
            left: 8,
            right: 8,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: Colors.black54,
                borderRadius: BorderRadius.circular(4),
              ),
              child: Text(
                'You - ${widget.track.sid}',
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 12,
                ),
                textAlign: TextAlign.center,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
