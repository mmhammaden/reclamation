import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:reclamations_iscae/features/reclamations/providers/reclamations_provider.dart';
import 'package:reclamations_iscae/core/models/reclamation.dart';

class CreateReclamationScreen extends ConsumerStatefulWidget {
  final int noteId;
  final String noteLabel;

  const CreateReclamationScreen({
    super.key,
    required this.noteId,
    required this.noteLabel,
  });

  @override
  ConsumerState<CreateReclamationScreen> createState() => _CreateReclamationScreenState();
}

class _CreateReclamationScreenState extends ConsumerState<CreateReclamationScreen> {
  final _formKey = GlobalKey<FormState>();
  MotifReclamation _motif = MotifReclamation.AUTRE;
  final _descriptionController = TextEditingController();
  bool _isSubmitting = false;

  @override
  void dispose() {
    _descriptionController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isSubmitting = true);

    try {
      final request = ReclamationCreate(
        motif: _motif,
        description: _descriptionController.text.trim(),
        noteElementaire: widget.noteId,
      );

      await ref.read(reclamationsProvider.notifier).createReclamation(request);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Réclamation soumise avec succès!')),
        );
        Navigator.pop(context);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Erreur: $e')),
        );
      }
    } finally {
      setState(() => _isSubmitting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Nouvelle Réclamation'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: ListView(
            children: [
              Text(
                'Note: ${widget.noteLabel}',
                style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w500),
              ),
              const SizedBox(height: 24),
              DropdownButtonFormField<MotifReclamation>(
                value: _motif,
                decoration: const InputDecoration(
                  labelText: 'Motif',
                  border: OutlineInputBorder(),
                ),
                items: MotifReclamation.values.map((motif) {
                  return DropdownMenuItem(
                    value: motif,
                    child: Text(_motifLabel(motif)),
                  );
                }).toList(),
                onChanged: (value) {
                  if (value != null) {
                    setState(() => _motif = value);
                  }
                },
                validator: (value) => value == null ? 'Veuillez sélectionner un motif' : null,
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _descriptionController,
                maxLines: 5,
                decoration: const InputDecoration(
                  labelText: 'Description',
                  border: OutlineInputBorder(),
                ),
                validator: (value) =>
                    value?.isEmpty ?? true ? 'Veuillez entrer une description' : null,
              ),
              const SizedBox(height: 24),
              _isSubmitting
                  ? const Center(child: CircularProgressIndicator())
                  : ElevatedButton(
                      onPressed: _submit,
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 16),
                      ),
                      child: const Text('Soumettre'),
                    ),
            ],
          ),
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