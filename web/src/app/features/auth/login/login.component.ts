import { Component, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../../core/auth/auth.service';
import { LoadingSpinnerComponent } from '../../../shared/components/loading-spinner/loading-spinner.component';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [FormsModule, LoadingSpinnerComponent],
  template: `
    <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-600 to-primary-900">
      <div class="w-full max-w-md">
        <div class="bg-white rounded-2xl shadow-2xl p-8">
          <!-- Header -->
          <div class="text-center mb-8">
            <h1 class="text-3xl font-bold text-gray-900">ISCAE</h1>
            <p class="text-gray-500 mt-2">Gestion des Réclamations</p>
          </div>

          <!-- Error Message -->
          @if (error()) {
            <div class="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
              {{ error() }}
            </div>
          }

          <!-- Login Form -->
          <form (ngSubmit)="onSubmit()" class="space-y-5">
            <div>
              <label for="matricule" class="block text-sm font-medium text-gray-700 mb-1">
                Matricule
              </label>
              <input
                id="matricule"
                type="text"
                [(ngModel)]="matricule"
                name="matricule"
                required
                class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition-colors"
                placeholder="Entrez votre matricule"
                autocomplete="username"
              />
            </div>

            <div>
              <label for="password" class="block text-sm font-medium text-gray-700 mb-1">
                Mot de passe
              </label>
              <input
                id="password"
                type="password"
                [(ngModel)]="password"
                name="password"
                required
                class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition-colors"
                placeholder="Entrez votre mot de passe"
                autocomplete="current-password"
              />
            </div>

            <button
              type="submit"
              [disabled]="loading()"
              class="w-full py-2.5 px-4 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              @if (loading()) {
                <app-loading-spinner size="sm" containerClass="py-0" color="white" />
              } @else {
                Se connecter
              }
            </button>
          </form>
        </div>
      </div>
    </div>
  `,
})
export class LoginComponent {
  matricule = '';
  password = '';
  loading = signal(false);
  error = signal('');

  constructor(
    private authService: AuthService,
    private router: Router,
  ) {
    // Redirect if already logged in
    if (this.authService.isAuthenticated()) {
      this.authService.redirectBasedOnRole();
    }
  }

  onSubmit(): void {
    if (!this.matricule || !this.password) {
      this.error.set('Veuillez remplir tous les champs.');
      return;
    }

    this.loading.set(true);
    this.error.set('');

    this.authService.login({ matricule: this.matricule, password: this.password }).subscribe({
      next: () => {
        this.loading.set(false);
        this.authService.redirectBasedOnRole();
      },
      error: (err) => {
        this.loading.set(false);
        if (err.status === 401) {
          this.error.set('Matricule ou mot de passe incorrect.');
        } else if (err.error?.detail) {
          this.error.set(err.error.detail);
        } else {
          this.error.set('Erreur de connexion. Veuillez réessayer.');
        }
      },
    });
  }
}