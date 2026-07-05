import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:reclamations_iscae/features/notes/providers/notes_provider.dart';
import 'package:reclamations_iscae/core/models/note.dart';

class NotesScreen extends ConsumerWidget {
  const NotesScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final notesState = ref.watch(notesProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Mes Notes'),
      ),
      body: RefreshIndicator(
        onRefresh: () => ref.read(notesProvider.notifier).loadNotes(),
        child: notesState.when(
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
          data: (noteList) {
            if (noteList == null || noteList.results.isEmpty) {
              return const Center(
                child: Text('Aucune note trouvée.'),
              );
            }

            return ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: noteList.results.length,
              itemBuilder: (context, index) {
                final note = noteList.results[index];
                return NoteCard(note: note);
              },
            );
          },
        ),
      ),
    );
  }
}

class NoteCard extends StatelessWidget {
  final NoteElementaire note;

  const NoteCard({super.key, required this.note});

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        title: Text(
          note.libelleModule,
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        subtitle: Text('${note.codeModule}\n${note.semestre} - ${note.anneeAcademique}'),
        trailing: Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
          decoration: BoxDecoration(
            color: note.valeurNote >= note.noteSur / 2 ? Colors.green : Colors.red,
            borderRadius: BorderRadius.circular(8),
          ),
          child: Text(
            '${note.valeurNote}/${note.noteSur}',
            style: const TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        onTap: () {
          // Navigate to create reclamation for this note
          context.push('/reclamations/create/${note.id}?label=${Uri.encodeComponent("${note.libelleModule} - ${note.codeModule}")}');
        },
      ),
    );
  }
}