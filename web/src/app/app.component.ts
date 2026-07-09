import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { SidebarComponent } from './shared/components/sidebar/sidebar.component';
import { AuthService } from './core/auth/auth.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, SidebarComponent],
  template: `
    <!-- Skip Link for Accessibility -->
    <a href="#main-content" class="skip-to-content-link absolute -top-10 left-0 bg-primary-700 text-white px-4 py-2 rounded-br-lg transition-transform focus:top-0 z-50">
      Passer au contenu principal
    </a>

    <div class="flex min-h-screen">
      @if (authService.isAuthenticated()) {
        <app-sidebar />
        <main class="flex-1 p-8 bg-gray-50" id="main-content">
          <router-outlet />
        </main>
      } @else {
        <main class="flex-1" id="main-content">
          <router-outlet />
        </main>
      }
    </div>
  `,
})
export class AppComponent {
  constructor(public authService: AuthService) {}
}