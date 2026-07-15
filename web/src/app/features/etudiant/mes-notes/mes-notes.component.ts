import { Component, signal, inject, OnInit } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { NotesService } from '../../../core/services/notes.service';
import { AnneeAcademiqueService, AnneeAcademique } from '../../../core/services/annee-academique.service';
import { ResultatSemestre, ElementModule } from '../../../core/models/note.model';
import { LoadingSpinnerComponent } from '../../../shared/components/loading-spinner/loading-spinner.component';

@Component({
  selector: 'app-mes-notes',
  standalone: true,
  imports: [LoadingSpinnerComponent, RouterLink],
  template: `
    <div class="max-w-5xl mx-auto">
      <div class="flex items-center justify-between mb-6">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">Mes Notes</h1>
          <p class="text-gray-500 mt-1">Consultez vos notes et soumettez une réclamation si nécessaire.</p>
        </div>
        <a routerLink="/etudiant/nouvelle-reclamation"
           class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm font-medium">
          + Créer une réclamation
        </a>
      </div>

      @if (activeAnnee(); as annee) {
        <div class="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg text-sm text-blue-700">
          Notes pour l'année <strong>{{ annee.annee }}</strong>
        </div>
      }

      @if (loading()) {
        <app-loading-spinner text="Chargement des notes..." />
      } @else if (error()) {
        <div class="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">{{ error() }}</div>
      } @else if (resultats().length === 0) {
        <div class="text-center py-12 text-gray-500">
          <p class="text-lg">Aucune note trouvée.</p>
        </div>
      } @else {
        <div class="space-y-6">
          @for (resultat of resultats(); track resultat.id) {
            <div class="bg-white rounded-lg border border-gray-200 overflow-hidden">
              <!-- Elements table -->
              <table class="w-full text-sm">
                <thead class="bg-gray-50 text-xs text-gray-500 uppercase">
                  <tr>
                    <th class="text-left px-4 py-2">Matière</th>
                    <th class="text-left px-4 py-2">Code</th>
                    <th class="text-center px-4 py-2">CC</th>
                    <th class="text-center px-4 py-2">Examen</th>
                    <th class="text-center px-4 py-2">Moyenne</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-100">
                  @for (element of resultat.elements; track element.id) {
                    <tr class="hover:bg-gray-50 cursor-pointer" (click)="onCreateReclamation(element)">
                      <td class="px-4 py-2 text-gray-900">{{ element.nom_matiere || element.code_element }}</td>
                      <td class="px-4 py-2 text-gray-500">{{ element.code_element }}</td>
                      <td class="px-4 py-2 text-center text-gray-700">{{ element.note_continu }}</td>
                      <td class="px-4 py-2 text-center text-gray-700">{{ element.note_final }}</td>
                      <td class="px-4 py-2 text-center font-medium"
                          [class.text-green-600]="element.note_moyenne >= 10"
                          [class.text-red-600]="element.note_moyenne < 10">
                        {{ element.note_moyenne }}
                      </td>
                    </tr>
                  }
                </tbody>
              </table>
            </div>
          }
        </div>
      }
    </div>
  `,
})
export class MesNotesComponent implements OnInit {
  private notesService = inject(NotesService);
  private anneeService = inject(AnneeAcademiqueService);
  private router = inject(Router);
  resultats = signal<ResultatSemestre[]>([]);
  loading = signal(true);
  error = signal('');
  activeAnnee = signal<AnneeAcademique | null>(null);

  ngOnInit(): void {
    this.anneeService.getCurrent().subscribe({
      next: (annee) => {
        this.activeAnnee.set(annee);
        this.loadNotes(annee.annee);
      },
      error: () => {
        this.loadNotes();
      },
    });
  }

  onCreateReclamation(element: ElementModule): void {
    this.router.navigate(['/etudiant/nouvelle-reclamation'], {
      queryParams: { elementId: element.id.toString() }
    });
  }

  private loadNotes(annee?: string): void {
    const params: Record<string, string> = {};
    if (annee) {
      params['annee_academique'] = annee;
    }
    this.notesService.getNotes(params).subscribe({
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
