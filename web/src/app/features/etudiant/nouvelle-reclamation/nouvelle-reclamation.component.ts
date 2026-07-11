import { Component, signal, inject, OnInit, computed } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink, ActivatedRoute } from '@angular/router';
import { ReclamationsService } from '../../../core/services/reclamations.service';
import { NotesService } from '../../../core/services/notes.service';
import { MotifReclamation, LigneReclamationCreate } from '../../../core/models/reclamation.model';
import { ResultatSemestre, Module, ElementModule, TypeNoteReclamation } from '../../../core/models/note.model';
import { LoadingSpinnerComponent } from '../../../shared/components/loading-spinner/loading-spinner.component';

interface SelectedElement {
  element: ElementModule;
  type_note: TypeNoteReclamation;
  selected: boolean;
}

@Component({
  selector: 'app-nouvelle-reclamation',
  standalone: true,
  imports: [FormsModule, RouterLink, LoadingSpinnerComponent],
  template: `
    <div class="max-w-3xl mx-auto">
      <div class="mb-6">
        <h1 class="text-2xl font-bold text-gray-900">Nouvelle Réclamation</h1>
        <p class="text-gray-500 mt-1">Sélectionnez les éléments concernés par votre réclamation.</p>
      </div>

      @if (success()) {
        <div class="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg text-green-700">
          <p class="font-medium mb-2">Réclamation soumise avec succès !</p>
          <p class="text-sm">Votre réclamation sera traitée dans les 72 heures ouvrées.</p>
          <a routerLink="/etudiant/mes-reclamations" class="underline ml-2">Voir mes réclamations</a>
        </div>
      }

      @if (error()) {
        <div class="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">{{ error() }}</div>
      }

      @if (!success()) {
        <form (ngSubmit)="onSubmit()" class="bg-white rounded-lg border border-gray-200 p-6 space-y-5">

          <!-- Description globale -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Description générale (optionnel)</label>
            <textarea [(ngModel)]="description" name="description" rows="3"
                      class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none resize-none"
                      placeholder="Contexte général de votre réclamation..."></textarea>
          </div>

          <!-- Modules grouped by code_module -->
          <div>
            <div class="flex items-center justify-between mb-3">
              <label class="block text-sm font-medium text-gray-700">Éléments concernés *</label>
            </div>

            @if (loadingNotes()) {
              <div class="flex justify-center py-8">
                <app-loading-spinner text="Chargement des notes..." />
              </div>
            } @else {
              <div class="space-y-4 max-h-96 overflow-y-auto border border-gray-200 rounded-lg p-4">
                @for (resultat of resultats(); track resultat.id) {
                  <div class="border-b border-gray-100 last:border-0 pb-3 mb-3 last:mb-0">
                    <div class="mb-2">
                      <h3 class="font-medium text-gray-900">
                        {{ resultat.semestre }} - {{ resultat.annee_academique }}
                        <span class="text-sm font-normal"
                              [class.text-green-600]="resultat.observation === 'Validé'"
                              [class.text-red-600]="resultat.observation === 'Rattrapage'">
                          ({{ resultat.observation }})
                        </span>
                      </h3>
                    </div>

                    @for (module of resultat.modules; track module.id) {
                      <div class="ml-2 mb-3">
                        <div class="mb-1">
                          <span class="text-sm font-medium text-gray-700">{{ module.code_module }}</span>
                          <span class="text-xs text-gray-500 ml-2">Moy: {{ module.moy_module }}/20</span>
                        </div>

                        <div class="space-y-2">
                          @for (element of module.elements; track element.id) {
                            <div class="flex items-center gap-4 p-2 bg-gray-50 rounded">
                              <div class="flex-1">
                                <span class="text-sm text-gray-800">{{ element.code_element }}</span>
                                <span class="text-xs text-gray-500 block">
                                  CC: {{ element.note_continu }} | Exam: {{ element.note_final }} | Moy: {{ element.note_moyenne }}
                                </span>
                              </div>

                              <div class="flex gap-2">
                                <label class="flex items-center gap-1 cursor-pointer">
                                  <input type="checkbox"
                                         [checked]="isElementSelected(element.id, 'CONTINU')"
                                         (change)="toggleElementSelection(element, 'CONTINU')"
                                         class="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500" />
                                  <span class="text-xs text-gray-700">CC</span>
                                </label>
                                <label class="flex items-center gap-1 cursor-pointer">
                                  <input type="checkbox"
                                         [checked]="isElementSelected(element.id, 'FINAL')"
                                         (change)="toggleElementSelection(element, 'FINAL')"
                                         class="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500" />
                                  <span class="text-xs text-gray-700">Exam</span>
                                </label>
                              </div>
                            </div>
                          }
                        </div>
                      </div>
                    }
                  </div>
                }
              </div>
            }

            @if (selectedElements().length > 0) {
              <div class="mt-4 space-y-4">
                @for (ligne of lignes; track $index; let i = $index) {
                  <div class="p-4 bg-gray-50 rounded-lg border border-gray-200 space-y-3">
                    <div class="grid grid-cols-12 gap-3">
                      <div class="col-span-6">
                        <label class="block text-xs font-medium text-gray-600 mb-1">Type sélectionné</label>
                        <p class="text-sm font-medium text-gray-900">
                          {{ getElementType(lignes[i].type_note) }} - {{ getElementById(lignes[i].element_module!)?.code_element }}
                        </p>
                      </div>
                      <div class="col-span-5">
                        <label class="block text-xs font-medium text-gray-600 mb-1">Motif *</label>
                        <select [(ngModel)]="lignes[i].motif"
                                name="motif_{{i}}"
                                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 outline-none"
                                required>
                          <option value="">Motif</option>
                          <option value="ERREUR_SAISIE">Erreur de saisie</option>
                          <option value="OUBLI_NOTE">Oubli de note</option>
                          <option value="VERIFICATION_COPIE">Vérification de copie</option>
                          <option value="AUTRE">Autre motif</option>
                        </select>
                      </div>
                      <div class="col-span-1 flex items-end justify-center pb-1">
                        <button type="button" (click)="supprimerLigne(i)" class="text-red-500 hover:text-red-700 text-sm">✕</button>
                      </div>
                    </div>
                    <div>
                      <label class="block text-xs font-medium text-gray-600 mb-1">Description (optionnel)</label>
                      <textarea [(ngModel)]="lignes[i].description"
                                name="desc_{{i}}" rows="2"
                                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 outline-none resize-none"
                                placeholder="Décrivez le problème pour cet élément..."></textarea>
                    </div>
                    <div>
                      <label class="block text-xs font-medium text-gray-600 mb-1">Pièce jointe (optionnel)</label>
                      <input type="file" multiple accept=".pdf,.png,.jpg,.jpeg"
                             (change)="onLigneFichiers($event, i)"
                             class="w-full text-sm text-gray-500 file:mr-3 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-medium file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100" />
                      @if (lignes[i].fichiers?.length) {
                        <p class="mt-1 text-xs text-gray-400">{{ lignes[i].fichiers!.length }} fichier(s)</p>
                      }
                    </div>
                  </div>
                }
              </div>
            }
          </div>

          <!-- Submit -->
          <div class="flex items-center gap-3 pt-2">
            <button type="submit" [disabled]="submitting() || selectedElements().length === 0"
                    class="px-6 py-2.5 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50">
              @if (submitting()) {
                <app-loading-spinner size="sm" containerClass="py-0" color="white" />
              } @else {
                Soumettre la réclamation
              }
            </button>
            <a routerLink="/etudiant/mes-reclamations"
               class="px-6 py-2.5 text-gray-700 hover:text-gray-900 transition-colors">
              Annuler
            </a>
          </div>
        </form>
      }
    </div>
  `,
})
export class NouvelleReclamationComponent implements OnInit {
  private reclamationsService = inject(ReclamationsService);
  private notesService = inject(NotesService);
  private router = inject(Router);
  private route = inject(ActivatedRoute);

  resultats = signal<ResultatSemestre[]>([]);
  loadingNotes = signal(true);
  lignes: LigneReclamationCreate[] = [];
  description = '';
  submitting = signal(false);
  success = signal(false);
  error = signal('');

  // Track selected element IDs with type
  private selectedElementKeys = signal<Set<string>>(new Set());

  // Get all elements from all modules
  allElements = computed(() => {
    const elements: ElementModule[] = [];
    for (const resultat of this.resultats()) {
      for (const module of resultat.modules) {
        elements.push(...module.elements);
      }
    }
    return elements;
  });

  // Get selected elements
  selectedElements = computed(() => {
    return this.allElements().filter(e =>
      this.selectedElementKeys().has(`${e.id}_CONTINU`) ||
      this.selectedElementKeys().has(`${e.id}_FINAL`)
    );
  });

  ngOnInit(): void {
    // Store elementId from query params if available
    this.preselectedElementId = this.route.snapshot.queryParams['elementId']
      ? Number(this.route.snapshot.queryParams['elementId'])
      : null;
    this.loadNotes();
  }

  private preselectedElementId: number | null = null;

  loadNotes(): void {
    this.notesService.getNotes().subscribe({
      next: (response) => {
        this.resultats.set(response.results);
        this.loadingNotes.set(false);
        // After notes are loaded, apply pre-selection if needed
        if (this.preselectedElementId) {
          this.applyPreselection();
        }
      },
      error: () => {
        this.loadingNotes.set(false);
      },
    });
  }

  private applyPreselection(): void {
    const elementId = this.preselectedElementId;
    if (!elementId) return;

    // Find the element in the loaded data
    const element = this.allElements().find(e => e.id === elementId);
    if (!element) return;

    // Pre-select CONTINU by default
    const key = `${elementId}_CONTINU`;
    const newSet = new Set(this.selectedElementKeys());
    newSet.add(key);
    this.selectedElementKeys.set(newSet);

    // Also populate the lignes array
    this.lignes.push({
      element_module: elementId,
      type_note: 'CONTINU' as TypeNoteReclamation,
      motif: MotifReclamation.ERREUR_SAISIE,
      description: '',
      fichiers: [],
    });
  }

  isElementSelected(elementId: number, type: TypeNoteReclamation): boolean {
    return this.selectedElementKeys().has(`${elementId}_${type}`);
  }

  toggleElementSelection(element: ElementModule, type: TypeNoteReclamation): void {
    const key = `${element.id}_${type}`;
    const newSet = new Set(this.selectedElementKeys());
    if (newSet.has(key)) {
      newSet.delete(key);
      // Remove corresponding ligne
      this.lignes = this.lignes.filter(l =>
        !(l.element_module === element.id && l.type_note === type)
      );
    } else {
      newSet.add(key);
      // Add new ligne
      this.lignes.push({
        element_module: element.id,
        type_note: type,
        motif: MotifReclamation.ERREUR_SAISIE,
        description: '',
        fichiers: [],
      });
    }
    this.selectedElementKeys.set(newSet);
  }

  getElementById(id: number): ElementModule | undefined {
    return this.allElements().find(e => e.id === id);
  }

  getElementType(type: TypeNoteReclamation): string {
    return type === 'CONTINU' ? 'Continu (CC)' : 'Final (Examen)';
  }

  supprimerLigne(index: number): void {
    const elementId = this.lignes[index].element_module;
    const type = this.lignes[index].type_note;
    if (elementId) {
      this.selectedElementKeys.update(keys => {
        const newSet = new Set(keys);
        newSet.delete(`${elementId}_${type}`);
        return newSet;
      });
    }
    this.lignes.splice(index, 1);
  }

  onLigneFichiers(event: Event, index: number): void {
    const input = event.target as HTMLInputElement;
    if (input.files) {
      this.lignes[index].fichiers = Array.from(input.files);
    }
  }

  onSubmit(): void {
    // Validate all lines have required fields
    const invalidLine = this.lignes.find(l => !l.element_module || !l.motif);
    if (invalidLine) {
      this.error.set('Veuillez remplir tous les champs obligatoires pour chaque élément.');
      return;
    }

    this.submitting.set(true);
    this.error.set('');

    this.reclamationsService.createReclamation({
      description: this.description,
      lignes: this.lignes,
    }).subscribe({
      next: () => {
        this.submitting.set(false);
        this.success.set(true);
      },
      error: (err) => {
        this.submitting.set(false);
        if (err.error?.lignes) {
          this.error.set(err.error.lignes.join(' '));
        } else if (err.error?.detail) {
          this.error.set(err.error.detail);
        } else {
          this.error.set('Erreur lors de la soumission.');
        }
      },
    });
  }
}