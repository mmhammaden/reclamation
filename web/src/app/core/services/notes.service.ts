import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { NoteElementaire, NoteListResponse } from '../models/note.model';

@Injectable({ providedIn: 'root' })
export class NotesService extends ApiService {
  private readonly endpoint = `${this.API}/notes`;

  getNotes(params?: { page?: number; search?: string }): Observable<NoteListResponse> {
    return this.http.get<NoteListResponse>(this.endpoint, {
      params: this.buildParams(params),
    });
  }

  getNote(id: number): Observable<NoteElementaire> {
    return this.http.get<NoteElementaire>(`${this.endpoint}/${id}/`);
  }
}