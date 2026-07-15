import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { ApiService } from './api.service';
import { ResultatSemestre, NoteListResponse, ElementModule } from '../models/note.model';

function parseElement(e: ElementModule): ElementModule {
  return {
    ...e,
    note_continu: e.note_continu != null ? +e.note_continu : 0,
    note_final: e.note_final != null ? +e.note_final : 0,
    note_moyenne: e.note_moyenne != null ? +e.note_moyenne : 0,
    credit: e.credit != null ? +e.credit : 0,
  };
}

function parseResultat(r: ResultatSemestre): ResultatSemestre {
  return {
    ...r,
    moy_semestre: r.moy_semestre != null ? +r.moy_semestre : 0,
    elements: r.elements ? r.elements.map(parseElement) : [],
  };
}

@Injectable({ providedIn: 'root' })
export class NotesService extends ApiService {
  private readonly endpoint = `${this.API}/notes`;

  getNotes(params?: { page?: number; search?: string }): Observable<NoteListResponse> {
    return this.http.get<NoteListResponse>(`${this.endpoint}/`, {
      params: this.buildParams(params),
    }).pipe(map(res => ({ ...res, results: res.results.map(parseResultat) })));
  }

  getNote(id: number): Observable<ResultatSemestre> {
    return this.http.get<ResultatSemestre>(`${this.endpoint}/${id}/`)
      .pipe(map(parseResultat));
  }
}