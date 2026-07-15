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
  private readonly endpoint = `${this.API}/notifications/`;

  getNotifications(): Observable<Notification[]> {
    return this.http.get<Notification[]>(this.endpoint);
  }

  getUnreadCount(): Observable<{ unread_count: number }> {
    return this.http.get<{ unread_count: number }>(`${this.endpoint}unread-count/`);
  }

  markAsRead(id: number): Observable<Notification> {
    return this.http.patch<Notification>(`${this.endpoint}${id}/read/`, {});
  }

  markAllAsRead(): Observable<void> {
    return this.http.post<void>(`${this.endpoint}mark-all-read/`, {});
  }
}