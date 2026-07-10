import { Component, signal, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { ReclamationsService } from '../../../core/services/reclamations.service';
import { DashboardStats } from '../../../core/models/reclamation.model';
import { BadgeComponent } from '../../../shared/components/badge/badge.component';
import { LoadingSpinnerComponent } from '../../../shared/components/loading-spinner/loading-spinner.component';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [RouterLink, BadgeComponent, LoadingSpinnerComponent],
  template: `
    <div class="max-w-6xl mx-auto">
      <div class="mb-6">
        <h1 class="text-2xl font-bold text-gray-900">Tableau de Bord</h1>
        <p class="text-gray-500 mt-1">Vue d'ensemble des réclamations.</p>
      </div>

      @if (loading()) {
        <app-loading-spinner text="Chargement du tableau de bord..." />
      } @else {
        <!-- Stats Cards -->
        <div class="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
          <div class="bg-white rounded-lg border border-gray-200 p-4">
            <p class="text-sm text-gray-500">Total</p>
            <p class="text-2xl font-bold text-gray-900">{{ stats()?.total ?? 0 }}</p>
          </div>
          <div class="bg-yellow-50 rounded-lg border border-yellow-200 p-4">
            <p class="text-sm text-yellow-700">En attente</p>
            <p class="text-2xl font-bold text-yellow-800">{{ stats()?.en_attente ?? 0 }}</p>
          </div>
          <div class="bg-blue-50 rounded-lg border border-blue-200 p-4">
            <p class="text-sm text-blue-700">En cours</p>
            <p class="text-2xl font-bold text-blue-800">{{ stats()?.en_cours ?? 0 }}</p>
          </div>
          <div class="bg-red-50 rounded-lg border border-red-200 p-4">
            <p class="text-sm text-red-700">En retard</p>
            <p class="text-2xl font-bold text-red-800">{{ stats()?.en_retard ?? 0 }}</p>
          </div>
          <div class="bg-green-50 rounded-lg border border-green-200 p-4">
            <p class="text-sm text-green-700">Traitées</p>
            <p class="text-2xl font-bold text-green-800">{{ stats()?.traitees ?? 0 }}</p>
          </div>
        </div>

        <!-- Recent Reclamations -->
        <div class="bg-white rounded-lg border border-gray-200">
          <div class="px-4 py-3 border-b border-gray-200 flex items-center justify-between">
            <h2 class="font-semibold text-gray-900">Réclamations récentes</h2>
            <a routerLink="/coordinateur/reclamations" class="text-sm text-primary-600 hover:text-primary-700">
              Voir tout →
            </a>
          </div>
          <div class="divide-y divide-gray-200">
            @for (rec of stats()?.recentes ?? []; track rec.id) {
              <div class="px-4 py-3 hover:bg-gray-50 cursor-pointer"
                   [routerLink]="['/coordinateur/reclamations', rec.id]">
                <div class="flex items-center justify-between">
                  <div>
                    <p class="text-sm font-medium text-gray-900">{{ rec.etudiant_nom }}</p>
                    <p class="text-xs text-gray-500">
                      @for (module of rec.modules; track module.code) {
                        {{ module.code }}@if (!$last) {, }
                      }
                    </p>
                  </div>
                  <app-badge [statut]="rec.statut" />
                </div>
              </div>
            }
          </div>
        </div>
      }
    </div>
  `,
})
export class DashboardComponent {
  private reclamationsService = inject(ReclamationsService);
  stats = signal<DashboardStats | null>(null);
  loading = signal(true);

  constructor() {
    this.loadDashboard();
  }

  private loadDashboard(): void {
    this.reclamationsService.getDashboard().subscribe({
      next: (data) => {
        this.stats.set(data);
        this.loading.set(false);
      },
      error: () => this.loading.set(false),
    });
  }
}