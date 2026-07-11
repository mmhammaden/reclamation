import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';

export interface Notification {
  id: number;
  type_notification: string;
  contenu: string;
  est_lu: boolean;
  date_creation: string;
  date_lecture: string | null;
  reclamation: number;
}

@Injectable({ providedIn: 'root' })
export class NotificationsService extends ApiService {
  private readonly endpoint = `${this.API}/notifications`;

  getNotifications(): Observable<Notification[]> {
    return this.http.get<Notification[]>(this.endpoint);
  }

  getUnreadCount(): Observable<{ unread_count: number }> {
    return this.http.get<{ unread_count: number }>(`${this.endpoint}/unread-count/`);
  }

  markAsRead(id: number): Observable<Notification> {
    return this.http.patch<Notification>(`${this.endpoint}/${id}/read/`, {});
  }

  markAllAsRead(): Observable<void> {
    // Mark all unread notifications as read
    return new Observable(observer => {
      this.getNotifications().subscribe({
        next: (notifications) => {
          const unread = notifications.filter(n => !n.est_lu);
          let completed = 0;
          if (unread.length === 0) {
            observer.next();
            observer.complete();
            return;
          }
          unread.forEach(notification => {
            this.markAsRead(notification.id).subscribe({
              next: () => {
                completed++;
                if (completed === unread.length) {
                  observer.next();
                  observer.complete();
                }
              },
              error: (err) => observer.error(err),
            });
          });
        },
        error: (err) => observer.error(err),
      });
    });
  }
}