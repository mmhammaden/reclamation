import { Component, signal, inject, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink, ActivatedRoute } from '@angular/router';
import { ReclamationsService } from '../../../core/services/reclamations.service';
import { NotesService } from '../../../core/services/notes.service';
import { MotifReclamation, LigneReclamationCreate } from '../../../core/models/reclamation.model';
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
        <p class="text-gray-500 mt-1">Ajoutez une ou plusieurs matières à réclamation.</p>
      </div>

      @if (success()) {
        <div class="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg text-green-700">
          <p class="font-medium mb-2">Réclamation soumise avec succès !</p>
          <p class="text-sm">Votre réclamation sera traitée dans les 72 heures ouvrées.</p>
          <a routerLink="/etudiant/mes-reclamations" class="underline ml-2">Voir mes réclamations</a>
        </div>
      }

      @if (error()) {
        <div class="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">{{ error() }}</div>
      }

      @if (!success()) {
        <form (ngSubmit)="onSubmit()" class="bg-white rounded-lg border border-gray-200 p-6 space-y-5">

          <!-- Description globale -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Description générale (optionnel)</label>
            <textarea [(ngModel)]="description" name="description" rows="3"
                      class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none resize-none"
                      placeholder="Contexte général de votre réclamation..."></textarea>
          </div>

          <!-- Lignes de matières -->
          <div>
            <div class="flex items-center justify-between mb-3">
              <label class="block text-sm font-medium text-gray-700">Matières concernées *</label>
              <button type="button" (click)="ajouterLigne()"
                      class="text-sm text-primary-600 hover:text-primary-700 font-medium">
                + Ajouter une matière
              </button>
            </div>

            @for (ligne of lignes; track $index; let i = $index) {
              <div class="mb-4 p-4 bg-gray-50 rounded-lg border border-gray-200 space-y-3">
                <div class="grid grid-cols-12 gap-3">
                  <div class="col-span-6">
                    <label class="block text-xs font-medium text-gray-600 mb-1">Matière *</label>
                    <select [(ngModel)]="lignes[i].note_elementaire"
                            name="note_{{i}}"
                            class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 outline-none"
                            required>
                      <option value="">Sélectionnez une note</option>
                      @for (note of notes(); track note.id) {
                        <option [value]="note.id">
                          {{ note.nom_module }} ({{ note.code_module }}) - {{ note.valeur_note }}/{{ note.note_sur }}
                        </option>
                      }
                    </select>
                  </div>
                  <div class="col-span-5">
                    <label class="block text-xs font-medium text-gray-600 mb-1">Motif *</label>
                    <select [(ngModel)]="lignes[i].motif"
                            name="motif_{{i}}"
                            class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 outline-none"
                            required>
                      <option value="">Motif</option>
                      <option value="ERREUR_SAISIE">Erreur de saisie</option>
                      <option value="OUBLI_NOTE">Oubli de note</option>
                      <option value="VERIFICATION_COPIE">Vérification de copie</option>
                      <option value="AUTRE">Autre motif</option>
                    </select>
                  </div>
                  <div class="col-span-1 flex items-end justify-center pb-1">
                    @if (lignes.length > 1) {
                      <button type="button" (click)="supprimerLigne(i)" class="text-red-500 hover:text-red-700 text-sm">✕</button>
                    }
                  </div>
                </div>
                <div>
                  <label class="block text-xs font-medium text-gray-600 mb-1">Description (optionnel)</label>
                  <textarea [(ngModel)]="lignes[i].description"
                            name="desc_{{i}}" rows="2"
                            class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 outline-none resize-none"
                            placeholder="Décrivez le problème pour cette matière..."></textarea>
                </div>
                <div>
                  <label class="block text-xs font-medium text-gray-600 mb-1">Pièce jointe (optionnel)</label>
                  <input type="file" multiple accept=".pdf,.png,.jpg,.jpeg"
                         (change)="onLigneFichiers($event, i)"
                         class="w-full text-sm text-gray-500 file:mr-3 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-medium file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100" />
                  @if (lignes[i].fichiers?.length) {
                    <p class="mt-1 text-xs text-gray-400">{{ lignes[i].fichiers!.length }} fichier(s)</p>
                  }
                </div>
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
  lignes: LigneReclamationCreate[] = [{ note_elementaire: 0, motif: MotifReclamation.ERREUR_SAISIE, description: '', fichiers: [] }];
  description = '';
  submitting = signal(false);
  success = signal(false);
  error = signal('');

  ngOnInit(): void {
    // Get noteId from query params if available
    const noteId = this.route.snapshot.queryParams['noteId'];
    if (noteId) {
      this.lignes = [{ note_elementaire: Number(noteId), motif: MotifReclamation.ERREUR_SAISIE, description: '', fichiers: [] }];
    }
    this.loadNotes();
  }

  ajouterLigne(): void {
    this.lignes.push({ note_elementaire: 0, motif: MotifReclamation.ERREUR_SAISIE, description: '', fichiers: [] });
  }

  supprimerLigne(index: number): void {
    this.lignes.splice(index, 1);
  }

  onLigneFichiers(event: Event, index: number): void {
    const input = event.target as HTMLInputElement;
    if (input.files) {
      this.lignes[index].fichiers = Array.from(input.files);
    }
  }

  onSubmit(): void {
    // Validate all lines have required fields (note_elementaire must be > 0)
    const invalidLine = this.lignes.find(l => !l.note_elementaire || l.note_elementaire === 0 || !l.motif);
    if (invalidLine) {
      this.error.set('Veuillez remplir tous les champs obligatoires pour chaque matière.');
      return;
    }

    this.submitting.set(true);
    this.error.set('');

    this.reclamationsService.createReclamation({
      description: this.description,
      lignes: this.lignes,
    }).subscribe({
      next: () => {
        this.submitting.set(false);
        this.success.set(true);
      },
      error: (err) => {
        this.submitting.set(false);
        if (err.error?.lignes) {
          this.error.set(err.error.lignes.join(' '));
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