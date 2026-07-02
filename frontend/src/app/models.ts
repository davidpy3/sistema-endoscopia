export interface ApiListResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface AuthAccess {
  role: 'leer' | 'escribir' | 'todo' | 'sin_acceso' | 'anon';
  role_label: string;
  groups: string[];
  can_read: boolean;
  can_write: boolean;
  can_delete: boolean;
}

export interface AuthSessionUser {
  id: number;
  username: string;
  first_name: string;
  last_name: string;
  is_superuser: boolean;
  is_staff: boolean;
  groups: string[];
  access: AuthAccess;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface ProcedureCatalogItem {
  code: string;
  name: string;
  description: string;
  scope: string;
}

export interface Paciente {
  id: number;
  nombres: string;
  apellidos: string;
  dni: string;
  fecha_nacimiento: string | null;
  sexo: string;
  telefono: string;
}

export interface Personal {
  id: number;
  nombre_completo: string;
  rol: 'medico' | 'enfermera' | string;
  rol_display: string;
  colegiatura: string;
  activo: boolean;
}

export interface SegmentoColon {
  id?: number;
  segmento: string;
  estado: 'normal' | 'alterado';
  texto: string;
}

export interface BiopsiaColonoscopia {
  id?: number;
  frasco: string;
  descripcion: string;
  n_lesiones: number | null;
}

export interface DiagnosticoColonoscopia {
  id?: number;
  texto: string;
  orden: number;
}

export interface SugerenciaColonoscopia {
  id?: number;
  texto: string;
  orden: number;
}

export interface Colonoscopia {
  id: number;
  paciente: number;
  paciente_nombre: string;
  medico: number;
  medico_nombre: string;
  enfermera: number | null;
  fecha: string;
  motivo: string;
  antecedentes: string;
  sedacion: string;
  farmacos: string;
  tiempo_retiro_min: number | null;
  intubacion_cecal: boolean | null;
  foto_doc_ciego: boolean | null;
  ileoscopia_distal: boolean | null;
  boston_cd: number | null;
  boston_ct: number | null;
  boston_ci: number | null;
  boston_total: number | null;
  preparacion_adecuada: boolean | null;
  insp_pasiva: string;
  insp_activa: string;
  tacto_rectal: string;
  canal_anal: string;
  segmentos: SegmentoColon[];
  biopsias: BiopsiaColonoscopia[];
  diagnosticos: DiagnosticoColonoscopia[];
  sugerencias: SugerenciaColonoscopia[];
  creado_en: string;
  actualizado_en: string;
}

export interface SegmentoEDA {
  id?: number;
  segmento: string;
  estado: 'normal' | 'alterado';
  texto: string;
  cardias_hill: string;
  piloro: string;
}

export interface BiopsiaEDA {
  id?: number;
  frasco: string;
  descripcion: string;
  n_lesiones: number | null;
}

export interface DiagnosticoEDA {
  id?: number;
  texto: string;
  orden: number;
}

export interface SugerenciaEDA {
  id?: number;
  texto: string;
  orden: number;
}

export interface EDA {
  id: number;
  paciente: number;
  paciente_nombre: string;
  medico: number;
  medico_nombre: string;
  enfermera: number | null;
  fecha: string;
  motivo: string;
  antecedentes: string;
  sedacion: string;
  farmacos: string;
  tiempo_examen_min: number | null;
  peace_esofago: number | null;
  peace_estomago: number | null;
  peace_duodeno: number | null;
  peace_total: number | null;
  segmentos: SegmentoEDA[];
  biopsias: BiopsiaEDA[];
  diagnosticos: DiagnosticoEDA[];
  sugerencias: SugerenciaEDA[];
  creado_en: string;
  actualizado_en: string;
}

export interface ImagenEndoscopica {
  id: number;
  tipo: 'eda' | 'colonoscopia';
  tipo_display: string;
  object_id: number;
  archivo: string;
  epigrafe: string;
  orden: number;
  subido_en: string;
}

export interface SegmentOption {
  key: string;
  label: string;
  normalText: string;
}

export const SEDATION_OPTIONS = [
  { value: '', label: '—' },
  { value: 'ninguna', label: 'Ninguna' },
  { value: 'consciente', label: 'Consciente' },
  { value: 'profunda', label: 'Profunda' },
  { value: 'naap', label: 'NAAP / propofol' },
];

export const SEXO_OPTIONS = [
  { value: '', label: '—' },
  { value: 'M', label: 'Masculino' },
  { value: 'F', label: 'Femenino' },
];

export const HILL_OPTIONS = [
  { value: '', label: '—' },
  { value: 'hill1', label: 'Hill I' },
  { value: 'hill2', label: 'Hill II' },
  { value: 'hill3', label: 'Hill III' },
  { value: 'hill4', label: 'Hill IV' },
];

export const PILORO_OPTIONS = [
  { value: '', label: '—' },
  { value: 'centrico', label: 'Céntrico y permeable' },
  { value: 'deformado', label: 'Deformado' },
  { value: 'estenotico', label: 'Estenótico' },
];

export const COLON_SEGMENTS: SegmentOption[] = [
  {
    key: 'ciego',
    label: 'Ciego',
    normalText:
      'Se visualiza orificio apendicular y válvula ileocecal de aspecto conservado. Mucosa y patrón vascular submucoso de aspecto conservado.',
  },
  {
    key: 'ascendente',
    label: 'Colon ascendente',
    normalText: 'Mucosa y patrón vascular submucoso de aspecto conservado.',
  },
  {
    key: 'transverso',
    label: 'Colon transverso',
    normalText: 'Mucosa y patrón vascular submucoso de aspecto conservado.',
  },
  {
    key: 'descendente',
    label: 'Colon descendente',
    normalText: 'Mucosa y patrón vascular submucoso de aspecto conservado.',
  },
  {
    key: 'sigmoides',
    label: 'Colon sigmoides',
    normalText: 'Mucosa y patrón vascular submucoso de aspecto conservado.',
  },
  {
    key: 'recto',
    label: 'Recto',
    normalText: 'Mucosa y patrón vascular submucoso de aspecto conservado.',
  },
];

export const EDA_SEGMENTS: SegmentOption[] = [
  {
    key: 'esofago',
    label: 'Esófago',
    normalText: 'Mucosa de aspecto conservado. Línea Z regular, no congestiva.',
  },
  {
    key: 'fondo',
    label: 'Estómago — Fondo',
    normalText: 'Mucosa de aspecto conservado.',
  },
  {
    key: 'cuerpo',
    label: 'Estómago — Cuerpo',
    normalText: 'Mucosa de aspecto conservado. Pliegues gástricos sin alteraciones.',
  },
  {
    key: 'angulo',
    label: 'Estómago — Ángulo',
    normalText: 'Mucosa de aspecto conservado.',
  },
  {
    key: 'antro',
    label: 'Estómago — Antro',
    normalText: 'Mucosa de aspecto conservado.',
  },
  {
    key: 'bulbo',
    label: 'Duodeno — Bulbo',
    normalText: 'Mucosa de aspecto conservado.',
  },
  {
    key: 'segporcion',
    label: 'Duodeno — 2.ª porción',
    normalText: 'Mucosa de aspecto conservado. Ampolla de Vater sin alteraciones.',
  },
];