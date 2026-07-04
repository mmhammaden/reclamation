import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { User, UserCreate } from '../models/user.model';

@Injectable({ providedIn: 'root' })
export class UsersService {
  private readonly API = `${environment.apiUrl}/admin/users`;
  private http = inject(HttpClient);

  getUsers(): Observable<{ count: number; results: User[] }> {
    return this.http.get<{ count: number; results: User[] }>(this.API);
  }

  createUser(data: UserCreate): Observable<User> {
    return this.http.post<User>(this.API, data);
  }
}