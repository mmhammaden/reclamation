import { TestBed } from '@angular/core/testing';
import { RouterTestingModule } from '@angular/router/testing';
import { ActivatedRouteSnapshot, Router } from '@angular/router';
import { authGuard } from './auth.guard';
import { AuthService } from './auth.service';
import { Role } from '../models/user.model';

describe('authGuard', () => {
  let authService: jasmine.SpyObj<AuthService>;
  let router: Router;

  const runGuard = (roles?: Role[]) => {
    const route = { data: roles ? { roles } : {} } as unknown as ActivatedRouteSnapshot;
    return TestBed.runInInjectionContext(() => authGuard(route, null!));
  };

  beforeEach(() => {
    authService = jasmine.createSpyObj('AuthService', ['isAuthenticated', 'hasRole'], {
      isAuthenticated: jasmine.createSpy().and.returnValue(false),
      hasRole: jasmine.createSpy().and.returnValue(false),
    });
    TestBed.configureTestingModule({
      imports: [RouterTestingModule],
      providers: [{ provide: AuthService, useValue: authService }],
    });
    router = TestBed.inject(Router);
    spyOn(router, 'navigate');
  });

  it('redirects to /login when unauthenticated', () => {
    (authService.isAuthenticated as jasmine.Spy).and.returnValue(false);
    expect(runGuard()).toBeFalse();
    expect(router.navigate).toHaveBeenCalledWith(['/login']);
  });

  it('allows access when authenticated and no role required', () => {
    (authService.isAuthenticated as jasmine.Spy).and.returnValue(true);
    expect(runGuard()).toBeTrue();
  });

  it('blocks access when role does not match', () => {
    (authService.isAuthenticated as jasmine.Spy).and.returnValue(true);
    (authService.hasRole as jasmine.Spy).and.returnValue(false);
    expect(runGuard([Role.ADMIN])).toBeFalse();
  });

  it('allows access when role matches', () => {
    (authService.isAuthenticated as jasmine.Spy).and.returnValue(true);
    (authService.hasRole as jasmine.Spy).and.returnValue(true);
    expect(runGuard([Role.COORDINATEUR])).toBeTrue();
  });
});