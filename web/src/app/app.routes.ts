import { Routes } from '@angular/router';
import { authGuard } from './core/auth/auth.guard';
import { Role } from './core/models/user.model';

export const routes: Routes = [
  {
    path: 'login',
    loadComponent: () =>
      import('./features/auth/login/login.component').then((m) => m.LoginComponent),
  },
  {
    path: 'etudiant',
    canActivate: [authGuard],
    data: { roles: [Role.ETUDIANT] },
    children: [
      {
        path: 'mes-notes',
        loadComponent: () =>
          import('./features/etudiant/mes-notes/mes-notes.component').then((m) => m.MesNotesComponent),
      },
      {
        path: 'mes-reclamations',
        loadComponent: () =>
          import('./features/etudiant/mes-reclamations/mes-reclamations.component').then(
            (m) => m.MesReclamationsComponent,
          ),
      },
      {
        path: 'reclamations/:id',
        loadComponent: () =>
          import('./features/coordinateur/reclamation-detail/reclamation-detail.component').then(
            (m) => m.ReclamationDetailComponent,
          ),
      },
      {
        path: 'nouvelle-reclamation',
        loadComponent: () =>
          import('./features/etudiant/nouvelle-reclamation/nouvelle-reclamation.component').then(
            (m) => m.NouvelleReclamationComponent,
          ),
      },
      {
        path: 'change-password',
        loadComponent: () =>
          import('./shared/components/change-password/change-password.component').then(
            (m) => m.ChangePasswordComponent,
          ),
      },
      { path: '', redirectTo: 'mes-notes', pathMatch: 'full' },
    ],
  },
  {
    path: 'coordinateur',
    canActivate: [authGuard],
    data: { roles: [Role.COORDINATEUR] },
    children: [
      {
        path: 'dashboard',
        loadComponent: () =>
          import('./features/coordinateur/dashboard/dashboard.component').then(
            (m) => m.DashboardComponent,
          ),
      },
      {
        path: 'reclamations',
        loadComponent: () =>
          import('./features/coordinateur/reclamations-list/reclamations-list.component').then(
            (m) => m.ReclamationsListComponent,
          ),
      },
      {
        path: 'reclamations/:id',
        loadComponent: () =>
          import('./features/coordinateur/reclamation-detail/reclamation-detail.component').then(
            (m) => m.ReclamationDetailComponent,
          ),
      },
      {
        path: 'change-password',
        loadComponent: () =>
          import('./shared/components/change-password/change-password.component').then(
            (m) => m.ChangePasswordComponent,
          ),
      },
      { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
    ],
  },
  {
    path: 'admin',
    canActivate: [authGuard],
    data: { roles: [Role.ADMIN] },
    children: [
      {
        path: 'users',
        loadComponent: () =>
          import('./features/admin/users/users.component').then((m) => m.UsersComponent),
      },
      {
        path: 'import-pv',
        loadComponent: () =>
          import('./features/admin/import-pv/import-pv.component').then((m) => m.ImportPvComponent),
      },
      {
        path: 'change-password',
        loadComponent: () =>
          import('./shared/components/change-password/change-password.component').then(
            (m) => m.ChangePasswordComponent,
          ),
      },
      { path: '', redirectTo: 'users', pathMatch: 'full' },
    ],
  },
  {
    path: 'enseignant',
    canActivate: [authGuard],
    data: { roles: [Role.ENSEIGNANT] },
    children: [
      {
        path: 'reclamations',
        loadComponent: () =>
          import('./features/enseignant/reclamations/reclamations.component').then(
            (m) => m.ReclamationsComponent,
          ),
      },
      {
        path: 'change-password',
        loadComponent: () =>
          import('./shared/components/change-password/change-password.component').then(
            (m) => m.ChangePasswordComponent,
          ),
      },
      { path: '', redirectTo: 'reclamations', pathMatch: 'full' },
    ],
  },
  { path: '', redirectTo: 'login', pathMatch: 'full' },
  { path: '**', redirectTo: 'login' },
];