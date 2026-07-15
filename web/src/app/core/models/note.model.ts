export type TypeNote = 'DEVOIR' | 'EXAMEN';

export type TypeNoteReclamation = 'CONTINU' | 'FINAL';

export interface ElementModule {
  id: number;
  code_element: string;
  nom_matiere: string;
  note_continu: number;
  note_final: number;
  note_moyenne: number;
  credit: number;
  observation: string;
}

export interface ResultatSemestre {
  id: number;
  moy_semestre: number;
  observation: string;
  semestre: string;
  annee_academique: string;
  elements: ElementModule[];
}

export interface NoteListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: ResultatSemestre[];
}