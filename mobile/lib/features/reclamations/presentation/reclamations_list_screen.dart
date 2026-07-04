import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:reclamations_iscae/features/reclamations/providers/reclamations_provider.dart';

class ReclamationsListScreen extends ConsumerWidget {
  const ReclamationsListScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final reclamationsState = ref.watch(reclamationsProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Mes Réclamations'),
      ),
      body: RefreshIndicator(
        onRefresh: () => ref.read(reclamationsProvider.notifier).loadReclamations(),
        child: reclamationsState.when(
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
          data: (reclamations) {
            if (reclamations.isEmpty) {
              return const Center(
                child: Text('Aucune réclamation pour le moment.'),
              );
            }

            return ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: reclamations.length,
              itemBuilder: (context, index) {
                final rec = reclamations[index];
                return Card(
                  margin: const EdgeInsets.only(bottom: 12),
                  child: ListTile(
                    title: Text(
                      rec.codeModule,
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                    subtitle: Text(_motifLabel(rec.motif)),
                    trailing: _StatutBadge(statut: rec.statut),
                    onTap: () {
                      context.push('/reclamations/${rec.id}');
                    },
                  ),
                );
              },
            );
          },
        ),
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
}

class _StatutBadge extends StatelessWidget {
  final StatutReclamation statut;

  const _StatutBadge({required this.statut});

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
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Text(
        label,
        style: const TextStyle(color: Colors.white, fontSize: 12),
      ),
    );
  }
}