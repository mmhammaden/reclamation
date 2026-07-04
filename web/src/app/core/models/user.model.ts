export enum Role {
  ETUDIANT = 'ETUDIANT',
  COORDINATEUR = 'COORDINATEUR',
  ADMIN = 'ADMIN',
  ENSEIGNANT = 'ENSEIGNANT',
}

export interface User {
  id: number;
  matricule: string;
  email: string;
  role: Role;
  first_name: string;
  last_name: string;
  telephone: string;
  is_active: boolean;
}

export interface LoginRequest {
  matricule: string;
  password: string;
}

export interface LoginResponse {
  access: string;
  refresh: string;
  user: {
    id: number;
    matricule: string;
    email: string;
    role: Role;
    nom: string;
  };
}

export interface UserCreate {
  matricule: string;
  email: string;
  role: Role;
  first_name: string;
  last_name: string;
  telephone?: string;
  password: string;
}