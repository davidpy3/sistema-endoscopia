import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { map, Observable } from 'rxjs';

import {
  ApiListResponse,
  Colonoscopia,
  EDA,
  ImagenEndoscopica,
  ProcedureCatalogItem,
  Paciente,
  Personal,
} from './models';

@Injectable({ providedIn: 'root' })
export class EndoscopyApiService {
  private readonly http = inject(HttpClient);
  private readonly apiRoot = '/api';
  private readonly reportRoot = '/reportes';

  list<T>(resource: string): Observable<T[]> {
    return this.http
      .get<ApiListResponse<T> | T[]>(`${this.apiRoot}/${resource}/`, { withCredentials: true })
      .pipe(map((response) => (Array.isArray(response) ? response : response.results)));
  }

  create<T>(resource: string, payload: unknown): Observable<T> {
    return this.http.post<T>(`${this.apiRoot}/${resource}/`, payload, { withCredentials: true });
  }

  update<T>(resource: string, id: number, payload: unknown): Observable<T> {
    return this.http.put<T>(`${this.apiRoot}/${resource}/${id}/`, payload, { withCredentials: true });
  }

  createFromDraft<T>(kind: 'colonoscopia' | 'eda', payload: unknown): Observable<T> {
    return this.http.post<T>(this.fromDraftUrl(kind), payload, { withCredentials: true });
  }

  uploadImage(payload: FormData): Observable<ImagenEndoscopica> {
    return this.http.post<ImagenEndoscopica>(`${this.apiRoot}/imagenes/`, payload, { withCredentials: true });
  }

  draftUrl(kind: 'colonoscopia' | 'eda', id: number): string {
    return `${this.apiRoot}/${kind === 'colonoscopia' ? 'colonoscopias' : 'edas'}/${id}/draft/`;
  }

  reportUrl(kind: 'colonoscopia' | 'eda', id: number): string {
    return `${this.reportRoot}/${kind}/${id}/pdf/?inline=1`;
  }

  fromDraftUrl(kind: 'colonoscopia' | 'eda'): string {
    return `${this.apiRoot}/${kind === 'colonoscopia' ? 'colonoscopias' : 'edas'}/from-draft/`;
  }

  loadPatients(): Observable<Paciente[]> {
    return this.list<Paciente>('pacientes');
  }

  loadPersonnel(): Observable<Personal[]> {
    return this.list<Personal>('personal');
  }

  loadColonoscopias(): Observable<Colonoscopia[]> {
    return this.list<Colonoscopia>('colonoscopias');
  }

  loadEdas(): Observable<EDA[]> {
    return this.list<EDA>('edas');
  }

  loadImages(): Observable<ImagenEndoscopica[]> {
    return this.list<ImagenEndoscopica>('imagenes');
  }

  loadProcedureCatalog(): Observable<ProcedureCatalogItem[]> {
    return this.list<ProcedureCatalogItem>('procedimientos/catalogo');
  }
}