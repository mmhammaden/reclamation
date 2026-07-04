import 'package:flutter/material.dart';
import 'package:reclamations_iscae/core/models/reclamation.dart';

class StatusBadge extends StatelessWidget {
  final StatutReclamation statut;

  const StatusBadge({super.key, required this.statut});

  @override
  Widget build(BuildContext context) {
    Color color;
    String label;
    switch (statut) {
      case StatutReclamation.EN_ATTENTE:
        color = Colors.orange;
        label = 'En attente';
        break;
      case StatutReclamation.EN_COURS:
        color = Colors.blue;
        label = 'En cours';
        break;
      case StatutReclamation.ACCEPTEE:
        color = Colors.green;
        label = 'Acceptée';
        break;
      case StatutReclamation.REJETEE:
        color = Colors.red;
        label = 'Rejetée';
        break;
      case StatutReclamation.ARCHIVEE:
        color = Colors.grey;
        label = 'Archivée';
        break;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: color,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Text(
        label,
        style: const TextStyle(
          color: Colors.white,
          fontSize: 12,
          fontWeight: FontWeight.w500,
        ),
      ),
    );
  }
}