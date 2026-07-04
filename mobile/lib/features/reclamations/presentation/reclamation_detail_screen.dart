import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:reclamations_iscae/features/reclamations/providers/reclamation_detail_provider.dart';
import 'package:reclamations_iscae/core/models/reclamation.dart';

class ReclamationDetailScreen extends ConsumerWidget {
  final int reclamationId;

  const ReclamationDetailScreen({super.key, required this.reclamationId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final detailState = ref.watch(reclamationDetailProvider);

    // Load reclamation when screen opens
    ref.listen<AsyncValue<ReclamationDetail?>>(reclamationDetailProvider, (previous, next) {
      if (next.value == null && previous?.value == null) {
        ref.read(reclamationDetailProvider.notifier).loadReclamation(reclamationId);
      }
    });

    return Scaffold(
      appBar: AppBar(
        title: const Text('Détail Réclamation'),
      ),
      body: detailState.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, _) => Center(
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Text(
              'Erreur: $error',
              style: const TextStyle(color: Colors.red),
              textAlign: TextAlign.center,
            ),
          ),
        ),
        data: (reclamation) {
          if (reclamation == null) {
            return const Center(child: Text('Chargement...'));
          }

          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Réclamation #${reclamation.id}',
                          style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                        ),
                        const SizedBox(height: 16),
                        _buildInfoRow('Motif', _motifLabel(reclamation.motif)),
                        _buildInfoRow('Statut', _statutLabel(reclamation.statut)),
                        _buildInfoRow('Note originale', reclamation.noteOriginale?.toString() ?? 'N/A'),
                        _buildInfoRow('Nouvelle note', reclamation.nouvelleNote?.toString() ?? 'N/A'),
                        const SizedBox(height: 16),
                        const Text(
                          'Description',
                          style: TextStyle(fontWeight: FontWeight.bold),
                        ),
                        const SizedBox(height: 8),
                        Text(reclamation.description),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 120,
            child: Text(
              label,
              style: const TextStyle(fontWeight: FontWeight.w500, color: Colors.grey),
            ),
          ),
          Expanded(child: Text(value)),
        ],
      ),
    );
  }

  String _motifLabel(MotifReclamation motif) {
    switch (motif) {
      case MotifReclamation.ERREUR_SAISIE:
        return 'Erreur de saisie';
      case MotifReclamation.OUBLI_NOTE:
        return 'Oubli de note';
      case MotifReclamation.VERIFICATION_COPIE:
        return 'Vérification de copie';
      case MotifReclamation.AUTRE:
        return 'Autre';
    }
  }

  String _statutLabel(StatutReclamation statut) {
    switch (statut) {
      case StatutReclamation.EN_ATTENTE:
        return 'En attente';
      case StatutReclamation.EN_COURS:
        return 'En cours';
      case StatutReclamation.ACCEPTEE:
        return 'Acceptée';
      case StatutReclamation.REJETEE:
        return 'Rejetée';
      case StatutReclamation.ARCHIVEE:
        return 'Archivée';
    }
  }
}