import { Component, computed } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { AuthService } from '../../../core/auth/auth.service';
import { Role } from '../../../core/models/user.model';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [RouterLink, RouterLinkActive],
  template: `
    <aside class="w-64 bg-white border-r border-gray-200 min-h-screen flex flex-col">
      <!-- Logo -->
      <div class="p-6 border-b border-gray-200">
        <h1 class="text-xl font-bold text-primary-700">ISCAE</h1>
        <p class="text-sm text-gray-500">Gestion des Réclamations</p>
      </div>

      <!-- User Info -->
      <div class="px-6 py-4 border-b border-gray-100 bg-gray-50">
        <p class="text-sm font-medium text-gray-900">{{ currentUser()?.first_name }} {{ currentUser()?.last_name }}</p>
        <p class="text-xs text-gray-500">{{ currentUser()?.matricule }}</p>
        <span class="inline-block mt-1 px-2 py-0.5 text-xs font-medium rounded-full"
              [class]="roleBadgeClass()">
          {{ roleLabel() }}
        </span>
      </div>

      <!-- Navigation -->
      <nav class="flex-1 p-4 space-y-1">
        @for (item of menuItems(); track item.path) {
          <a [routerLink]="item.path"
             routerLinkActive="bg-primary-50 text-primary-700 border-l-4 border-primary-600"
             class="flex items-center gap-3 px-3 py-2.5 text-sm font-medium rounded-lg
                    text-gray-600 hover:bg-gray-100 transition-colors min-h-[44px]">
            <span class="text-lg">{{ item.icon }}</span>
            <span>{{ item.label }}</span>
          </a>
        }
      </nav>

      <!-- Logout -->
      <div class="p-4 border-t border-gray-200">
        <button (click)="logout()"
                class="flex items-center gap-3 w-full px-3 py-2.5 text-sm font-medium text-red-600
                       hover:bg-red-50 rounded-lg transition-colors min-h-[44px]">
          <span class="text-lg">🚪</span>
          <span>Déconnexion</span>
        </button>
      </div>
    </aside>
  `,
})
export class SidebarComponent {
  currentUser = this.authService.currentUser;

  constructor(private authService: AuthService) {}

  roleLabel = computed(() => {
    const role = this.authService.userRole();
    const labels: Record<string, string> = {
      ETUDIANT: 'Étudiant',
      COORDINATEUR: 'Coordinateur',
      ADMIN: 'Administrateur',
      ENSEIGNANT: 'Enseignant',
    };
    return role ? labels[role] || role : '';
  });

  roleBadgeClass = computed(() => {
    const role = this.authService.userRole();
    const classes: Record<string, string> = {
      ETUDIANT: 'bg-blue-100 text-blue-800',
      COORDINATEUR: 'bg-purple-100 text-purple-800',
      ADMIN: 'bg-red-100 text-red-800',
      ENSEIGNANT: 'bg-green-100 text-green-800',
    };
    return role ? classes[role] || '' : '';
  });

  menuItems = computed(() => {
    const role = this.authService.userRole();
    const items: { path: string; label: string; icon: string }[] = [];

    switch (role) {
      case Role.ETUDIANT:
        items.push(
          { path: '/etudiant/mes-notes', label: 'Mes Notes', icon: '📊' },
          { path: '/etudiant/mes-reclamations', label: 'Mes Réclamations', icon: '📋' },
          { path: '/etudiant/nouvelle-reclamation', label: 'Nouvelle Réclamation', icon: '➕' },
          { path: '/etudiant/change-password', label: 'Changer mot de passe', icon: '🔑' },
        );
        break;
      case Role.COORDINATEUR:
        items.push(
          { path: '/coordinateur/dashboard', label: 'Tableau de Bord', icon: '📈' },
          { path: '/coordinateur/reclamations', label: 'Réclamations', icon: '📋' },
          { path: '/coordinateur/change-password', label: 'Changer mot de passe', icon: '🔑' },
        );
        break;
      case Role.ADMIN:
        items.push(
          { path: '/admin/users', label: 'Utilisateurs', icon: '👥' },
          { path: '/admin/import-pv', label: 'Import PV', icon: '📄' },
          { path: '/admin/change-password', label: 'Changer mot de passe', icon: '🔑' },
        );
        break;
      case Role.ENSEIGNANT:
        items.push(
          { path: '/enseignant/reclamations', label: 'Réclamations', icon: '📋' },
          { path: '/enseignant/change-password', label: 'Changer mot de passe', icon: '🔑' },
        );
        break;
    }
    return items;
  });

  logout(): void {
    this.authService.logout();
  }
}