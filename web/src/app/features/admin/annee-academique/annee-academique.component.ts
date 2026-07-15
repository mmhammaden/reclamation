import { Component, signal, inject, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { AnneeAcademiqueService, AnneeAcademique } from '../../../core/services/annee-academique.service';
import { LoadingSpinnerComponent } from '../../../shared/components/loading-spinner/loading-spinner.component';

@Component({
  selector: 'app-annee-academique',
  standalone: true,
  imports: [FormsModule, LoadingSpinnerComponent],
  template: `
    <div class="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Année Académique</h1>
        <p class="text-gray-500 mt-1">Configurez l'année académique active et ses semestres.</p>
      </div>

      @if (success()) {
        <div class="p-4 bg-green-50 border border-green-200 rounded-lg text-green-700">{{ success() }}</div>
      }
      @if (error()) {
        <div class="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">{{ error() }}</div>
      }

      @if (loading()) {
        <app-loading-spinner text="Chargement..." />
      } @else {
        <!-- Current active year display -->
        @if (currentAnnee(); as annee) {
          <div class="bg-white rounded-lg border border-gray-200 p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Année active</h2>
            <div class="space-y-2">
              <p><span class="font-medium text-gray-700">Année :</span> {{ annee.annee }}</p>
              <p><span class="font-medium text-gray-700">Semestres :</span>
                <span class="inline-flex gap-1">
                  @for (s of annee.semestres_list; track s) {
                    <span class="px-2 py-0.5 bg-primary-50 text-primary-700 text-xs font-medium rounded-full">{{ s }}</span>
                  }
                </span>
              </p>
            </div>
            <button (click)="showEditForm.set(true)" class="mt-4 px-4 py-2 text-sm font-medium text-primary-600 border border-primary-300 rounded-lg hover:bg-primary-50 transition-colors">
              Modifier
            </button>
          </div>
        } @else {
          <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-yellow-800">
            <p class="font-medium">Aucune année académique active</p>
            <p class="text-sm mt-1">Créez une année académique pour commencer.</p>
          </div>
        }

        <!-- Create/Edit Form -->
        @if (!currentAnnee() || showEditForm()) {
          <div class="bg-white rounded-lg border border-gray-200 p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">
              @if (currentAnnee()) {
                Modifier l'année académique
              } @else {
                Créer une année académique
              }
            </h2>
            <form (ngSubmit)="onSubmit()" class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Année</label>
                <input type="text" [ngModel]="annee()" (ngModelChange)="annee.set($event)" name="annee" required
                       placeholder="Ex: 2024-2025"
                       class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none"
                       [class.border-red-500]="anneeError()" />
                @if (anneeError()) {
                  <p class="mt-1 text-xs text-red-600">{{ anneeError() }}</p>
                }
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Semestres</label>
                <div class="space-y-2">
                  <label class="flex items-center gap-3 p-3 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50"
                         [class.border-primary-500]="semestresActifs() === 'S1,S3,S5'">
                    <input type="radio" [ngModel]="semestresActifs()" (ngModelChange)="semestresActifs.set($event)" name="semestres" value="S1,S3,S5"
                           class="text-primary-600 focus:ring-primary-500" />
                    <div>
                      <p class="font-medium text-gray-900">Les semestres impaires</p>
                      <p class="text-sm text-gray-500">S1, S3, S5</p>
                    </div>
                  </label>
                  <label class="flex items-center gap-3 p-3 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50"
                         [class.border-primary-500]="semestresActifs() === 'S2,S4,S6'">
                    <input type="radio" [ngModel]="semestresActifs()" (ngModelChange)="semestresActifs.set($event)" name="semestres" value="S2,S4,S6"
                           class="text-primary-600 focus:ring-primary-500" />
                    <div>
                      <p class="font-medium text-gray-900">Les semestres paires</p>
                      <p class="text-sm text-gray-500">S2, S4, S6</p>
                    </div>
                  </label>
                </div>
              </div>

              <div class="flex items-center gap-3 pt-2">
                <button type="submit" [disabled]="submitting()"
                        class="px-6 py-2.5 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50">
                  @if (submitting()) {
                    <app-loading-spinner size="sm" containerClass="py-0" color="white" />
                  } @else {
                    @if (currentAnnee()) {
                      Enregistrer
                    } @else {
                      Créer
                    }
                  }
                </button>
                @if (currentAnnee()) {
                  <button type="button" (click)="showEditForm.set(false); resetForm()"
                          class="px-4 py-2 text-gray-700 hover:text-gray-900">
                    Annuler
                  </button>
                }
              </div>
            </form>
          </div>
        }
      }
    </div>
  `,
})
export class AnneeAcademiqueComponent implements OnInit {
  private anneeService = inject(AnneeAcademiqueService);

  currentAnnee = signal<AnneeAcademique | null>(null);
  loading = signal(true);
  submitting = signal(false);
  success = signal('');
  error = signal('');
  showEditForm = signal(false);

  annee = signal('');
  semestresActifs = signal('S1,S3,S5');
  anneeError = signal('');

  ngOnInit(): void {
    this.loadCurrent();
  }

  private loadCurrent(): void {
    this.anneeService.getCurrent().subscribe({
      next: (annee) => {
        this.currentAnnee.set(annee);
        this.annee.set(annee.annee);
        this.semestresActifs.set(annee.semestres_actifs);
        this.loading.set(false);
      },
      error: () => {
        this.currentAnnee.set(null);
        this.loading.set(false);
      },
    });
  }

  resetForm(): void {
    const current = this.currentAnnee();
    if (current) {
      this.annee.set(current.annee);
      this.semestresActifs.set(current.semestres_actifs);
    } else {
      this.annee.set('');
      this.semestresActifs.set('S1,S3,S5');
    }
    this.anneeError.set('');
  }

  onSubmit(): void {
    this.anneeError.set('');
    this.error.set('');
    this.success.set('');

    if (!this.annee().trim()) {
      this.anneeError.set("L'année est obligatoire.");
      return;
    }

    this.submitting.set(true);
    const current = this.currentAnnee();

    if (current) {
      // Update existing
      this.anneeService.update(current.id, {
        semestres_actifs: this.semestresActifs(),
      }).subscribe({
        next: (updated) => {
          this.currentAnnee.set(updated);
          this.showEditForm.set(false);
          this.submitting.set(false);
          this.success.set('Année académique mise à jour avec succès.');
        },
        error: (err) => {
          this.submitting.set(false);
          this.error.set(err.error?.detail || 'Erreur lors de la mise à jour.');
        },
      });
    } else {
      // Create new
      this.anneeService.create({
        annee: this.annee().trim(),
        semestres_actifs: this.semestresActifs(),
      }).subscribe({
        next: (created) => {
          this.currentAnnee.set(created);
          this.submitting.set(false);
          this.success.set('Année académique créée avec succès.');
        },
        error: (err) => {
          this.submitting.set(false);
          this.error.set(err.error?.detail || 'Erreur lors de la création.');
        },
      });
    }
  }
}