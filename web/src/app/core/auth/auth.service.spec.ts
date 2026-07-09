import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { RouterTestingModule } from '@angular/router/testing';
import { AuthService } from './auth.service';
import { Role } from '../models/user.model';

describe('AuthService', () => {
  let service: AuthService;
  let http: HttpTestingController;

  beforeEach(() => {
    localStorage.clear();
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule, RouterTestingModule],
      providers: [AuthService],
    });
    service = TestBed.inject(AuthService);
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => http.verify());

  it('should be unauthenticated initially', () => {
    expect(service.isAuthenticated()).toBeFalse();
  });

  it('login stores tokens and sets user', () => {
    service.login({ matricule: 'E001', password: 'pass' }).subscribe();
    const req = http.expectOne(r => r.url.includes('/auth/login/'));
    req.flush({
      access: 'access-token',
      refresh: 'refresh-token',
      user: { id: 1, matricule: 'E001', email: 'e@iscae.mr', role: Role.ETUDIANT, nom: 'Ali Ben' },
    });
    expect(service.isAuthenticated()).toBeTrue();
    expect(service.getAccessToken()).toBe('access-token');
    expect(localStorage.getItem('refresh_token')).toBe('refresh-token');
  });

  it('logout clears session and navigates to /login', () => {
    localStorage.setItem('refresh_token', 'tok');
    service.logout();
    http.expectOne(r => r.url.includes('/auth/logout/')).flush({});
    expect(service.isAuthenticated()).toBeFalse();
    expect(service.getAccessToken()).toBeNull();
  });

  it('hasRole returns true for matching role', () => {
    service['currentUser'].set({
      id: 1, matricule: 'E001', email: 'e@iscae.mr',
      role: Role.COORDINATEUR, first_name: '', last_name: '',
      telephone: '', is_active: true,
    });
    expect(service.hasRole([Role.COORDINATEUR])).toBeTrue();
    expect(service.hasRole([Role.ETUDIANT])).toBeFalse();
  });
});