import { HttpClient } from '@angular/common/http';
import { Injectable, computed, inject, signal } from '@angular/core';
import { lastValueFrom, of } from 'rxjs';
import { catchError } from 'rxjs/operators';

import { AuthSessionUser, LoginCredentials } from './models';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);

  readonly currentUser = signal<AuthSessionUser | null>(null);
  readonly bootstrapping = signal(true);
  readonly loading = signal(false);
  readonly error = signal<string | null>(null);

  readonly authenticated = computed(() => this.currentUser() !== null);
  readonly access = computed(() => this.currentUser()?.access ?? null);
  readonly canRead = computed(() => this.access()?.can_read ?? false);
  readonly canWrite = computed(() => this.access()?.can_write ?? false);
  readonly canDelete = computed(() => this.access()?.can_delete ?? false);
  readonly canManageMasterData = computed(() => this.currentUser()?.is_superuser ?? false);
  readonly roleLabel = computed(() => this.access()?.role_label ?? 'Sin sesión');
  readonly username = computed(() => this.currentUser()?.username ?? '');

  async bootstrap(): Promise<void> {
    this.bootstrapping.set(true);
    try {
      await lastValueFrom(this.http.get('/api/auth/csrf/', { withCredentials: true }));
      const session = await lastValueFrom(
        this.http.get<AuthSessionUser>('/api/auth/me/', { withCredentials: true }).pipe(
          catchError(() => of(null))
        )
      );
      this.currentUser.set(session);
      this.error.set(null);
    } finally {
      this.bootstrapping.set(false);
    }
  }

  async login(credentials: LoginCredentials): Promise<void> {
    this.loading.set(true);
    this.error.set(null);
    try {
      const session = await lastValueFrom(
        this.http.post<AuthSessionUser>('/api/auth/login/', credentials, { withCredentials: true })
      );
      this.currentUser.set(session);
    } catch (error) {
      this.error.set(this.formatError(error));
      throw error;
    } finally {
      this.loading.set(false);
    }
  }

  async logout(): Promise<void> {
    this.loading.set(true);
    this.error.set(null);
    try {
      await lastValueFrom(this.http.post('/api/auth/logout/', {}, { withCredentials: true }));
      this.currentUser.set(null);
    } finally {
      this.loading.set(false);
    }
  }

  private formatError(error: unknown): string {
    if (error && typeof error === 'object' && 'error' in error) {
      const errorObject = error as { error?: { detail?: string; non_field_errors?: string[] } };
      if (errorObject.error?.detail) {
        return errorObject.error.detail;
      }
      if (errorObject.error?.non_field_errors?.length) {
        return errorObject.error.non_field_errors[0];
      }
    }

    if (error && typeof error === 'object' && 'message' in error) {
      return String((error as { message: unknown }).message);
    }

    return 'No se pudo iniciar sesión.';
  }
}
