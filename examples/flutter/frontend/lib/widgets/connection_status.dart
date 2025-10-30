import 'package:flutter/material.dart';
import 'package:livekit_client/livekit_client.dart' as lk;

import '../theme/app_theme.dart';

/// Widget for displaying connection status
class ConnectionStatus extends StatelessWidget {
  final bool isConnected;
  final bool isConnecting;
  final lk.ConnectionState connectionState;
  final String? error;

  const ConnectionStatus({
    super.key,
    required this.isConnected,
    required this.isConnecting,
    required this.connectionState,
    this.error,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: _getStatusColor().withOpacity(0.9),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          _buildStatusIcon(),
          const SizedBox(width: 8),
          Text(
            _getStatusText(),
            style: const TextStyle(
              color: Colors.white,
              fontSize: 14,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatusIcon() {
    if (isConnecting) {
      return const SizedBox(
        width: 12,
        height: 12,
        child: CircularProgressIndicator(
          strokeWidth: 2,
          valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
        ),
      );
    }

    return Icon(
      _getStatusIconData(),
      size: 12,
      color: Colors.white,
    );
  }

  IconData _getStatusIconData() {
    if (error != null) {
      return Icons.error;
    } else if (isConnected) {
      return Icons.check_circle;
    } else {
      return Icons.circle;
    }
  }

  Color _getStatusColor() {
    if (error != null) {
      return AppTheme.controlErrorColor;
    } else if (isConnected) {
      return AppTheme.controlActiveColor;
    } else if (isConnecting) {
      return Colors.orange;
    } else {
      return AppTheme.controlInactiveColor;
    }
  }

  String _getStatusText() {
    if (error != null) {
      return 'Error';
    } else if (isConnecting) {
      return 'Connecting...';
    } else if (isConnected) {
      return 'Connected';
    } else {
      return 'Disconnected';
    }
  }
}
