import { Component, signal, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { FrDatePipe } from '../../../core/pipes/fr-date.pipe';
import { ReclamationsService } from '../../../core/services/reclamations.service';
import { ReclamationListItem } from '../../../core/models/reclamation.model';
import { BadgeComponent } from '../../../shared/components/badge/badge.component';
import { LoadingSpinnerComponent } from '../../../shared/components/loading-spinner/loading-spinner.component';

@Component({
  selector: 'app-mes-reclamations',
  standalone: true,
  imports: [RouterLink, BadgeComponent, LoadingSpinnerComponent, FrDatePipe],
  template: `
    <div class="max-w-5xl mx-auto">
      <div class="flex items-center justify-between mb-6">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">Mes Réclamations</h1>
          <p class="text-gray-500 mt-1">Suivez l'état de vos réclamations.</p>
        </div>
        <a routerLink="/etudiant/nouvelle-reclamation"
           class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors">
          + Nouvelle réclamation
        </a>
      </div>

      @if (loading()) {
        <app-loading-spinner text="Chargement des réclamations..." />
      } @else if (error()) {
        <div class="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">{{ error() }}</div>
      } @else if (reclamations().length === 0) {
        <div class="text-center py-12 bg-white rounded-lg border border-gray-200">
          <p class="text-lg text-gray-500">Aucune réclamation pour le moment.</p>
          <a routerLink="/etudiant/nouvelle-reclamation"
             class="inline-block mt-4 text-primary-600 hover:text-primary-700 font-medium">
            Soumettre une réclamation
          </a>
        </div>
      } @else {
        <div class="bg-white rounded-lg border border-gray-200 overflow-hidden">
          <table class="w-full">
            <thead class="bg-gray-50">
              <tr>
                <th class="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase">Modules</th>
                <th class="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase">Statut</th>
                <th class="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase">Date</th>
                <th class="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase">Délai</th>
                <th class="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200">
              @for (rec of reclamations(); track rec.id) {
                <tr class="hover:bg-gray-50 cursor-pointer"
                    [routerLink]="['/etudiant/reclamations', rec.id]">
                  <td class="px-4 py-3 text-sm">
                    <div class="space-y-1">
                      @for (module of rec.modules; track module.code) {
                        <div class="text-gray-900">
                          <span class="font-medium">{{ module.code }} - {{ module.element }}</span>
                          <span class="text-gray-500 text-xs ml-1">({{ module.type }})</span>
                          <span class="text-gray-500 text-xs ml-1">({{ motifLabel(module.motif) }})</span>
                        </div>
                      }
                    </div>
                  </td>
                  <td class="px-4 py-3"><app-badge [statut]="rec.statut" /></td>
                  <td class="px-4 py-3 text-sm text-gray-500">{{ rec.date_creation | frDate }}</td>
                  <td class="px-4 py-3">
                    <span class="text-sm" [class.text-red-600]="rec.est_en_retard">
                      {{ rec.date_limite_traitement | frDate }}
                      @if (rec.est_en_retard) { <span class="ml-1">⚠️</span> }
                    </span>
                  </td>
                  <td class="px-4 py-3">
                    @if (rec.statut === 'EN_ATTENTE') {
                      <button (click)="$event.stopPropagation(); onDelete(rec.id)"
                              class="text-sm text-red-600 hover:text-red-800 transition-colors">
                        Supprimer
                      </button>
                    }
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
export class MesReclamationsComponent {
  private reclamationsService = inject(ReclamationsService);
  reclamations = signal<ReclamationListItem[]>([]);
  loading = signal(true);
  error = signal('');
  currentPage = signal(1);
  totalPages = signal(1);
  deleteLoading = signal(false);

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

  onDelete(id: number): void {
    if (!confirm('Êtes-vous sûr de vouloir supprimer cette réclamation ?')) return;
    this.deleteLoading.set(true);
    this.reclamationsService.deleteReclamation(id).subscribe({
      next: () => {
        this.deleteLoading.set(false);
        this.loadReclamations();
      },
      error: () => {
        this.deleteLoading.set(false);
        this.error.set('Erreur lors de la suppression.');
      },
    });
  }

  range(n: number): number[] {
    return Array.from({ length: n }, (_, i) => i);
  }

  goToPage(page: number): void {
    this.currentPage.set(page);
    this.loadReclamations();
  }

  private loadReclamations(): void {
    this.reclamationsService.getMyReclamations({ page: this.currentPage() }).subscribe({
      next: (response) => {
        this.reclamations.set(response.results);
        this.totalPages.set(Math.ceil(response.count / 10) || 1);
        this.loading.set(false);
      },
      error: () => {
        this.error.set('Erreur lors du chargement des réclamations.');
        this.loading.set(false);
      },
    });
  }
}