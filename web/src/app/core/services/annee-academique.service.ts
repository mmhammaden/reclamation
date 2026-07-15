import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';

export interface AnneeAcademique {
  id: number;
  annee: string;
  est_active: boolean;
  semestres_actifs: string;
  semestres_list: string[];
  date_creation: string;
}

@Injectable({ providedIn: 'root' })
export class AnneeAcademiqueService extends ApiService {
  private readonly endpoint = `${this.API}/admin/annee-academique`;

  getCurrent(): Observable<AnneeAcademique> {
    return this.http.get<AnneeAcademique>(`${this.endpoint}/current/`);
  }

  create(data: { annee: string; semestres_actifs: string }): Observable<AnneeAcademique> {
    return this.http.post<AnneeAcademique>(`${this.endpoint}/`, data);
  }

  update(id: number, data: Partial<{ semestres_actifs: string; est_active: boolean }>): Observable<AnneeAcademique> {
    return this.http.patch<AnneeAcademique>(`${this.endpoint}/${id}/`, data);
  }
}