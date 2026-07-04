import { Injectable, signal, computed } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, tap, catchError, throwError } from 'rxjs';
import { environment } from '../../../environments/environment';
import { LoginRequest, LoginResponse, User, Role } from '../models/user.model';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly API = `${environment.apiUrl}/auth`;
  private readonly REFRESH_KEY = 'refresh_token';
  private readonly USER_KEY = 'current_user';

  // Access token stored ONLY in memory (not localStorage) to mitigate XSS risk
  private _accessToken: string | null = null;

  // Signals for reactive state
  currentUser = signal<User | null>(null);
  isAuthenticated = computed(() => this.currentUser() !== null);
  userRole = computed<Role | null>(() => this.currentUser()?.role ?? null);

  constructor(
    private http: HttpClient,
    private router: Router,
  ) {
    this.loadUserFromStorage();
  }

  login(credentials: LoginRequest): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(`${this.API}/login/`, credentials).pipe(
      tap((response) => {
        this.setTokens(response.access, response.refresh);
        const user: User = {
          id: response.user.id,
          matricule: response.user.matricule,
          email: response.user.email,
          role: response.user.role,
          first_name: response.user.nom.split(' ')[0] || '',
          last_name: response.user.nom.split(' ').slice(1).join(' ') || '',
          telephone: '',
          is_active: true,
        };
        this.setUser(user);
      }),
      catchError((error) => {
        return throwError(() => error);
      }),
    );
  }

  logout(): void {
    const refresh = this.getRefreshToken();
    if (refresh) {
      this.http.post(`${this.API}/logout/`, { refresh }).subscribe({
        error: () => {},
      });
    }
    this.clearSession();
    this.router.navigate(['/login']);
  }

  refreshToken(): Observable<{ access: string }> {
    const refresh = this.getRefreshToken();
    return this.http
      .post<{ access: string }>(`${this.API}/refresh/`, { refresh })
      .pipe(
        tap((response) => {
          // Store new access token in memory only
          this._accessToken = response.access;
        }),
        catchError((error) => {
          this.clearSession();
          this.router.navigate(['/login']);
          return throwError(() => error);
        }),
      );
  }

  getAccessToken(): string | null {
    return this._accessToken;
  }

  getRefreshToken(): string | null {
    return localStorage.getItem(this.REFRESH_KEY);
  }

  hasRole(roles: Role[]): boolean {
    const role = this.userRole();
    return role !== null && roles.includes(role);
  }

  redirectBasedOnRole(): void {
    const role = this.userRole();
    switch (role) {
      case Role.ETUDIANT:
        this.router.navigate(['/etudiant/mes-notes']);
        break;
      case Role.COORDINATEUR:
        this.router.navigate(['/coordinateur/dashboard']);
        break;
      case Role.ADMIN:
        this.router.navigate(['/admin/users']);
        break;
      case Role.ENSEIGNANT:
        this.router.navigate(['/enseignant/reclamations']);
        break;
      default:
        this.router.navigate(['/login']);
    }
  }

  private setTokens(access: string, refresh: string): void {
    // Access token stored in memory only — not accessible via JS from other contexts
    this._accessToken = access;
    // Refresh token stored in localStorage (ideally this should be an httpOnly cookie set by the backend)
    localStorage.setItem(this.REFRESH_KEY, refresh);
  }

  private setUser(user: User): void {
    localStorage.setItem(this.USER_KEY, JSON.stringify(user));
    this.currentUser.set(user);
  }

  private loadUserFromStorage(): void {
    const stored = localStorage.getItem(this.USER_KEY);
    if (stored) {
      try {
        this.currentUser.set(JSON.parse(stored));
      } catch {
        this.clearSession();
      }
    }
  }

  private clearSession(): void {
    this._accessToken = null;
    localStorage.removeItem(this.REFRESH_KEY);
    localStorage.removeItem(this.USER_KEY);
    this.currentUser.set(null);
  }
}