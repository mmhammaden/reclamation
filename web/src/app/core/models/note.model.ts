export interface NoteElementaire {
  id: number;
  code_module: string;
  libelle_module: string;
  valeur_note: number;
  note_sur: number;
  semestre: string;
  annee_academique: string;
  date_saisie: string;
  est_verifiee: boolean;
}

export interface NoteListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: NoteElementaire[];
}