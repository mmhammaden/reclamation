import { Component, signal, inject } from '@angular/core';
import { ReclamationsService } from '../../../core/services/reclamations.service';
import { ReclamationListItem } from '../../../core/models/reclamation.model';
import { DatePipe } from '@angular/common';
import { BadgeComponent } from '../../../shared/components/badge/badge.component';
import { LoadingSpinnerComponent } from '../../../shared/components/loading-spinner/loading-spinner.component';

@Component({
  selector: 'app-reclamations',
  standalone: true,
  imports: [BadgeComponent, LoadingSpinnerComponent, DatePipe],
  template: `
    <div class="max-w-6xl mx-auto">
      <div class="mb-6">
        <h1 class="text-2xl font-bold text-gray-900">Réclamations</h1>
        <p class="text-gray-500 mt-1">Consultez les réclamations liées à vos modules.</p>
      </div>

      @if (loading()) {
        <app-loading-spinner text="Chargement..." />
      } @else if (error()) {
        <div class="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">{{ error() }}</div>
      } @else if (reclamations().length === 0) {
        <div class="text-center py-12 bg-white rounded-lg border border-gray-200">
          <p class="text-lg text-gray-500">Aucune réclamation pour vos modules.</p>
        </div>
      } @else {
        <div class="bg-white rounded-lg border border-gray-200 overflow-hidden">
          <table class="w-full">
            <thead class="bg-gray-50">
              <tr>
                <th class="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase">Étudiant</th>
                <th class="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase">Module</th>
                <th class="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase">Motif</th>
                <th class="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase">Statut</th>
                <th class="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase">Date</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200">
              @for (rec of reclamations(); track rec.id) {
                <tr class="hover:bg-gray-50">
                  <td class="px-4 py-3">
                    <p class="text-sm font-medium text-gray-900">{{ rec.etudiant_nom }}</p>
                    <p class="text-xs text-gray-500">{{ rec.etudiant_matricule }}</p>
                  </td>
                  <td class="px-4 py-3 text-sm text-gray-600">
                    @for (module of rec.modules; track module.code) {
                      <div>{{ module.code }}</div>
                    }
                  </td>
                  <td class="px-4 py-3 text-sm text-gray-600">
                    @for (module of rec.modules; track module.code) {
                      <div>{{ motifLabel(module.motif) }}</div>
                    }
                  </td>
                  <td class="px-4 py-3"><app-badge [statut]="rec.statut" /></td>
                  <td class="px-4 py-3 text-sm text-gray-500">{{ rec.date_creation | date:'short' }}</td>
                </tr>
              }
            </tbody>
          </table>
        </div>
      }
    </div>
  `,
})
export class ReclamationsComponent {
  private reclamationsService = inject(ReclamationsService);
  reclamations = signal<ReclamationListItem[]>([]);
  loading = signal(true);
  error = signal('');

  constructor() {
    this.loadReclamations();
  }

  motifLabel(motif: string): string {
    const labels: Record<string, string> = {
      ERREUR_SAISIE: 'Erreur de saisie',
      OUBLI_NOTE: 'Oubli de note',
      VERIFICATION_COPIE: 'Vérification de copie',
      AUTRE: 'Autre',
    };
    return labels[motif] || motif;
  }

  private loadReclamations(): void {
    this.reclamationsService.getTeacherReclamations().subscribe({
      next: (response) => {
        this.reclamations.set(response.results);
        this.loading.set(false);
      },
      error: () => {
        this.error.set('Erreur lors du chargement.');
        this.loading.set(false);
      },
    });
  }
}