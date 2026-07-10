import { Component, signal, inject } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { DatePipe } from '@angular/common';
import { Observable } from 'rxjs';
import { ReclamationsService } from '../../../core/services/reclamations.service';
import { ReclamationDetail, StatutReclamation, ReclamationDecision } from '../../../core/models/reclamation.model';
import { BadgeComponent } from '../../../shared/components/badge/badge.component';
import { LoadingSpinnerComponent } from '../../../shared/components/loading-spinner/loading-spinner.component';

@Component({
  selector: 'app-reclamation-detail',
  standalone: true,
  imports: [FormsModule, BadgeComponent, LoadingSpinnerComponent, DatePipe],
  template: `
    <div class="max-w-4xl mx-auto">
      @if (loading()) {
        <app-loading-spinner text="Chargement..." />
      } @else if (error()) {
        <div class="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">{{ error() }}</div>
      } @else {
        @if (reclamation(); as rec) {
        <!-- Header -->
        <div class="mb-6">
          <div class="flex items-center justify-between">
            <div>
              <h1 class="text-2xl font-bold text-gray-900">Réclamation #{{ rec.id }}</h1>
              <p class="text-gray-500 mt-1">
                {{ rec.etudiant_info.nom }} ({{ rec.etudiant_info.matricule }})
              </p>
            </div>
            <app-badge [statut]="rec.statut" />
          </div>
        </div>

        <!-- Lignes (matières) -->
        <div class="bg-white rounded-lg border border-gray-200 p-4 mb-6">
          <h2 class="font-semibold text-gray-900 mb-3">Matières concernées</h2>
          <div class="space-y-3">
            @for (ligne of rec.lignes; track ligne.id) {
              <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <p class="font-medium text-gray-900">{{ ligne.code_module }} - {{ ligne.nom_module }}</p>
                  <p class="text-sm text-gray-500">Motif : {{ motifLabel(ligne.motif) }}</p>
                </div>
                <div class="text-right">
                  <p class="text-sm text-gray-500">Originale : <span class="font-medium">{{ ligne.note_originale ?? 'N/A' }}</span></p>
                  <p class="text-sm text-gray-500">Nouvelle : <span class="font-medium">{{ ligne.nouvelle_note ?? 'N/A' }}</span></p>
                </div>
              </div>
            }
          </div>
        </div>

        <!-- Info Cards -->
        <div class="grid grid-cols-2 gap-4 mb-6">
          <div class="bg-white rounded-lg border border-gray-200 p-4">
            <p class="text-sm text-gray-500">Date limite</p>
            <p class="font-medium" [class.text-red-600]="rec.est_en_retard">
              {{ rec.date_limite_traitement | date:'short' }}
              @if (rec.est_en_retard) { ⚠️ }
            </p>
          </div>
          <div class="bg-white rounded-lg border border-gray-200 p-4">
            <p class="text-sm text-gray-500">Date de traitement</p>
            <p class="font-medium">{{ (rec.date_traitement | date:'short') ?? 'N/A' }}</p>
          </div>
        </div>

        <!-- Description -->
        @if (rec.description) {
          <div class="bg-white rounded-lg border border-gray-200 p-4 mb-6">
            <p class="text-sm text-gray-500 mb-2">Description</p>
            <p class="text-gray-900">{{ rec.description }}</p>
          </div>
        }

        <!-- History -->
        <div class="bg-white rounded-lg border border-gray-200 p-4 mb-6">
          <h2 class="font-semibold text-gray-900 mb-3">Historique</h2>
          <div class="space-y-3">
            @for (h of rec.historique_statuts; track h.id) {
              <div class="flex items-start gap-3">
                <div class="w-2 h-2 rounded-full bg-primary-500 mt-2"></div>
                <div>
                  <p class="text-sm text-gray-900">
                    <span class="font-medium">{{ h.modifie_par_nom }}</span>
                    a changé le statut
                  </p>
                  <p class="text-xs text-gray-500">{{ h.date_modification | date:'short' }}</p>
                  @if (h.commentaire) {
                    <p class="text-sm text-gray-600 mt-1">{{ h.commentaire }}</p>
                  }
                </div>
              </div>
            }
          </div>
        </div>

        <!-- Action: Prendre en cours (only for EN_ATTENTE) -->
        @if (rec.statut === 'EN_ATTENTE') {
          <div class="bg-white rounded-lg border border-gray-200 p-6 mb-6">
            <h2 class="font-semibold text-gray-900 mb-4">Prise en charge</h2>
            <button (click)="onTraiter()" [disabled]="actionLoading()"
                    class="px-6 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50">
              Prendre en cours de traitement
            </button>
          </div>
        }

        <!-- Action Form (for EN_ATTENTE or EN_COURS — traiter is chained automatically) -->
        @if (rec.statut === 'EN_ATTENTE' || rec.statut === 'EN_COURS') {
          <div class="bg-white rounded-lg border border-gray-200 p-6">
            <h2 class="font-semibold text-gray-900 mb-4">Traiter la réclamation</h2>

            @if (actionError()) {
              <div class="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
                {{ actionError() }}
              </div>
            }

            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Commentaire</label>
                <textarea [(ngModel)]="commentaire" rows="3"
                          class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none resize-none"
                          placeholder="Commentaire obligatoire..."></textarea>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Nouvelles notes (si acceptée)
                </label>
                @for (ligne of rec.lignes; track ligne.id) {
                  <div class="flex items-center gap-2 mb-2">
                    <span class="text-sm text-gray-600 w-40">{{ ligne.code_module }} :</span>
                    <input type="number" [ngModel]="nouvellesNotes()[ligne.note_elementaire]"
                           (ngModelChange)="setNouvelleNote(ligne.note_elementaire, $event)"
                           step="0.01" class="w-32 px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 outline-none"
                           placeholder="Note" />
                  </div>
                }
              </div>
              <div class="flex items-center gap-3">
                <button (click)="onAccepter()" [disabled]="actionLoading()"
                        class="px-6 py-2.5 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50">
                  Accepter
                </button>
                <button (click)="onRejeter()" [disabled]="actionLoading()"
                        class="px-6 py-2.5 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50">
                  Rejeter
                </button>
              </div>
            </div>
          </div>
        }
      }
      }
    </div>
  `,
})
export class ReclamationDetailComponent {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private reclamationsService = inject(ReclamationsService);

  reclamation = signal<ReclamationDetail | null>(null);
  loading = signal(true);
  error = signal('');
  commentaire = '';
  nouvellesNotes = signal<Record<number, number>>({});
  actionLoading = signal(false);
  actionError = signal('');

  constructor() {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    if (id) {
      this.loadReclamation(id);
    }
  }

  setNouvelleNote(noteElementaireId: number, valeur: string): void {
    const val = parseFloat(valeur);
    if (!isNaN(val)) {
      this.nouvellesNotes.update(n => ({ ...n, [noteElementaireId]: val }));
    } else {
      this.nouvellesNotes.update(n => {
        const copy = { ...n };
        delete copy[noteElementaireId];
        return copy;
      });
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

  onTraiter(): void {
    this.actionLoading.set(true);
    this.actionError.set('');

    const id = this.reclamation()!.id;
    this.reclamationsService.traiterReclamation(id).subscribe({
      next: (rec) => {
        this.reclamation.set(rec);
        this.actionLoading.set(false);
      },
      error: (err) => {
        this.actionLoading.set(false);
        this.actionError.set(err.error?.detail || 'Erreur lors de la prise en charge.');
      },
    });
  }

  private ensureTraiterThenAct(
    id: number,
    action: () => Observable<ReclamationDetail>
  ): void {
    const rec = this.reclamation();
    if (!rec) return;

    if (rec.statut === 'EN_ATTENTE') {
      this.reclamationsService.traiterReclamation(id).subscribe({
        next: () => {
          action().subscribe({
            next: (updated) => {
              this.reclamation.set(updated);
              this.actionLoading.set(false);
            },
            error: (err) => {
              this.actionLoading.set(false);
              this.actionError.set(err.error?.detail || 'Erreur lors du traitement.');
            },
          });
        },
        error: (err) => {
          this.actionLoading.set(false);
          this.actionError.set(err.error?.detail || 'Erreur lors de la prise en charge.');
        },
      });
    } else {
      action().subscribe({
        next: (updated) => {
          this.reclamation.set(updated);
          this.actionLoading.set(false);
        },
        error: (err) => {
          this.actionLoading.set(false);
          this.actionError.set(err.error?.detail || 'Erreur lors du traitement.');
        },
      });
    }
  }

  onAccepter(): void {
    if (!this.commentaire) {
      this.actionError.set('Le commentaire est obligatoire.');
      return;
    }
    this.actionLoading.set(true);
    this.actionError.set('');

    const id = this.reclamation()!.id;
    const notes = this.nouvellesNotes();
    const decision: ReclamationDecision = {
      commentaire_decision: this.commentaire,
    };
    if (Object.keys(notes).length > 0) {
      // Convert numeric keys to string keys as expected by the API
      const strNotes: Record<string, number> = {};
      for (const [key, val] of Object.entries(notes)) {
        strNotes[String(key)] = val;
      }
      decision.nouvelles_notes = strNotes;
    }

    this.ensureTraiterThenAct(id, () =>
      this.reclamationsService.accepterReclamation(id, decision)
    );
  }

  onRejeter(): void {
    if (!this.commentaire) {
      this.actionError.set('Le commentaire est obligatoire.');
      return;
    }
    this.actionLoading.set(true);
    this.actionError.set('');

    const id = this.reclamation()!.id;
    this.ensureTraiterThenAct(id, () =>
      this.reclamationsService.rejeterReclamation(id, {
        commentaire_decision: this.commentaire,
      })
    );
  }

  private loadReclamation(id: number): void {
    this.reclamationsService.getReclamation(id).subscribe({
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
