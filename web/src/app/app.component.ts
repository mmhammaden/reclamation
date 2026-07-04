import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { SidebarComponent } from './shared/components/sidebar/sidebar.component';
import { AuthService } from './core/auth/auth.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, SidebarComponent],
  template: `
    <div class="flex min-h-screen">
      @if (authService.isAuthenticated()) {
        <app-sidebar />
        <main class="flex-1 p-8 bg-gray-50">
          <router-outlet />
        </main>
      } @else {
        <main class="flex-1">
          <router-outlet />
        </main>
      }
    </div>
  `,
})
export class AppComponent {
  constructor(public authService: AuthService) {}
}