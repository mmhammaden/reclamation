import { Component, signal, inject } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { NotesService } from '../../../core/services/notes.service';
import { ResultatSemestre, Module, ElementModule } from '../../../core/models/note.model';
import { LoadingSpinnerComponent } from '../../../shared/components/loading-spinner/loading-spinner.component';

@Component({
  selector: 'app-mes-notes',
  standalone: true,
  imports: [LoadingSpinnerComponent, RouterLink],
  template: `
    <div class="max-w-5xl mx-auto">
      <div class="mb-6">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-bold text-gray-900">Mes Notes</h1>
            <p class="text-gray-500 mt-1">Consultez vos notes et soumettez une réclamation si nécessaire.</p>
          </div>
          <a routerLink="/etudiant/nouvelle-reclamation"
             class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm font-medium">
            + Créer une réclamation
          </a>
        </div>
      </div>

      @if (loading()) {
        <app-loading-spinner text="Chargement des notes..." />
      } @else if (error()) {
        <div class="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {{ error() }}
        </div>
      } @else if (resultats().length === 0) {
        <div class="text-center py-12 text-gray-500">
          <p class="text-lg">Aucune note trouvée.</p>
        </div>
      } @else {
        <div class="space-y-6">
          @for (resultat of resultats(); track resultat.id) {
            <div class="bg-white rounded-lg border border-gray-200 overflow-hidden">
              <!-- Semester Header -->
              <div class="p-4 border-b border-gray-200"
                   [class.bg-green-50]="resultat.observation === 'Validé'"
                   [class.border-green-200]="resultat.observation === 'Validé'"
                   [class.bg-red-50]="resultat.observation === 'Rattrapage'"
                   [class.border-red-200]="resultat.observation === 'Rattrapage'">
                <div class="flex items-center justify-between">
                  <div>
                    <h2 class="text-lg font-semibold text-gray-900">
                      {{ resultat.semestre }} - {{ resultat.annee_academique }}
                    </h2>
                    <p class="text-sm text-gray-500">
                      Moyenne générale: <span class="font-medium"
                        [class.text-green-600]="resultat.moy_semestre >= 10"
                        [class.text-red-600]="resultat.moy_semestre < 10">
                        {{ resultat.moy_semestre }}/20
                      </span>
                    </p>
                  </div>
                  <span class="px-3 py-1 rounded-full text-sm font-medium"
                        [class.bg-green-100]="resultat.observation === 'Validé'"
                        [class.text-green-800]="resultat.observation === 'Validé'"
                        [class.bg-red-100]="resultat.observation === 'Rattrapage'"
                        [class.text-red-800]="resultat.observation === 'Rattrapage'">
                    {{ resultat.observation }}
                  </span>
                </div>
              </div>

              <!-- Modules -->
              <div class="divide-y divide-gray-100">
                @for (module of resultat.modules; track module.id) {
                  <div class="p-4">
                    <div class="flex items-center justify-between mb-3">
                      <div>
                        <h3 class="font-medium text-gray-900">{{ module.nom_module || module.code_module }}</h3>
                        <p class="text-xs text-gray-500">{{ module.code_module }}</p>
                      </div>
                      <div class="text-right">
                        <span class="text-lg font-bold"
                              [class.text-green-600]="module.moy_module >= 10"
                              [class.text-red-600]="module.moy_module < 10">
                          {{ module.moy_module }}/20
                        </span>
                        <span class="text-xs text-gray-400 block">Crédit: {{ module.credit }}</span>
                        <span class="text-xs px-2 py-0.5 rounded"
                              [class.bg-green-100]="module.observation === 'Validé'"
                              [class.text-green-800]="module.observation === 'Validé'"
                              [class.bg-red-100]="module.observation === 'Rattrapage'"
                              [class.text-red-800]="module.observation === 'Rattrapage'">
                          {{ module.observation }}
                        </span>
                      </div>
                    </div>

                    <!-- Elements -->
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-2 ml-4">
                      @for (element of module.elements; track element.id) {
                        <div class="flex items-center justify-between p-2 bg-gray-50 rounded cursor-pointer hover:bg-gray-100 transition-colors"
                             (click)="onCreateReclamation(element)">
                          <div>
                            <p class="text-sm font-medium text-gray-800">{{ element.nom_element || element.code_element }}</p>
                            <p class="text-xs text-gray-500">{{ element.code_element }}</p>
                            <p class="text-xs text-gray-500">
                              CC: {{ element.note_continu }} | Exam: {{ element.note_final }}
                            </p>
                          </div>
                          <div class="text-right">
                            <span class="text-sm font-bold"
                                  [class.text-green-600]="element.note_moyenne >= 10"
                                  [class.text-red-600]="element.note_moyenne < 10">
                              {{ element.note_moyenne }}
                            </span>
                            <span class="text-xs block"
                                  [class.text-green-600]="element.observation === 'Validé'"
                                  [class.text-red-600]="element.observation === 'Rattrapage'">
                              {{ element.observation }}
                            </span>
                          </div>
                        </div>
                      }
                    </div>
                  </div>
                }
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
  private router = inject(Router);
  resultats = signal<ResultatSemestre[]>([]);
  loading = signal(true);
  error = signal('');

  constructor() {
    this.loadNotes();
  }

  onCreateReclamation(element: ElementModule): void {
    this.router.navigate(['/etudiant/nouvelle-reclamation'], {
      queryParams: { elementId: element.id.toString() }
    });
  }

  private loadNotes(): void {
    this.notesService.getNotes().subscribe({
      next: (response) => {
        this.resultats.set(response.results);
        this.loading.set(false);
      },
      error: () => {
        this.error.set('Erreur lors du chargement des notes.');
        this.loading.set(false);
      },
    });
  }
}