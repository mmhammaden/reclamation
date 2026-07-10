import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { UsersService } from '../../../core/services/users.service';

@Component({
  selector: 'app-change-password',
  standalone: true,
  imports: [FormsModule],
  template: `
    <div class="max-w-md mx-auto mt-10 bg-white p-8 rounded-xl shadow">
      <h2 class="text-xl font-bold text-gray-800 mb-6">Changer le mot de passe</h2>

      @if (success()) {
        <div class="mb-4 p-3 bg-green-50 text-green-700 rounded-lg text-sm">
          Mot de passe modifié avec succès.
        </div>
      }
      @if (error()) {
        <div class="mb-4 p-3 bg-red-50 text-red-700 rounded-lg text-sm">{{ error() }}</div>
      }

      <form (ngSubmit)="submit()" #f="ngForm" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Ancien mot de passe</label>
          <input type="password" name="oldPassword" [(ngModel)]="oldPassword" required
                 class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Nouveau mot de passe</label>
          <input type="password" name="newPassword" [(ngModel)]="newPassword" required minlength="8"
                 class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Confirmer le mot de passe</label>
          <input type="password" name="confirmPassword" [(ngModel)]="confirmPassword" required
                 class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" />
        </div>
        <button type="submit" [disabled]="loading() || f.invalid"
                class="w-full bg-primary-600 text-white py-2 rounded-lg text-sm font-medium hover:bg-primary-700 disabled:opacity-50 transition-colors">
          {{ loading() ? 'Enregistrement...' : 'Modifier le mot de passe' }}
        </button>
      </form>
    </div>
  `,
})
export class ChangePasswordComponent {
  private usersService = inject(UsersService);

  oldPassword = '';
  newPassword = '';
  confirmPassword = '';
  loading = signal(false);
  success = signal(false);
  error = signal('');

  submit(): void {
    if (this.newPassword !== this.confirmPassword) {
      this.error.set('Les mots de passe ne correspondent pas.');
      return;
    }
    this.loading.set(true);
    this.error.set('');
    this.success.set(false);
    this.usersService.changePassword(this.oldPassword, this.newPassword).subscribe({
      next: () => {
        this.success.set(true);
        this.oldPassword = this.newPassword = this.confirmPassword = '';
        this.loading.set(false);
      },
      error: (err) => {
        this.error.set(err.error?.old_password || err.error?.detail || 'Une erreur est survenue.');
        this.loading.set(false);
      },
    });
  }
}