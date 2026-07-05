import { Component, signal, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { UsersService } from '../../../core/services/users.service';
import { User, UserCreate, Role } from '../../../core/models/user.model';
import { LoadingSpinnerComponent } from '../../../shared/components/loading-spinner/loading-spinner.component';

@Component({
  selector: 'app-users',
  standalone: true,
  imports: [FormsModule, LoadingSpinnerComponent],
  template: `
    <div class="max-w-6xl mx-auto">
      <div class="flex items-center justify-between mb-6">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">Gestion des Utilisateurs</h1>
          <p class="text-gray-500 mt-1">Créez et gérez les comptes utilisateurs.</p>
        </div>
        <button (click)="showForm.set(true)"
                class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors">
          + Nouvel utilisateur
        </button>
      </div>

      @if (error()) {
        <div class="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">{{ error() }}</div>
      }

      <!-- Create User Form -->
      @if (showForm()) {
        <div class="bg-white rounded-lg border border-gray-200 p-6 mb-6">
          <h2 class="font-semibold text-gray-900 mb-4">Créer un utilisateur</h2>
          <form (ngSubmit)="onCreate()" class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Matricule</label>
              <input type="text" [(ngModel)]="formData.matricule" name="matricule" required
                     class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <input type="email" [(ngModel)]="formData.email" name="email" required
                     class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Prénom</label>
              <input type="text" [(ngModel)]="formData.first_name" name="first_name" required
                     class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Nom</label>
              <input type="text" [(ngModel)]="formData.last_name" name="last_name" required
                     class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Rôle</label>
              <select [(ngModel)]="formData.role" name="role" required
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none">
                <option value="ETUDIANT">Étudiant</option>
                <option value="COORDINATEUR">Coordinateur</option>
                <option value="ADMIN">Administrateur</option>
                <option value="ENSEIGNANT">Enseignant</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Mot de passe</label>
              <input type="password" [(ngModel)]="password" name="password" required
                     class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none" />
            </div>
            <div class="col-span-2 flex items-center gap-3 pt-2">
              <button type="submit" [disabled]="submitting()"
                      class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50">
                Créer
              </button>
              <button type="button" (click)="showForm.set(false)"
                      class="px-4 py-2 text-gray-700 hover:text-gray-900">
                Annuler
              </button>
            </div>
          </form>
        </div>
      }

      <!-- Users Table -->
      @if (loading()) {
        <app-loading-spinner text="Chargement des utilisateurs..." />
      } @else {
        <div class="bg-white rounded-lg border border-gray-200 overflow-hidden">
          <table class="w-full">
            <thead class="bg-gray-50">
              <tr>
                <th class="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase">Matricule</th>
                <th class="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase">Nom</th>
                <th class="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase">Email</th>
                <th class="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase">Rôle</th>
                <th class="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase">Actif</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200">
              @for (user of users(); track user.id) {
                <tr class="hover:bg-gray-50">
                  <td class="px-4 py-3 text-sm font-medium text-gray-900">{{ user.matricule }}</td>
                  <td class="px-4 py-3 text-sm text-gray-600">{{ user.first_name }} {{ user.last_name }}</td>
                  <td class="px-4 py-3 text-sm text-gray-600">{{ user.email }}</td>
                  <td class="px-4 py-3">
                    <span class="inline-flex px-2 py-0.5 text-xs font-medium rounded-full"
                          [class]="roleBadgeClass(user.role)">
                      {{ roleLabel(user.role) }}
                    </span>
                  </td>
                  <td class="px-4 py-3">
                    <span [class.text-green-600]="user.is_active" [class.text-red-600]="!user.is_active">
                      {{ user.is_active ? 'Oui' : 'Non' }}
                    </span>
                  </td>
                </tr>
              }
            </tbody>
          </table>
        </div>
      }
    </div>
  `,
})
export class UsersComponent {
  private usersService = inject(UsersService);
  users = signal<User[]>([]);
  loading = signal(true);
  error = signal('');
  showForm = signal(false);
  submitting = signal(false);
  
  // Separate password from form data to avoid storing credentials with user data
  password = '';
  
  formData: Omit<UserCreate, 'password'> = {
    matricule: '',
    email: '',
    role: Role.ETUDIANT,
    first_name: '',
    last_name: '',
  };

  constructor() {
    this.loadUsers();
  }

  roleLabel(role: string): string {
    const labels: Record<string, string> = {
      ETUDIANT: 'Étudiant',
      COORDINATEUR: 'Coordinateur',
      ADMIN: 'Administrateur',
      ENSEIGNANT: 'Enseignant',
    };
    return labels[role] || role;
  }

  roleBadgeClass(role: string): string {
    const classes: Record<string, string> = {
      ETUDIANT: 'bg-blue-100 text-blue-800',
      COORDINATEUR: 'bg-purple-100 text-purple-800',
      ADMIN: 'bg-red-100 text-red-800',
      ENSEIGNANT: 'bg-green-100 text-green-800',
    };
    return classes[role] || '';
  }

  onCreate(): void {
    this.submitting.set(true);
    // Combine form data with password for API call only
    const userData: UserCreate = {
      ...this.formData,
      password: this.password,
    };
    this.usersService.createUser(userData).subscribe({
      next: () => {
        this.submitting.set(false);
        this.showForm.set(false);
        // Clear form data and password immediately after successful creation
        this.formData = { matricule: '', email: '', role: Role.ETUDIANT, first_name: '', last_name: '' };
        this.password = '';
        this.loadUsers();
      },
      error: (err) => {
        this.submitting.set(false);
        this.error.set(err.error?.detail || 'Erreur lors de la création.');
      },
    });
  }

  private loadUsers(): void {
    this.usersService.getUsers().subscribe({
      next: (response) => {
        this.users.set(response.results);
        this.loading.set(false);
      },
      error: () => {
        this.error.set('Erreur lors du chargement.');
        this.loading.set(false);
      },
    });
  }
}