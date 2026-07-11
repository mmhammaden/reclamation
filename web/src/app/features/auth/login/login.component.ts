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
              <div class="relative">
                <input
                  id="password"
                  [type]="showPassword() ? 'text' : 'password'"
                  [(ngModel)]="password"
                  name="password"
                  required
                  class="w-full px-4 py-2.5 pr-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition-colors"
                  placeholder="Entrez votre mot de passe"
                  autocomplete="current-password"
                />
                <button
                  type="button"
                  (click)="showPassword.set(!showPassword())"
                  class="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-400 hover:text-gray-600"
                  [attr.aria-label]="showPassword() ? 'Masquer le mot de passe' : 'Afficher le mot de passe'"
                >
                  @if (showPassword()) {
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 4.411m0 0L21 21" />
                    </svg>
                  } @else {
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                  }
                </button>
              </div>
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
  showPassword = signal(false);

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