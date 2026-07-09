import { Component, signal, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { DatePipe } from '@angular/common';
import { ReclamationsService } from '../../../core/services/reclamations.service';
import { ReclamationListItem } from '../../../core/models/reclamation.model';
import { BadgeComponent } from '../../../shared/components/badge/badge.component';
import { LoadingSpinnerComponent } from '../../../shared/components/loading-spinner/loading-spinner.component';

@Component({
  selector: 'app-reclamations-list',
  standalone: true,
  imports: [RouterLink, BadgeComponent, LoadingSpinnerComponent, DatePipe],
  template: `
    <div class="max-w-6xl mx-auto">
      <div class="mb-6">
        <h1 class="text-2xl font-bold text-gray-900">Gestion des Réclamations</h1>
        <p class="text-gray-500 mt-1">Traitez les réclamations des étudiants.</p>
      </div>

      @if (loading()) {
        <app-loading-spinner text="Chargement..." />
      } @else if (error()) {
        <div class="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">{{ error() }}</div>
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
                <th class="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase">Délai</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200">
              @for (rec of reclamations(); track rec.id) {
                <tr class="hover:bg-gray-50 cursor-pointer"
                    [routerLink]="['/coordinateur/reclamations', rec.id]">
                  <td class="px-4 py-3">
                    <p class="text-sm font-medium text-gray-900">{{ rec.etudiant_nom }}</p>
                    <p class="text-xs text-gray-500">{{ rec.etudiant_matricule }}</p>
                  </td>
                  <td class="px-4 py-3 text-sm text-gray-600">{{ rec.code_module }}</td>
                  <td class="px-4 py-3 text-sm text-gray-600">{{ motifLabel(rec.motif) }}</td>
                  <td class="px-4 py-3"><app-badge [statut]="rec.statut" /></td>
                  <td class="px-4 py-3 text-sm text-gray-500">{{ rec.date_creation | date:'short' }}</td>
                  <td class="px-4 py-3">
                    <span class="text-sm" [class.text-red-600]="rec.est_en_retard">
                      {{ rec.date_limite_traitement | date:'short' }}
                      @if (rec.est_en_retard) { <span class="ml-1">⚠️</span> }
                    </span>
                  </td>
                </tr>
              }
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        @if (totalPages() > 1) {
          <div class="flex items-center justify-center gap-2 mt-6">
            <button (click)="goToPage(currentPage() - 1)" [disabled]="currentPage() <= 1"
                    class="px-3 py-1.5 text-sm rounded-lg border border-gray-300 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed">
              ← Précédent
            </button>
            @for (p of range(totalPages()); track $index) {
              <button (click)="goToPage($index + 1)"
                      class="px-3 py-1.5 text-sm rounded-lg border"
                      [class.bg-primary-600]="$index + 1 === currentPage()"
                      [class.text-white]="$index + 1 === currentPage()"
                      [class.border-gray-300]="$index + 1 !== currentPage()"
                      [class.hover:bg-gray-50]="$index + 1 !== currentPage()">
                {{ $index + 1 }}
              </button>
            }
            <button (click)="goToPage(currentPage() + 1)" [disabled]="currentPage() >= totalPages()"
                    class="px-3 py-1.5 text-sm rounded-lg border border-gray-300 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed">
              Suivant →
            </button>
          </div>
        }
      }
    </div>
  `,
})
export class ReclamationsListComponent {
  private reclamationsService = inject(ReclamationsService);
  reclamations = signal<ReclamationListItem[]>([]);
  loading = signal(true);
  error = signal('');
  currentPage = signal(1);
  totalPages = signal(1);

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

  range(n: number): number[] {
    return Array.from({ length: n }, (_, i) => i);
  }

  goToPage(page: number): void {
    this.currentPage.set(page);
    this.loadReclamations();
  }

  private loadReclamations(): void {
    this.reclamationsService.getPendingReclamations({ page: this.currentPage() }).subscribe({
      next: (response) => {
        this.reclamations.set(response.results);
        this.totalPages.set(Math.ceil(response.count / 10) || 1);
        this.loading.set(false);
      },
      error: () => {
        this.error.set('Erreur lors du chargement.');
        this.loading.set(false);
      },
    });
  }
}