import { inject } from '@angular/core';
import { Router, type CanActivateFn, type ActivatedRouteSnapshot } from '@angular/router';
import { AuthService } from './auth.service';
import { Role } from '../models/user.model';

export const authGuard: CanActivateFn = (route: ActivatedRouteSnapshot) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (!authService.isAuthenticated()) {
    router.navigate(['/login']);
    return false;
  }

  const requiredRoles = route.data['roles'] as Role[] | undefined;
  if (requiredRoles && requiredRoles.length > 0) {
    if (!authService.hasRole(requiredRoles)) {
      router.navigate(['/login']);
      return false;
    }
  }

  return true;
};