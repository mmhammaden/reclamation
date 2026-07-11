import { Component, signal, inject } from '@angular/core';
import { ReclamationsService } from '../../../core/services/reclamations.service';
import { LoadingSpinnerComponent } from '../../../shared/components/loading-spinner/loading-spinner.component';

@Component({
  selector: 'app-import-pv',
  standalone: true,
  imports: [LoadingSpinnerComponent],
  template: `
    <div class="max-w-3xl mx-auto space-y-6">
      <div class="mb-6">
        <h1 class="text-2xl font-bold text-gray-900">Administration</h1>
        <p class="text-gray-500 mt-1">Import de PV et export des rapports.</p>
      </div>

      @if (success()) {
        <div class="p-4 bg-green-50 border border-green-200 rounded-lg text-green-700">{{ success() }}</div>
      }
      @if (error()) {
        <div class="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">{{ error() }}</div>
      }

      <!-- Import PV -->
      <div class="bg-white rounded-lg border border-gray-200 p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">Import de PV</h2>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Fichier PV (Excel/CSV)</label>
            <input type="file" (change)="onFileSelected($event)" accept=".xlsx,.xls,.csv"
                   class="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100" />
          </div>
          <button (click)="onImport()" [disabled]="!selectedFile() || uploading()"
                  class="px-6 py-2.5 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50">
            @if (uploading()) {
              <app-loading-spinner size="sm" containerClass="py-0" color="white" />
            } @else {
              Importer
            }
          </button>
        </div>
      </div>

      <!-- Export Rapport -->
      <div class="bg-white rounded-lg border border-gray-200 p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-1">Export des rapports</h2>
        <p class="text-sm text-gray-500 mb-4">Téléchargez toutes les réclamations avec leurs détails au format CSV.</p>
        <button (click)="onExport()" [disabled]="exporting()"
                class="px-6 py-2.5 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50">
          @if (exporting()) {
            <app-loading-spinner size="sm" containerClass="py-0" color="white" />
          } @else {
            Télécharger le rapport CSV
          }
        </button>
      </div>
    </div>
  `,
})
export class ImportPvComponent {
  private reclamationsService = inject(ReclamationsService);
  selectedFile = signal<File | null>(null);
  uploading = signal(false);
  exporting = signal(false);
  success = signal('');
  error = signal('');

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files?.length) {
      this.selectedFile.set(input.files[0]);
      this.success.set('');
      this.error.set('');
    }
  }

  onImport(): void {
    const file = this.selectedFile();
    if (!file) {
      this.error.set('Veuillez sélectionner un fichier.');
      return;
    }

    this.uploading.set(true);
    this.error.set('');
    this.success.set('');

    const formData = new FormData();
    formData.append('fichier', file);

    this.reclamationsService.importPV(formData).subscribe({
      next: (response) => {
        this.success.set(response.detail);
        this.uploading.set(false);
        this.selectedFile.set(null);
      },
      error: (err) => {
        this.uploading.set(false);
        this.error.set(err.error?.detail || 'Erreur lors de l\'import.');
      },
    });
  }

  onExport(): void {
    this.exporting.set(true);
    this.error.set('');

    this.reclamationsService.getRapports({ format: 'csv' }).subscribe({
      next: (blob) => {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `rapport_reclamations_${new Date().toISOString().slice(0, 10)}.csv`;
        a.click();
        URL.revokeObjectURL(url);
        this.exporting.set(false);
      },
      error: () => {
        this.exporting.set(false);
        this.error.set('Erreur lors de l\'export.');
      },
    });
  }
}