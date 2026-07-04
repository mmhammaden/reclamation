export enum StatutReclamation {
  EN_ATTENTE = 'EN_ATTENTE',
  EN_COURS = 'EN_COURS',
  ACCEPTEE = 'ACCEPTEE',
  REJETEE = 'REJETEE',
  ARCHIVEE = 'ARCHIVEE',
}

export enum MotifReclamation {
  ERREUR_SAISIE = 'ERREUR_SAISIE',
  OUBLI_NOTE = 'OUBLI_NOTE',
  VERIFICATION_COPIE = 'VERIFICATION_COPIE',
  AUTRE = 'AUTRE',
}

export interface ReclamationListItem {
  id: number;
  motif: MotifReclamation;
  statut: StatutReclamation;
  date_creation: string;
  date_limite_traitement: string;
  etudiant_matricule: string;
  etudiant_nom: string;
  code_module: string;
  est_en_retard: boolean;
}

export interface PieceJointe {
  id: number;
  fichier: string;
  nom_fichier: string;
  taille: number;
  date_ajout: string;
}

export interface HistoriqueStatut {
  id: number;
  statut_precedent: string | null;
  nouveau_statut: string;
  commentaire: string;
  modifie_par: number;
  modifie_par_nom: string;
  date_modification: string;
}

export interface ReclamationDetail {
  id: number;
  motif: MotifReclamation;
  statut: StatutReclamation;
  description: string;
  commentaire_decision: string;
  etudiant: number;
  etudiant_info: {
    matricule: string;
    nom: string;
    email: string;
  };
  note_elementaire: number;
  coordonnateur: number | null;
  date_creation: string;
  date_limite_traitement: string;
  date_traitement: string | null;
  note_originale: number | null;
  nouvelle_note: number | null;
  pieces_jointes: PieceJointe[];
  historique_statuts: HistoriqueStatut[];
  est_en_retard: boolean;
}

export interface ReclamationCreate {
  motif: MotifReclamation;
  description: string;
  note_elementaire: number;
  pieces_jointes?: File[];
}

export interface ReclamationDecision {
  commentaire_decision: string;
  nouvelle_note?: number;
}

export interface DashboardStats {
  total: number;
  en_attente: number;
  en_cours: number;
  en_retard: number;
  traitees: number;
  recentes: ReclamationListItem[];
}