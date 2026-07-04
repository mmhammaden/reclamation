import { Component, Input } from '@angular/core';
import { StatutReclamation } from '../../../core/models/reclamation.model';

@Component({
  selector: 'app-badge',
  standalone: true,
  template: `
    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
          [class]="badgeClass">
      {{ label }}
    </span>
  `,
})
export class BadgeComponent {
  @Input() statut!: StatutReclamation;

  get label(): string {
    const labels: Record<string, string> = {
      EN_ATTENTE: 'En attente',
      EN_COURS: 'En cours',
      ACCEPTEE: 'Acceptée',
      REJETEE: 'Rejetée',
      ARCHIVEE: 'Archivée',
    };
    return labels[this.statut] || this.statut;
  }

  get badgeClass(): string {
    const classes: Record<string, string> = {
      EN_ATTENTE: 'bg-yellow-100 text-yellow-800',
      EN_COURS: 'bg-blue-100 text-blue-800',
      ACCEPTEE: 'bg-green-100 text-green-800',
      REJETEE: 'bg-red-100 text-red-800',
      ARCHIVEE: 'bg-gray-100 text-gray-800',
    };
    return classes[this.statut] || 'bg-gray-100 text-gray-800';
  }
}