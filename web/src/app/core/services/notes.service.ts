import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { ResultatSemestre, NoteListResponse } from '../models/note.model';

@Injectable({ providedIn: 'root' })
export class NotesService extends ApiService {
  private readonly endpoint = `${this.API}/notes`;

  getNotes(params?: { page?: number; search?: string }): Observable<NoteListResponse> {
    return this.http.get<NoteListResponse>(this.endpoint, {
      params: this.buildParams(params),
    });
  }

  getNote(id: number): Observable<ResultatSemestre> {
    return this.http.get<ResultatSemestre>(`${this.endpoint}/${id}/`);
  }
}