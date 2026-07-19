# Plateforme de Gestion des Réclamations ISCAE

Application web pour la gestion et le suivi des réclamations pédagogiques à l'ISCAE.

## Architecture

```
reclamationsProject/
├── backend/          # Django + DRF API
│   ├── config/       # Settings, URLs, WSGI
│   ├── apps/
│   │   ├── users/        # User & Auth
│   │   ├── notes/        # NoteElementaire (import)
│   │   ├── reclamations/ # Core business logic
│   │   ├── audit/        # AuditLog (immutable)
│   │   └── notifications/# in-app
│   ├── manage.py
│   └── requirements.txt
├── web/              # Angular app
│   ├── src/
│   │   ├── app/
│   │   │   ├── core/     # Services, models, guards
│   │   │   ├── features/ # Admin, auth, coordinateur, etudiant, enseignant
│   │   │   └── shared/   # Components
│   │   └── main.ts
│   └── angular.json
├── mobile/           # Flutter app
│   ├── lib/
│   │   ├── features/     # Notes, reclamations, auth, notifications
│   │   ├── models/       # Data models
│   │   ├── providers/    # Riverpod state management
│   │   ├── services/     # API services
│   │   └── widgets/      # Shared components
│   ├── pubspec.yaml
│   └── assets/           # Images, icons
├── nginx/            # Nginx config
├── docker-compose.yml
└── .env.example
```

## Stack Technique

| Couche | Technologie |
|--------|------------|
| Backend | Django 5.1 + DRF 3.15 |
| Base de données | PostgreSQL 15 |
| Cache / Blacklist | Redis 7 |
| Auth | JWT (access 15min / refresh 7j) |
| Web | Angular 18 (TypeScript) - Standalone components, Signals |
| Mobile | Flutter 3.12+ (Dart) - Riverpod, Material Design |
| Notifications | In-app |
| Déploiement | Docker Compose |

## Règles de Gestion Implémentées

- **RG-01**: Délai de traitement 72h - `date_limite_traitement` auto-set, dashboard avec compteur "En retard"
- **RG-02**: Unicité des demandes - Validation serializer, blocage soumission si réclamation active existe
- **RG-03**: Gestion des conflits - Blocage si note déjà modifiée, message "Contactez la scolarité"

## API Endpoints

### Auth (`/api/auth/`)
- `POST /login/` - Authentification (matricule + password) → JWT
- `POST /refresh/` - Rafraîchir access token
- `POST /logout/` - Blacklist refresh token
- `GET /me/` - Profil utilisateur

### Étudiant (`/api/`)
- `GET /notes/` - Mes notes
- `POST /reclamations/create/` - Nouvelle réclamation
- `GET /reclamations/` - Mes réclamations
- `GET /reclamations/{id}/` - Détail + historique
- `DELETE /reclamations/{id}/delete/` - Annulation

### Coordinateur (`/api/coordinator/`)
- `GET /dashboard/` - Statistiques par statut
- `GET /reclamations/` - Liste toutes les réclamations
- `PATCH /reclamations/{id}/traiter/` - Passer en cours
- `POST /reclamations/{id}/accepter/` - Accepter (audit + notif)
- `POST /reclamations/{id}/rejeter/` - Rejeter (notif)

### Administrateur (`/api/admin/`)
- `GET/POST /users/` - CRUD utilisateurs
- `POST /import-pv/` - Import notes CSV/XLSX
- `GET /rapports/` - Export statistiques

### Enseignant (`/api/teacher/`)
- `GET /reclamations/` - Consultation (read-only)

## Démarrage Rapide

### Avec Docker (recommandé)
```bash
# Cloner le projet
cd reclamationsProject

# Copier et configurer les variables d'environnement
cp .env.example .env

# Lancer les services
docker-compose up --build

# Créer un superutilisateur
docker-compose exec backend python manage.py createsuperuser
```

### Sans Docker (développement)
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate sur Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# Web (Angular)
cd web
npm install
ng serve


## Modèles de Données

- **User**: matricule, role (ETUDIANT/COORDINATEUR/ADMIN/ENSEIGNANT), email
- **NoteElementaire**: code_module, valeur_note, semestre, annee_academique
- **Reclamation**: motif, statut (EN_ATTENTE/EN_COURS/ACCEPTEE/REJETEE/ARCHIVEE), date_limite_traitement
- **PieceJointe**: fichier, nom_fichier (<<extend>>)
- **HistoriqueStatut**: statut_precedent, nouveau_statut (écrit à chaque transition)
- **AuditLog**: ancienne_valeur, nouvelle_valeur (immuable)
- **Notification**: contenu, est_lu, type (ACCEPTATION/REJET)

## Sécurité

- JWT access token stocké en mémoire (pas localStorage) pour mitiguer XSS
- Refresh token dans httpOnly cookie (backend)
- Sanitization des logs d'erreur
- Intercepteur JWT avec prévention de boucle infinie
- Validation des permissions par rôle (auth guard)

## Fonctionnalités

### Web (Angular)
- Authentification JWT avec refresh automatique
- Dashboard coordinateur avec statistiques
- Liste paginée des réclamations
- Détail réclamation avec historique
- Prise en charge, acceptation, rejet avec commentaire
- Suppression de réclamation (étudiant)
- Import PV (admin)
- Export rapports (admin)

### Mobile (Flutter)
- Authentification JWT avec matricule et mot de passe
- Consultation des notes par semestre
- Création et suivi des réclamations
- Notifications en temps réel
- Support hors-ligne avec cache local (Hive)
- Interface Material Design adaptée

## Tests

```bash
# Backend
cd backend
python manage.py test

# Web
cd web
ng test
