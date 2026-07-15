import { Component, signal, inject, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NotificationsService, Notification } from '../../../core/services/notifications.service';
import { AuthService } from '../../../core/auth/auth.service';
import { LoadingSpinnerComponent } from '../loading-spinner/loading-spinner.component';

@Component({
  selector: 'app-notification-bell',
  standalone: true,
  imports: [CommonModule, LoadingSpinnerComponent],
  template: `
    <div class="relative">
      <!-- Bell Icon -->
      <button (click)="toggleDropdown()" class="relative p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors">
        <span class="text-xl">🔔</span>
        @if (unreadCount() > 0) {
          <span class="absolute top-1 right-1 inline-flex items-center justify-center px-1.5 py-0.5 text-xs font-bold leading-none text-white bg-red-600 rounded-full">
            {{ unreadCount() > 99 ? '99+' : unreadCount() }}
          </span>
        }
      </button>

      <!-- Dropdown -->
      @if (dropdownOpen()) {
        <div class="absolute right-0 mt-2 w-96 bg-white rounded-lg shadow-lg border border-gray-200 z-50 max-h-[500px] flex flex-col">
          <!-- Header -->
          <div class="px-4 py-3 border-b border-gray-200 flex items-center justify-between">
            <h3 class="text-sm font-semibold text-gray-900">Notifications</h3>
            @if (unreadCount() > 0) {
              <button (click)="markAllAsRead()" [disabled]="markingAllRead()" class="text-xs text-primary-600 hover:text-primary-700 disabled:opacity-50">
                @if (markingAllRead()) {
                  <app-loading-spinner size="sm" containerClass="py-0" />
                } @else {
                  Tout marquer comme lu
                }
              </button>
            }
          </div>

          <!-- Notifications List -->
          <div class="overflow-y-auto flex-1">
            @if (loading()) {
              <div class="p-4 flex justify-center">
                <app-loading-spinner />
              </div>
            } @else if (notifications().length === 0) {
              <div class="p-4 text-center text-sm text-gray-500">
                Aucune notification
              </div>
            } @else {
              @for (notification of notifications(); track notification.id) {
                <div (click)="onNotificationClick(notification)"
                     [class.bg-blue-50]="!notification.est_lu"
                     [class.bg-white]="notification.est_lu"
                     class="px-4 py-3 border-b border-gray-100 hover:bg-gray-50 cursor-pointer transition-colors">
                  <p class="text-sm text-gray-900" [class.font-medium]="!notification.est_lu">
                    {{ notification.contenu }}
                  </p>
                  <p class="text-xs text-gray-500 mt-1">
                    {{ notification.date_creation | date:'short' }}
                  </p>
                </div>
              }
            }
          </div>
        </div>
      }
    </div>
  `,
})
export class NotificationBellComponent implements OnInit, OnDestroy {
  private notificationsService = inject(NotificationsService);
  private authService = inject(AuthService);

  dropdownOpen = signal(false);
  notifications = signal<Notification[]>([]);
  unreadCount = signal(0);
  loading = signal(false);
  markingAllRead = signal(false);
  private pollInterval?: ReturnType<typeof setInterval>;

  ngOnInit(): void {
    this.loadUnreadCount();
    this.pollInterval = setInterval(() => this.loadUnreadCount(), 30000);
  }

  ngOnDestroy(): void {
    clearInterval(this.pollInterval);
  }

  toggleDropdown(): void {
    const isOpen = this.dropdownOpen();
    this.dropdownOpen.set(!isOpen);
    if (!isOpen) {
      this.loadNotifications();
    }
  }

  private loadNotifications(): void {
    this.loading.set(true);
    this.notificationsService.getNotifications().subscribe({
      next: (notifications) => {
        this.notifications.set(notifications);
        this.loading.set(false);
        this.updateUnreadCount(notifications);
      },
      error: () => {
        this.loading.set(false);
      },
    });
  }

  private loadUnreadCount(): void {
    this.notificationsService.getUnreadCount().subscribe({
      next: (response) => {
        this.unreadCount.set(response.unread_count);
      },
    });
  }

  private updateUnreadCount(notifications: Notification[]): void {
    this.unreadCount.set(notifications.filter(n => !n.est_lu).length);
  }

  markAllAsRead(): void {
    this.markingAllRead.set(true);
    this.notificationsService.markAllAsRead().subscribe({
      next: () => {
        this.notifications.update(notifications =>
          notifications.map(n => ({ ...n, est_lu: true }))
        );
        this.unreadCount.set(0);
        this.markingAllRead.set(false);
      },
      error: () => {
        this.markingAllRead.set(false);
      },
    });
  }

  onNotificationClick(notification: Notification): void {
    if (!notification.est_lu) {
      this.notificationsService.markAsRead(notification.id).subscribe({
        next: (updated) => {
          this.notifications.update(notifications =>
            notifications.map(n => n.id === updated.id ? updated : n)
          );
          this.updateUnreadCount(this.notifications());
        },
      });
    }

    // Navigate to reclamation if available
    if (notification.reclamation) {
      // Determine role and navigate accordingly
      const role = this.authService.userRole();
      let path = '/';
      if (role === 'ETUDIANT') {
        path = `/etudiant/mes-reclamations`;
      } else if (role === 'COORDINATEUR') {
        path = `/coordinateur/reclamations`;
      } else if (role === 'ENSEIGNANT') {
        path = `/enseignant/reclamations`;
      } else if (role === 'ADMIN') {
        path = `/admin/import-pv`;
      }
      window.location.href = `${path}#/reclamation/${notification.reclamation}`;
    }

    this.dropdownOpen.set(false);
  }
}