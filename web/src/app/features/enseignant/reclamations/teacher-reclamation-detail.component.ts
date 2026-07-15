import { Component, OnInit, inject, signal } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { ReclamationsService } from '../../../core/services/reclamations.service';
import { ReclamationDetail } from '../../../core/models/reclamation.model';
import { FrDatePipe } from '../../../core/pipes/fr-date.pipe';
import { BadgeComponent } from '../../../shared/components/badge/badge.component';
import { LoadingSpinnerComponent } from '../../../shared/components/loading-spinner/loading-spinner.component';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-teacher-reclamation-detail',
  standalone: true,
  imports: [BadgeComponent, LoadingSpinnerComponent, FrDatePipe, FormsModule],
  template: `
    <div class="max-w-4xl mx-auto">
      @if (loading()) {
        <app-loading-spinner text="Chargement..." />
      } @else if (error()) {
        <div class="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">{{ error() }}</div>
      } @else {
        @let rec = reclamation();
        @if (rec) {
          <div class="mb-6">
            <button (click)="router.navigate(['/enseignant/reclamations'])" class="text-indigo-600 hover:text-indigo-800 text-sm mb-4 inline-block">
              &larr; Retour aux réclamations
            </button>
            <h1 class="text-2xl font-bold text-gray-900">Détail de la réclamation</h1>
          </div>

          <div class="bg-white rounded-lg border border-gray-200 overflow-hidden">
            <div class="p-6 space-y-4">
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <p class="text-xs font-medium text-gray-500 uppercase">Étudiant</p>
                  <p class="text-sm text-gray-900">{{ rec.etudiant_info.nom }}</p>
                  <p class="text-xs text-gray-500">{{ rec.etudiant_info.matricule }}</p>
                </div>
                <div>
                  <p class="text-xs font-medium text-gray-500 uppercase">Statut</p>
                  <app-badge [statut]="rec.statut" />
                </div>
                <div>
                  <p class="text-xs font-medium text-gray-500 uppercase">Date</p>
                  <p class="text-sm text-gray-900">{{ rec.date_creation | frDate }}</p>
                </div>
              </div>

              <div>
                <p class="text-xs font-medium text-gray-500 uppercase">Description</p>
                <p class="text-sm text-gray-900 mt-1">{{ rec.description }}</p>
              </div>

              @if (rec.lignes && rec.lignes.length > 0) {
                <div>
                  <p class="text-xs font-medium text-gray-500 uppercase mb-2">Lignes concernées</p>
                  <div class="space-y-2">
                    @for (ligne of rec.lignes; track ligne.id) {
                      <div class="p-3 bg-gray-50 rounded-lg">
                        <p class="text-sm font-medium text-gray-900">{{ ligne.code_element }} - {{ ligne.nom_matiere }}</p>
                        <p class="text-xs text-gray-500">Note originale: {{ ligne.note_originale }}</p>
                        <p class="text-xs text-gray-500">Motif: {{ motifLabel(ligne.motif) }}</p>
                      </div>
                    }
                  </div>
                </div>
              }

              @if (rec.commentaire_professeur) {
                <div>
                  <p class="text-xs font-medium text-gray-500 uppercase">Mon commentaire</p>
                  <p class="text-sm text-gray-900 mt-1">{{ rec.commentaire_professeur }}</p>
                </div>
              }

              @if (rec.statut === 'EN_REVISION_ENSEIGNANT') {
                <div class="pt-4 border-t border-gray-200">
                  <p class="text-sm font-medium text-gray-900 mb-2">Commentaire pour le coordinateur</p>
                  <textarea [(ngModel)]="commentaire" rows="3"
                            class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                            placeholder="Ajoutez un commentaire..."></textarea>
                  <div class="flex gap-3 mt-4">
                    <button (click)="onApprouver()" [disabled]="actionLoading()"
                            class="px-4 py-2 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50">
                      Approuver & fermer
                    </button>
                    <button (click)="onRenvoyerAuCoordinateur()" [disabled]="actionLoading()"
                            class="px-4 py-2 bg-orange-600 text-white text-sm rounded-lg hover:bg-orange-700 transition-colors disabled:opacity-50">
                      Renvoyer au coordinateur
                    </button>
                  </div>
                </div>
              }
            </div>
          </div>
        }
      }
    </div>
  `,
})
export class TeacherReclamationDetailComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private reclamationsService = inject(ReclamationsService);
  router = inject(Router);

  reclamation = signal<ReclamationDetail | null>(null);
  loading = signal(true);
  error = signal('');
  actionLoading = signal(false);
  commentaire = signal('');

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    if (id) {
      this.loadReclamation(id);
    } else {
      this.error.set('ID de réclamation invalide.');
      this.loading.set(false);
    }
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

  onApprouver(): void {
    const rec = this.reclamation();
    if (!rec) return;
    this.actionLoading.set(true);
    this.reclamationsService.envoyerRevisionProfesseur(rec.id, this.commentaire()).subscribe({
      next: () => {
        this.actionLoading.set(false);
        this.router.navigate(['/enseignant/reclamations']);
      },
      error: (err) => {
        this.actionLoading.set(false);
        this.error.set(err?.error?.detail || 'Erreur lors de l\'approbation.');
      },
    });
  }

  onRenvoyerAuCoordinateur(): void {
    const rec = this.reclamation();
    if (!rec) return;
    this.actionLoading.set(true);
    this.reclamationsService.renvoyerAuCoordinateur(rec.id, this.commentaire() || 'Révision effectuée par l\'enseignant.').subscribe({
      next: () => {
        this.actionLoading.set(false);
        this.router.navigate(['/enseignant/reclamations']);
      },
      error: (err) => {
        this.actionLoading.set(false);
        this.error.set(err?.error?.detail || 'Erreur lors du renvoi au coordinateur.');
      },
    });
  }

  private loadReclamation(id: number): void {
    this.reclamationsService.getTeacherReclamationDetail(id).subscribe({
      next: (rec) => {
        this.reclamation.set(rec);
        this.loading.set(false);
      },
      error: () => {
        this.error.set('Erreur lors du chargement.');
        this.loading.set(false);
      },
    });
  }
}