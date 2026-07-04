import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import {
  ReclamationListItem,
  ReclamationDetail,
  ReclamationCreate,
  ReclamationDecision,
  DashboardStats,
} from '../models/reclamation.model';

@Injectable({ providedIn: 'root' })
export class ReclamationsService extends ApiService {
  private readonly endpoint = `${this.API}/reclamations`;

  // Student endpoints
  getMyReclamations(params?: { page?: number }): Observable<{ count: number; results: ReclamationListItem[] }> {
    return this.http.get<{ count: number; results: ReclamationListItem[] }>(this.endpoint, {
      params: this.buildParams(params),
    });
  }

  getReclamation(id: number): Observable<ReclamationDetail> {
    return this.http.get<ReclamationDetail>(`${this.endpoint}/${id}/`);
  }

  createReclamation(data: ReclamationCreate): Observable<ReclamationDetail> {
    const formData = new FormData();
    formData.append('motif', data.motif);
    formData.append('description', data.description);
    formData.append('note_elementaire', String(data.note_elementaire));
    if (data.pieces_jointes) {
      data.pieces_jointes.forEach((file) => formData.append('pieces_jointes', file));
    }
    return this.http.post<ReclamationDetail>(`${this.endpoint}/create/`, formData);
  }

  deleteReclamation(id: number): Observable<void> {
    return this.http.delete<void>(`${this.endpoint}/${id}/delete/`);
  }

  // Coordinator endpoints
  traiterReclamation(id: number): Observable<ReclamationDetail> {
    return this.http.patch<ReclamationDetail>(`${this.API}/coordinator/reclamations/${id}/traiter/`, {});
  }

  getDashboard(): Observable<DashboardStats> {
    return this.http.get<DashboardStats>(`${this.API}/coordinator/dashboard/`);
  }

  getPendingReclamations(params?: { page?: number; statut?: string }): Observable<{ count: number; results: ReclamationListItem[] }> {
    return this.http.get<{ count: number; results: ReclamationListItem[] }>(`${this.API}/coordinator/reclamations/`, {
      params: this.buildParams(params),
    });
  }

  accepterReclamation(id: number, data: ReclamationDecision): Observable<ReclamationDetail> {
    return this.http.post<ReclamationDetail>(`${this.API}/coordinator/reclamations/${id}/accepter/`, data);
  }

  rejeterReclamation(id: number, data: ReclamationDecision): Observable<ReclamationDetail> {
    return this.http.post<ReclamationDetail>(`${this.API}/coordinator/reclamations/${id}/rejeter/`, data);
  }

  // Admin endpoints
  importPV(formData: FormData): Observable<{ detail: string }> {
    return this.http.post<{ detail: string }>(`${this.API}/admin/import-pv/`, formData);
  }

  forceUnblockNote(reclamationId: number): Observable<{ detail: string }> {
    return this.http.post<{ detail: string }>(`${this.API}/admin/reclamations/${reclamationId}/force-unblock/`, {});
  }

  getRapports(params?: { format?: string }): Observable<Blob> {
    return this.http.get(`${this.API}/admin/rapports/`, {
      params: this.buildParams(params),
      responseType: 'blob',
    });
  }

  // Teacher endpoints
  getTeacherReclamations(params?: { page?: number }): Observable<{ count: number; results: ReclamationListItem[] }> {
    return this.http.get<{ count: number; results: ReclamationListItem[] }>(`${this.API}/teacher/reclamations/`, {
      params: this.buildParams(params),
    });
  }
}