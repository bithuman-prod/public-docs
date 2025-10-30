import 'package:flutter/material.dart';

import '../theme/app_theme.dart';

/// Widget for media controls (mute, camera, speaker, etc.)
class MediaControls extends StatelessWidget {
  final bool isMicrophoneEnabled;
  final bool isCameraEnabled;
  final bool isSpeakerEnabled;
  final bool canSwitchCamera;
  final VoidCallback onMicrophoneToggle;
  final VoidCallback onCameraToggle;
  final VoidCallback onSpeakerToggle;
  final VoidCallback onCameraSwitch;
  final VoidCallback onDisconnect;

  const MediaControls({
    super.key,
    required this.isMicrophoneEnabled,
    required this.isCameraEnabled,
    required this.isSpeakerEnabled,
    required this.canSwitchCamera,
    required this.onMicrophoneToggle,
    required this.onCameraToggle,
    required this.onSpeakerToggle,
    required this.onCameraSwitch,
    required this.onDisconnect,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
      children: [
        // Microphone toggle
        _buildControlButton(
          icon: isMicrophoneEnabled ? Icons.mic : Icons.mic_off,
          isActive: isMicrophoneEnabled,
          onPressed: onMicrophoneToggle,
          tooltip: isMicrophoneEnabled ? 'Mute microphone' : 'Unmute microphone',
        ),
        
        // Camera toggle
        _buildControlButton(
          icon: isCameraEnabled ? Icons.videocam : Icons.videocam_off,
          isActive: isCameraEnabled,
          onPressed: onCameraToggle,
          tooltip: isCameraEnabled ? 'Turn off camera' : 'Turn on camera',
        ),
        
        // Camera switch (if available)
        if (canSwitchCamera)
          _buildControlButton(
            icon: Icons.switch_camera,
            isActive: false,
            onPressed: onCameraSwitch,
            tooltip: 'Switch camera',
          ),
        
        // Speaker toggle
        _buildControlButton(
          icon: isSpeakerEnabled ? Icons.volume_up : Icons.volume_off,
          isActive: isSpeakerEnabled,
          onPressed: onSpeakerToggle,
          tooltip: isSpeakerEnabled ? 'Turn off speaker' : 'Turn on speaker',
        ),
        
        // Disconnect button
        _buildControlButton(
          icon: Icons.call_end,
          isActive: false,
          isDestructive: true,
          onPressed: onDisconnect,
          tooltip: 'End call',
        ),
      ],
    );
  }

  Widget _buildControlButton({
    required IconData icon,
    required bool isActive,
    required VoidCallback onPressed,
    required String tooltip,
    bool isDestructive = false,
  }) {
    Color backgroundColor;
    Color iconColor;
    
    if (isDestructive) {
      backgroundColor = AppTheme.controlErrorColor;
      iconColor = Colors.white;
    } else if (isActive) {
      backgroundColor = AppTheme.controlActiveColor;
      iconColor = Colors.white;
    } else {
      backgroundColor = AppTheme.controlBackgroundColor;
      iconColor = AppTheme.controlIconColor;
    }

    return Tooltip(
      message: tooltip,
      child: GestureDetector(
        onTap: onPressed,
        child: Container(
          width: 56,
          height: 56,
          decoration: BoxDecoration(
            color: backgroundColor,
            shape: BoxShape.circle,
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.3),
                blurRadius: 8,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          child: Icon(
            icon,
            color: iconColor,
            size: 24,
          ),
        ),
      ),
    );
  }
}
