import { Component, signal, inject, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink, ActivatedRoute } from '@angular/router';
import { ReclamationsService } from '../../../core/services/reclamations.service';
import { NotesService } from '../../../core/services/notes.service';
import { MotifReclamation } from '../../../core/models/reclamation.model';
import { NoteElementaire } from '../../../core/models/note.model';
import { LoadingSpinnerComponent } from '../../../shared/components/loading-spinner/loading-spinner.component';

@Component({
  selector: 'app-nouvelle-reclamation',
  standalone: true,
  imports: [FormsModule, RouterLink, LoadingSpinnerComponent],
  template: `
    <div class="max-w-3xl mx-auto">
      <div class="mb-6">
        <h1 class="text-2xl font-bold text-gray-900">Nouvelle Réclamation</h1>
        <p class="text-gray-500 mt-1">Soumettez une réclamation concernant une note.</p>
      </div>

      @if (success()) {
        <div class="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg text-green-700">
          <p class="font-medium mb-2">Réclamation soumise avec succès !</p>
          <p class="text-sm">Votre réclamation a été enregistrée et sera traitée dans les 72 heures ouvrées.</p>
          <a routerLink="/etudiant/mes-reclamations" class="underline ml-2">Voir mes réclamations</a>
        </div>
      }

      @if (error()) {
        <div class="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">{{ error() }}</div>
      }

      @if (!success()) {
        <form (ngSubmit)="onSubmit()" class="bg-white rounded-lg border border-gray-200 p-6 space-y-5">
          <!-- Note selection -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Note concernée</label>
            <select [(ngModel)]="selectedNoteId" name="note"
                    class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none"
                    required>
              <option value="">Sélectionnez une note</option>
              @for (note of notes(); track note.id) {
                <option [value]="note.id">
                  {{ note.libelle_module }} ({{ note.code_module }}) - {{ note.valeur_note }}/{{ note.note_sur }}
                </option>
              }
            </select>
          </div>

          <!-- Motif -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Motif</label>
            <select [(ngModel)]="motif" name="motif"
                    class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none"
                    required>
              <option value="">Sélectionnez un motif</option>
              <option value="ERREUR_SAISIE">Erreur de saisie</option>
              <option value="OUBLI_NOTE">Oubli de note</option>
              <option value="VERIFICATION_COPIE">Demande de vérification de copie</option>
              <option value="AUTRE">Autre motif</option>
            </select>
          </div>

          <!-- Description -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Description</label>
            <textarea [(ngModel)]="description" name="description" rows="4"
                      class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none resize-none"
                      placeholder="Décrivez votre réclamation..."></textarea>
          </div>

          <!-- File upload -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Pièces jointes (optionnel)</label>
            <input type="file" (change)="onFilesSelected($event)" multiple
                   accept=".pdf,.png,.jpg,.jpeg"
                   class="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100" />
            @if (selectedFiles().length > 0) {
              <div class="mt-2 text-sm text-gray-500">
                {{ selectedFiles().length }} fichier(s) sélectionné(s)
              </div>
            }
          </div>

          <!-- Submit -->
          <div class="flex items-center gap-3 pt-2">
            <button type="submit" [disabled]="submitting()"
                    class="px-6 py-2.5 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50">
              @if (submitting()) {
                <app-loading-spinner size="sm" containerClass="py-0" color="white" />
              } @else {
                Soumettre la réclamation
              }
            </button>
            <a routerLink="/etudiant/mes-reclamations"
               class="px-6 py-2.5 text-gray-700 hover:text-gray-900 transition-colors">
              Annuler
            </a>
          </div>
        </form>
      }
    </div>
  `,
})
export class NouvelleReclamationComponent implements OnInit {
  private reclamationsService = inject(ReclamationsService);
  private notesService = inject(NotesService);
  private router = inject(Router);
  private route = inject(ActivatedRoute);

  notes = signal<NoteElementaire[]>([]);
  selectedNoteId = '';
  motif = '';
  description = '';
  selectedFiles = signal<File[]>([]);
  submitting = signal(false);
  success = signal(false);
  error = signal('');

  ngOnInit(): void {
    // Get noteId from query params if available
    const noteId = this.route.snapshot.queryParams['noteId'];
    if (noteId) {
      this.selectedNoteId = noteId;
    }
    this.loadNotes();
  }

  onFilesSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files) {
      this.selectedFiles.set(Array.from(input.files));
    }
  }

  onSubmit(): void {
    if (!this.selectedNoteId || !this.motif) {
      this.error.set('Veuillez remplir tous les champs obligatoires.');
      return;
    }

    this.submitting.set(true);
    this.error.set('');

    this.reclamationsService.createReclamation({
      motif: this.motif as MotifReclamation,
      description: this.description,
      note_elementaire: Number(this.selectedNoteId),
      pieces_jointes: this.selectedFiles().length > 0 ? this.selectedFiles() : undefined,
    }).subscribe({
      next: () => {
        this.submitting.set(false);
        this.success.set(true);
      },
      error: (err) => {
        this.submitting.set(false);
        if (err.error?.note_elementaire) {
          this.error.set(err.error.note_elementaire.join(' '));
        } else if (err.error?.detail) {
          this.error.set(err.error.detail);
        } else {
          this.error.set('Erreur lors de la soumission.');
        }
      },
    });
  }

  private loadNotes(): void {
    this.notesService.getNotes().subscribe({
      next: (response) => this.notes.set(response.results),
    });
  }
}