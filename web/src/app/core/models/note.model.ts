export type TypeNote = 'DEVOIR' | 'EXAMEN';

export type TypeNoteReclamation = 'CONTINU' | 'FINAL';

export interface ElementModule {
  id: number;
  code_element: string;
  nom_element: string;
  note_continu: number;
  note_final: number;
  note_moyenne: number;
  credit: number;
  observation: string;
}

export interface Module {
  id: number;
  code_module: string;
  nom_module: string;
  moy_module: number;
  note_finale: number;
  credit: number;
  observation: string;
  elements: ElementModule[];
}

export interface ResultatSemestre {
  id: number;
  moy_semestre: number;
  observation: string;
  semestre: string;
  annee_academique: string;
  modules: Module[];
}

export interface NoteListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: ResultatSemestre[];
}