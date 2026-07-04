# Plateforme de Gestion des Réclamations ISCAE

Application multi-plateforme pour la gestion et le suivi des réclamations pédagogiques à l'ISCAE.

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
│   │   └── notifications/# FCM + in-app
│   ├── manage.py
│   └── requirements.txt
├── mobile/           # Flutter app
│   ├── lib/
│   │   ├── core/     # Dio client, models, secure storage
│   │   ├── features/ # Auth, notes, reclamations, notifications
│   │   └── main.dart
│   └── pubspec.yaml
├── web/              # Angular app
│   ├── src/
│   │   ├── app/
│   │   │   ├── core/     # Services, models, guards
│   │   │   ├── features/ # Admin, auth, coordinateur, etudiant, enseignant
│   │   │   └── shared/   # Components
│   │   └── main.ts
│   └── angular.json
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
| Mobile | Flutter (Dart) - Riverpod, Dio, FCM, go_router |
| Web | Angular 18 (TypeScript) - Standalone components, Signals |
| Notifications | Firebase FCM |
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

# Mobile (Flutter)
cd mobile
flutter pub get
flutter run
```

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
- Refresh token dans httpOnly cookie (backend) / secure storage (mobile)
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
- Écran de connexion
- Liste des notes avec indicateur de réussite
- Liste des réclamations avec pull-to-refresh
- Création de réclamation
- Détail de réclamation
- Notifications push FCM
- Navigation par bottom bar

## Tests

```bash
# Backend
cd backend
python manage.py test

# Web
cd web
ng test

# Mobile
cd mobile
flutter test