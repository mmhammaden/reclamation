import { Component, signal, inject } from '@angular/core';
import { NotesService } from '../../../core/services/notes.service';
import { NoteElementaire } from '../../../core/models/note.model';
import { LoadingSpinnerComponent } from '../../../shared/components/loading-spinner/loading-spinner.component';

@Component({
  selector: 'app-mes-notes',
  standalone: true,
  imports: [LoadingSpinnerComponent],
  template: `
    <div class="max-w-5xl mx-auto">
      <div class="mb-6">
        <h1 class="text-2xl font-bold text-gray-900">Mes Notes</h1>
        <p class="text-gray-500 mt-1">Consultez vos notes et soumettez une réclamation si nécessaire.</p>
      </div>

      @if (loading()) {
        <app-loading-spinner text="Chargement des notes..." />
      } @else if (error()) {
        <div class="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {{ error() }}
        </div>
      } @else if (notes().length === 0) {
        <div class="text-center py-12 text-gray-500">
          <p class="text-lg">Aucune note trouvée.</p>
        </div>
      } @else {
        <div class="grid gap-4">
          @for (note of notes(); track note.id) {
            <div class="bg-white rounded-lg border border-gray-200 p-5 hover:shadow-md transition-shadow">
              <div class="flex items-center justify-between">
                <div class="flex-1">
                  <h3 class="font-semibold text-gray-900">{{ note.libelle_module }}</h3>
                  <p class="text-sm text-gray-500">{{ note.code_module }}</p>
                  <p class="text-xs text-gray-400 mt-1">
                    {{ note.semestre }} - {{ note.annee_academique }}
                  </p>
                </div>
                <div class="text-right ml-4">
                  <span class="text-2xl font-bold"
                        [class.text-green-600]="note.valeur_note >= 10"
                        [class.text-red-600]="note.valeur_note < 10">
                    {{ note.valeur_note }}
                  </span>
                  <span class="text-gray-400">/{{ note.note_sur }}</span>
                </div>
              </div>
            </div>
          }
        </div>
      }
    </div>
  `,
})
export class MesNotesComponent {
  private notesService = inject(NotesService);
  notes = signal<NoteElementaire[]>([]);
  loading = signal(true);
  error = signal('');

  constructor() {
    this.loadNotes();
  }

  private loadNotes(): void {
    this.notesService.getNotes().subscribe({
      next: (response) => {
        this.notes.set(response.results);
        this.loading.set(false);
      },
      error: () => {
        this.error.set('Erreur lors du chargement des notes.');
        this.loading.set(false);
      },
    });
  }
}