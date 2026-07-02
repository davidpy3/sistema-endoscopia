import { CommonModule } from '@angular/common';
import { Component, OnInit, computed, effect, inject, signal } from '@angular/core';
import { ReactiveFormsModule, UntypedFormArray, UntypedFormBuilder, UntypedFormGroup, Validators } from '@angular/forms';
import { forkJoin, lastValueFrom } from 'rxjs';

import { AuthService } from './auth.service';
import { EndoscopyApiService } from './endoscopy-api.service';
import { ImageCategoriesPanelComponent } from './image-categories-panel/image-categories-panel.component';
import { LoginPanelComponent } from './login-panel/login-panel.component';
import { ProceduresPanelComponent } from './procedures-panel/procedures-panel.component';
import { SearchableSelectComponent } from './searchable-select/searchable-select.component';
import { PatientDialogComponent, PatientDialogMode, PatientFormValue } from './patient-dialog/patient-dialog.component';
import { PersonalDialogComponent, PersonalDialogMode, PersonalFormValue } from './personal-dialog/personal-dialog.component';
import {
  BiopsiaColonoscopia,
  BiopsiaEDA,
  COLON_SEGMENTS,
  Colonoscopia,
  DiagnosticoColonoscopia,
  DiagnosticoEDA,
  EDA,
  EDA_SEGMENTS,
  HILL_OPTIONS,
  ImagenEndoscopica,
  Paciente,
  Personal,
  ProcedureCatalogItem,
  PILORO_OPTIONS,
  SegmentOption,
  SEDATION_OPTIONS,
  SugerenciaColonoscopia,
  SugerenciaEDA,
} from './models';

type TabKey = 'resumen' | 'procedimientos' | 'pacientes' | 'personal' | 'colonoscopias' | 'eda' | 'imagenes';

@Component({
  selector: 'app-root',
  imports: [CommonModule, ReactiveFormsModule, ImageCategoriesPanelComponent, LoginPanelComponent, ProceduresPanelComponent, SearchableSelectComponent, PatientDialogComponent, PersonalDialogComponent],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App implements OnInit {
  protected readonly auth = inject(AuthService);
  private readonly api = inject(EndoscopyApiService);
  private readonly fb = inject(UntypedFormBuilder);

  constructor() {
    effect(() => {
      if (this.auth.bootstrapping()) {
        return;
      }

      if (this.auth.authenticated()) {
        void this.refreshAll();
      } else {
        this.resetWorkspaceState();
      }
    });
  }

  protected readonly tabs: Array<{ id: TabKey; label: string; description: string }> = [
    { id: 'resumen', label: 'Resumen', description: 'Métrica rápida y estado general' },
    { id: 'procedimientos', label: 'Procedimientos', description: 'Catálogo por tipo y carga' },
    { id: 'pacientes', label: 'Pacientes', description: 'Alta y consulta' },
    { id: 'personal', label: 'Personal', description: 'Médicos y enfermería' },
    { id: 'colonoscopias', label: 'Colonoscopías', description: 'Informe y borradores' },
    { id: 'eda', label: 'EDA', description: 'Informe y borradores' },
    { id: 'imagenes', label: 'Imágenes', description: 'Galería por categoría' },
  ];

  protected readonly activeTab = signal<TabKey>('resumen');
  protected readonly patientDialogOpen = signal(false);
  protected readonly patientDialogMode = signal<PatientDialogMode>('create');
  protected readonly selectedPatient = signal<Paciente | null>(null);
  protected readonly personalDialogOpen = signal(false);
  protected readonly personalDialogMode = signal<PersonalDialogMode>('create');
  protected readonly selectedPersonal = signal<Personal | null>(null);
  protected readonly loading = signal(false);
  protected readonly statusMessage = signal('Sincroniza con el backend para empezar.');
  protected readonly errorMessage = signal<string | null>(null);

  protected readonly patients = signal<Paciente[]>([]);
  protected readonly personnel = signal<Personal[]>([]);
  protected readonly procedureCatalog = signal<ProcedureCatalogItem[]>([]);
  protected readonly colonoscopias = signal<Colonoscopia[]>([]);
  protected readonly edas = signal<EDA[]>([]);
  protected readonly images = signal<ImagenEndoscopica[]>([]);

  protected readonly lastColonoscopiaId = signal<number | null>(null);
  protected readonly lastEdaId = signal<number | null>(null);

  protected readonly selectedImageFile = signal<File | null>(null);
  protected readonly imageResetToken = signal(0);
  protected readonly selectedDraftFile = signal<File | null>(null);

  protected readonly isSuperAdmin = computed(() => this.auth.canManageMasterData());

  protected readonly doctors = computed(() =>
    this.personnel().filter((person) => person.rol === 'medico' && person.activo)
  );
  protected readonly nurses = computed(() =>
    this.personnel().filter((person) => person.rol === 'enfermera' && person.activo)
  );
  protected readonly patientOptions = computed(() =>
    this.patients().map((patient) => ({
      value: patient.id,
      label: `${patient.apellidos}, ${patient.nombres}`,
      description: `DNI ${patient.dni}`,
    }))
  );
  protected readonly doctorOptions = computed(() =>
    this.doctors().map((doctor) => ({
      value: doctor.id,
      label: doctor.nombre_completo,
      description: doctor.colegiatura || 'Médico',
    }))
  );
  protected readonly nurseOptions = computed(() =>
    this.nurses().map((nurse) => ({
      value: nurse.id,
      label: nurse.nombre_completo,
      description: nurse.colegiatura || 'Enfermera',
    }))
  );
  protected readonly stats = computed(() => ({
    patients: this.patients().length,
    personnel: this.personnel().length,
    procedures: this.procedureCatalog().length,
    colonoscopias: this.colonoscopias().length,
    edas: this.edas().length,
    images: this.images().length,
  }));

  protected colonoscopiaForm = this.createColonoscopiaForm();
  protected edaForm = this.createEdaForm();
  protected readonly imageForm = this.createImageForm();
  protected readonly draftImportForm = this.fb.group({
    tipo: ['colonoscopia', Validators.required],
  });

  protected readonly sedationOptions = SEDATION_OPTIONS;
  protected readonly hillOptions = HILL_OPTIONS;
  protected readonly piloroOptions = PILORO_OPTIONS;
  protected readonly colonSegmentsData = COLON_SEGMENTS;
  protected readonly edaSegmentsData = EDA_SEGMENTS;

  async ngOnInit(): Promise<void> {
    await this.auth.bootstrap();
  }

  protected setTab(tab: TabKey): void {
    this.activeTab.set(tab);
  }

  protected openPatientDialog(): void {
    if (!this.isSuperAdmin()) {
      return;
    }

    this.selectedPatient.set(null);
    this.patientDialogMode.set('create');
    this.patientDialogOpen.set(true);
  }

  protected viewPatient(patient: Paciente): void {
    if (!this.isSuperAdmin()) {
      return;
    }

    this.selectedPatient.set(patient);
    this.patientDialogMode.set('view');
    this.patientDialogOpen.set(true);
  }

  protected editPatient(patient: Paciente): void {
    if (!this.isSuperAdmin()) {
      return;
    }

    this.selectedPatient.set(patient);
    this.patientDialogMode.set('edit');
    this.patientDialogOpen.set(true);
  }

  protected closePatientDialog(): void {
    this.patientDialogOpen.set(false);
    this.selectedPatient.set(null);
    this.patientDialogMode.set('create');
  }

  protected openPersonalDialog(): void {
    if (!this.isSuperAdmin()) {
      return;
    }

    this.selectedPersonal.set(null);
    this.personalDialogMode.set('create');
    this.personalDialogOpen.set(true);
  }

  protected viewPersonal(personal: Personal): void {
    if (!this.isSuperAdmin()) {
      return;
    }

    this.selectedPersonal.set(personal);
    this.personalDialogMode.set('view');
    this.personalDialogOpen.set(true);
  }

  protected editPersonal(personal: Personal): void {
    if (!this.isSuperAdmin()) {
      return;
    }

    this.selectedPersonal.set(personal);
    this.personalDialogMode.set('edit');
    this.personalDialogOpen.set(true);
  }

  protected async logout(): Promise<void> {
    await this.auth.logout();
  }

  protected closePersonalDialog(): void {
    this.personalDialogOpen.set(false);
    this.selectedPersonal.set(null);
    this.personalDialogMode.set('create');
  }

  protected async refreshAll(): Promise<void> {
    if (!this.auth.canRead()) {
      this.statusMessage.set('Inicia sesión para ver y sincronizar los datos.');
      return;
    }

    this.loading.set(true);
    this.errorMessage.set(null);

    try {
      const payload = await lastValueFrom(
        forkJoin({
          patients: this.api.loadPatients(),
          personnel: this.api.loadPersonnel(),
          procedures: this.api.loadProcedureCatalog(),
          colonoscopias: this.api.loadColonoscopias(),
          edas: this.api.loadEdas(),
          images: this.api.loadImages(),
        })
      );

      this.patients.set(payload.patients);
      this.personnel.set(payload.personnel);
      this.procedureCatalog.set(payload.procedures);
      this.colonoscopias.set(payload.colonoscopias);
      this.edas.set(payload.edas);
      this.images.set(payload.images);
      this.statusMessage.set('Datos actualizados desde la API.');
    } catch (error) {
      this.errorMessage.set(this.formatError(error));
      this.statusMessage.set('No se pudo sincronizar con la API.');
    } finally {
      this.loading.set(false);
    }
  }

  protected async savePatient(payload: PatientFormValue): Promise<void> {
    if (!this.isSuperAdmin()) {
      this.statusMessage.set('Solo el superadministrador puede gestionar pacientes.');
      return;
    }

    try {
      const selectedPatient = this.selectedPatient();
      if (this.patientDialogMode() === 'edit' && selectedPatient) {
        await lastValueFrom(this.api.update<Paciente>('pacientes', selectedPatient.id, payload));
        this.statusMessage.set('Paciente actualizado correctamente.');
      } else {
        await lastValueFrom(this.api.create<Paciente>('pacientes', payload));
        this.statusMessage.set('Paciente registrado correctamente.');
      }
      this.closePatientDialog();
      await this.refreshAll();
    } catch (error) {
      this.errorMessage.set(this.formatError(error));
    }
  }

  protected async savePersonal(payload: PersonalFormValue): Promise<void> {
    if (!this.isSuperAdmin()) {
      this.statusMessage.set('Solo el superadministrador puede gestionar personal.');
      return;
    }

    try {
      const selectedPersonal = this.selectedPersonal();
      if (this.personalDialogMode() === 'edit' && selectedPersonal) {
        await lastValueFrom(this.api.update<Personal>('personal', selectedPersonal.id, payload));
        this.statusMessage.set('Personal actualizado correctamente.');
      } else {
        await lastValueFrom(this.api.create<Personal>('personal', payload));
        this.statusMessage.set('Personal registrado correctamente.');
      }
      this.closePersonalDialog();
      await this.refreshAll();
    } catch (error) {
      this.errorMessage.set(this.formatError(error));
    }
  }

  protected async saveColonoscopia(): Promise<void> {
    if (!this.auth.canWrite()) {
      this.statusMessage.set('Tu usuario solo tiene permisos de lectura.');
      return;
    }

    if (this.colonoscopiaForm.invalid) {
      this.statusMessage.set('Completa paciente, médico y fecha para registrar la colonoscopía.');
      return;
    }

    try {
      const payload = this.buildColonoscopiaPayload();
      const created = await lastValueFrom(this.api.create<Colonoscopia>('colonoscopias', payload));
      this.lastColonoscopiaId.set(created.id);
      this.resetColonoscopiaForm();
      this.statusMessage.set(`Colonoscopía #${created.id} guardada y lista para PDF.`);
      this.activeTab.set('colonoscopias');
      await this.refreshAll();
    } catch (error) {
      this.errorMessage.set(this.formatError(error));
    }
  }

  protected async saveEda(): Promise<void> {
    if (!this.auth.canWrite()) {
      this.statusMessage.set('Tu usuario solo tiene permisos de lectura.');
      return;
    }

    if (this.edaForm.invalid) {
      this.statusMessage.set('Completa paciente, médico y fecha para registrar la EDA.');
      return;
    }

    try {
      const payload = this.buildEdaPayload();
      const created = await lastValueFrom(this.api.create<EDA>('edas', payload));
      this.lastEdaId.set(created.id);
      this.resetEdaForm();
      this.statusMessage.set(`EDA #${created.id} guardada y lista para PDF.`);
      this.activeTab.set('eda');
      await this.refreshAll();
    } catch (error) {
      this.errorMessage.set(this.formatError(error));
    }
  }

  protected async uploadImage(): Promise<void> {
    if (!this.auth.canWrite()) {
      this.statusMessage.set('Tu usuario solo tiene permisos de lectura.');
      return;
    }

    const file = this.selectedImageFile();
    if (!file || this.imageForm.invalid) {
      this.statusMessage.set('Selecciona una imagen y completa el destino antes de subirla.');
      return;
    }

    try {
      const formData = new FormData();
      formData.append('tipo', this.imageForm.get('tipo')?.value);
      formData.append('object_id', String(this.imageForm.get('object_id')?.value));
      formData.append('archivo', file);
      formData.append('epigrafe', this.imageForm.get('epigrafe')?.value || '');
      formData.append('orden', String(this.imageForm.get('orden')?.value ?? 0));

      await lastValueFrom(this.api.uploadImage(formData));
      this.selectedImageFile.set(null);
      this.resetImageForm();
      this.statusMessage.set('Imagen subida correctamente.');
      this.activeTab.set('imagenes');
      await this.refreshAll();
    } catch (error) {
      this.errorMessage.set(this.formatError(error));
    }
  }

  protected async importDraft(): Promise<void> {
    if (!this.auth.canWrite()) {
      this.statusMessage.set('Tu usuario solo tiene permisos de lectura.');
      return;
    }

    const file = this.selectedDraftFile();
    const kind = this.draftImportForm.get('tipo')?.value as 'colonoscopia' | 'eda';

    if (!file) {
      this.statusMessage.set('Selecciona un archivo JSON de borrador antes de importarlo.');
      return;
    }

    try {
      const parsed = JSON.parse(await file.text());
      if (kind === 'colonoscopia') {
        const created = await lastValueFrom(this.api.createFromDraft<Colonoscopia>(kind, parsed));
        this.lastColonoscopiaId.set(created.id);
        this.activeTab.set('colonoscopias');
        this.statusMessage.set(`Borrador de colonoscopía importado como #${created.id}.`);
      } else {
        const created = await lastValueFrom(this.api.createFromDraft<EDA>(kind, parsed));
        this.lastEdaId.set(created.id);
        this.activeTab.set('eda');
        this.statusMessage.set(`Borrador de EDA importado como #${created.id}.`);
      }

      this.selectedDraftFile.set(null);
      this.resetDraftImportForm();
      await this.refreshAll();
    } catch (error) {
      this.errorMessage.set(this.formatError(error));
    }
  }

  protected onImageSelected(file: File | null): void {
    this.selectedImageFile.set(file);
  }

  protected onDraftSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    this.selectedDraftFile.set(input.files?.[0] ?? null);
  }

  protected resetColonoscopiaForm(): void {
    this.colonoscopiaForm = this.createColonoscopiaForm();
  }

  protected resetEdaForm(): void {
    this.edaForm = this.createEdaForm();
  }

  protected resetImageForm(): void {
    this.imageForm.reset({ tipo: 'colonoscopia', object_id: '', epigrafe: '', orden: 0 });
    this.selectedImageFile.set(null);
    this.imageResetToken.update((currentValue: number) => currentValue + 1);
  }

  protected resetDraftImportForm(): void {
    this.draftImportForm.reset({ tipo: 'colonoscopia' });
    this.selectedDraftFile.set(null);
  }

  protected openDraft(kind: 'colonoscopia' | 'eda', id: number): void {
    window.open(this.api.draftUrl(kind, id), '_blank', 'noopener');
  }

  protected openReport(kind: 'colonoscopia' | 'eda', id: number): void {
    window.open(this.api.reportUrl(kind, id), '_blank', 'noopener');
  }

  protected get colonSegments(): UntypedFormArray {
    return this.colonoscopiaForm.get('segmentos') as UntypedFormArray;
  }

  protected get colonSegmentGroups(): UntypedFormGroup[] {
    return this.colonSegments.controls as UntypedFormGroup[];
  }

  protected get colonBiopsias(): UntypedFormArray {
    return this.colonoscopiaForm.get('biopsias') as UntypedFormArray;
  }

  protected get colonBiopsiaGroups(): UntypedFormGroup[] {
    return this.colonBiopsias.controls as UntypedFormGroup[];
  }

  protected get colonDiagnosticos(): UntypedFormArray {
    return this.colonoscopiaForm.get('diagnosticos') as UntypedFormArray;
  }

  protected get colonDiagnosticoGroups(): UntypedFormGroup[] {
    return this.colonDiagnosticos.controls as UntypedFormGroup[];
  }

  protected get colonSugerencias(): UntypedFormArray {
    return this.colonoscopiaForm.get('sugerencias') as UntypedFormArray;
  }

  protected get colonSugerenciaGroups(): UntypedFormGroup[] {
    return this.colonSugerencias.controls as UntypedFormGroup[];
  }

  protected get edaSegments(): UntypedFormArray {
    return this.edaForm.get('segmentos') as UntypedFormArray;
  }

  protected get edaSegmentGroups(): UntypedFormGroup[] {
    return this.edaSegments.controls as UntypedFormGroup[];
  }

  protected get edaBiopsias(): UntypedFormArray {
    return this.edaForm.get('biopsias') as UntypedFormArray;
  }

  protected get edaBiopsiaGroups(): UntypedFormGroup[] {
    return this.edaBiopsias.controls as UntypedFormGroup[];
  }

  protected get edaDiagnosticos(): UntypedFormArray {
    return this.edaForm.get('diagnosticos') as UntypedFormArray;
  }

  protected get edaDiagnosticoGroups(): UntypedFormGroup[] {
    return this.edaDiagnosticos.controls as UntypedFormGroup[];
  }

  protected get edaSugerencias(): UntypedFormArray {
    return this.edaForm.get('sugerencias') as UntypedFormArray;
  }

  protected get edaSugerenciaGroups(): UntypedFormGroup[] {
    return this.edaSugerencias.controls as UntypedFormGroup[];
  }

  protected addColonBiopsia(): void {
    this.colonBiopsias.push(this.createBiopsiaGroup());
  }

  protected removeColonBiopsia(index: number): void {
    if (this.colonBiopsias.length > 1) {
      this.colonBiopsias.removeAt(index);
    }
  }

  protected addColonDiagnostico(): void {
    this.colonDiagnosticos.push(this.createDiagnosticoGroup());
  }

  protected removeColonDiagnostico(index: number): void {
    if (this.colonDiagnosticos.length > 1) {
      this.colonDiagnosticos.removeAt(index);
    }
  }

  protected addColonSugerencia(): void {
    this.colonSugerencias.push(this.createSugerenciaGroup());
  }

  protected removeColonSugerencia(index: number): void {
    if (this.colonSugerencias.length > 1) {
      this.colonSugerencias.removeAt(index);
    }
  }

  protected addEdaBiopsia(): void {
    this.edaBiopsias.push(this.createBiopsiaGroup());
  }

  protected removeEdaBiopsia(index: number): void {
    if (this.edaBiopsias.length > 1) {
      this.edaBiopsias.removeAt(index);
    }
  }

  protected addEdaDiagnostico(): void {
    this.edaDiagnosticos.push(this.createDiagnosticoGroup());
  }

  protected removeEdaDiagnostico(index: number): void {
    if (this.edaDiagnosticos.length > 1) {
      this.edaDiagnosticos.removeAt(index);
    }
  }

  protected addEdaSugerencia(): void {
    this.edaSugerencias.push(this.createSugerenciaGroup());
  }

  protected removeEdaSugerencia(index: number): void {
    if (this.edaSugerencias.length > 1) {
      this.edaSugerencias.removeAt(index);
    }
  }

  protected syncColonSegment(index: number): void {
    const segmentGroup = this.colonSegments.at(index);
    const segment = COLON_SEGMENTS[index];
    if (!segmentGroup || !segment) {
      return;
    }

    const currentState = segmentGroup.get('estado')?.value;
    segmentGroup.get('texto')?.setValue(currentState === 'alterado' ? '' : segment.normalText);
  }

  protected syncEdaSegment(index: number): void {
    const segmentGroup = this.edaSegments.at(index);
    const segment = EDA_SEGMENTS[index];
    if (!segmentGroup || !segment) {
      return;
    }

    const currentState = segmentGroup.get('estado')?.value;
    segmentGroup.get('texto')?.setValue(currentState === 'alterado' ? '' : segment.normalText);
  }

  private createImageForm() {
    return this.fb.group({
      tipo: ['colonoscopia', Validators.required],
      object_id: ['', Validators.required],
      epigrafe: [''],
      orden: [0],
    });
  }

  private createColonoscopiaForm() {
    return this.fb.group({
      paciente: [null, Validators.required],
      medico: [null, Validators.required],
      enfermera: [null],
      fecha: [this.today(), Validators.required],
      motivo: [''],
      antecedentes: [''],
      sedacion: [''],
      farmacos: [''],
      tiempo_retiro_min: [null],
      intubacion_cecal: [null],
      foto_doc_ciego: [null],
      ileoscopia_distal: [null],
      boston_cd: [null],
      boston_ct: [null],
      boston_ci: [null],
      insp_pasiva: [''],
      insp_activa: [''],
      tacto_rectal: [''],
      canal_anal: [''],
      segmentos: this.fb.array(COLON_SEGMENTS.map((segment) => this.createColonSegmentGroup(segment))),
      biopsias: this.fb.array([this.createBiopsiaGroup()]),
      diagnosticos: this.fb.array([this.createDiagnosticoGroup()]),
      sugerencias: this.fb.array([this.createSugerenciaGroup()]),
    });
  }

  private createEdaForm() {
    return this.fb.group({
      paciente: [null, Validators.required],
      medico: [null, Validators.required],
      enfermera: [null],
      fecha: [this.today(), Validators.required],
      motivo: [''],
      antecedentes: [''],
      sedacion: [''],
      farmacos: [''],
      tiempo_examen_min: [null],
      peace_esofago: [null],
      peace_estomago: [null],
      peace_duodeno: [null],
      segmentos: this.fb.array(EDA_SEGMENTS.map((segment) => this.createEdaSegmentGroup(segment))),
      biopsias: this.fb.array([this.createBiopsiaGroup()]),
      diagnosticos: this.fb.array([this.createDiagnosticoGroup()]),
      sugerencias: this.fb.array([this.createSugerenciaGroup()]),
    });
  }

  private createColonSegmentGroup(segment: SegmentOption) {
    return this.fb.group({
      segmento: [segment.key],
      estado: ['normal'],
      texto: [segment.normalText],
    });
  }

  private createEdaSegmentGroup(segment: SegmentOption) {
    return this.fb.group({
      segmento: [segment.key],
      estado: ['normal'],
      texto: [segment.normalText],
      cardias_hill: [''],
      piloro: [''],
    });
  }

  private createBiopsiaGroup() {
    return this.fb.group({
      frasco: [''],
      descripcion: [''],
      n_lesiones: [null],
    });
  }

  private createDiagnosticoGroup() {
    return this.fb.group({
      texto: [''],
      orden: [0],
    });
  }

  private createSugerenciaGroup() {
    return this.fb.group({
      texto: [''],
      orden: [0],
    });
  }

  protected formatPeruPhone(phone: string): string {
    const normalized = this.normalizePeruPhone(phone);
    if (!normalized) {
      return '—';
    }

    return `+51 ${normalized.slice(0, 3)} ${normalized.slice(3, 6)} ${normalized.slice(6)}`;
  }

  protected patientWhatsappUrl(patient: Paciente): string | null {
    const phone = this.normalizePeruPhone(patient.telefono);
    if (!phone) {
      return null;
    }

    const latestReport = this.latestPatientReport(patient.id);
    const messageParts = [
      `Hola ${patient.nombres} ${patient.apellidos},`,
      'le compartimos su informe PDF desde el sistema de endoscopia.',
    ];

    if (latestReport) {
      messageParts.push(`PDF: ${this.api.reportUrl(latestReport.kind, latestReport.id)}`);
    }

    return `https://wa.me/51${phone}?text=${encodeURIComponent(messageParts.join(' '))}`;
  }

  private buildColonoscopiaPayload() {
    const raw = this.colonoscopiaForm.getRawValue();
    return {
      ...raw,
      paciente: this.asNumber(raw.paciente),
      medico: this.asNumber(raw.medico),
      enfermera: this.asNullableNumber(raw.enfermera),
      tiempo_retiro_min: this.asNullableDecimal(raw.tiempo_retiro_min),
      boston_cd: this.asNullableInteger(raw.boston_cd),
      boston_ct: this.asNullableInteger(raw.boston_ct),
      boston_ci: this.asNullableInteger(raw.boston_ci),
      intubacion_cecal: this.asNullableBoolean(raw.intubacion_cecal),
      foto_doc_ciego: this.asNullableBoolean(raw.foto_doc_ciego),
      ileoscopia_distal: this.asNullableBoolean(raw.ileoscopia_distal),
      segmentos: this.colonSegments.controls.map((control) => control.getRawValue()),
      biopsias: this.filterFilledRows(this.colonBiopsias.controls.map((control) => control.getRawValue())).map(
        (row: Record<string, unknown>) => ({
          ...row,
          n_lesiones: this.asNullableInteger(row['n_lesiones']),
        })
      ),
      diagnosticos: this.filterFilledRows(this.colonDiagnosticos.controls.map((control) => control.getRawValue())).map(
        (row: Record<string, unknown>, index: number) => ({
          texto: String(row['texto'] ?? '').trim(),
          orden: this.asInteger(row['orden'], index),
        })
      ),
      sugerencias: this.filterFilledRows(this.colonSugerencias.controls.map((control) => control.getRawValue())).map(
        (row: Record<string, unknown>, index: number) => ({
          texto: String(row['texto'] ?? '').trim(),
          orden: this.asInteger(row['orden'], index),
        })
      ),
    };
  }

  private buildEdaPayload() {
    const raw = this.edaForm.getRawValue();
    return {
      ...raw,
      paciente: this.asNumber(raw.paciente),
      medico: this.asNumber(raw.medico),
      enfermera: this.asNullableNumber(raw.enfermera),
      tiempo_examen_min: this.asNullableInteger(raw.tiempo_examen_min),
      peace_esofago: this.asNullableInteger(raw.peace_esofago),
      peace_estomago: this.asNullableInteger(raw.peace_estomago),
      peace_duodeno: this.asNullableInteger(raw.peace_duodeno),
      segmentos: this.edaSegments.controls.map((control) => control.getRawValue()),
      biopsias: this.filterFilledRows(this.edaBiopsias.controls.map((control) => control.getRawValue())).map(
        (row: Record<string, unknown>) => ({
          ...row,
          n_lesiones: this.asNullableInteger(row['n_lesiones']),
        })
      ),
      diagnosticos: this.filterFilledRows(this.edaDiagnosticos.controls.map((control) => control.getRawValue())).map(
        (row: Record<string, unknown>, index: number) => ({
          texto: String(row['texto'] ?? '').trim(),
          orden: this.asInteger(row['orden'], index),
        })
      ),
      sugerencias: this.filterFilledRows(this.edaSugerencias.controls.map((control) => control.getRawValue())).map(
        (row: Record<string, unknown>, index: number) => ({
          texto: String(row['texto'] ?? '').trim(),
          orden: this.asInteger(row['orden'], index),
        })
      ),
    };
  }

  private filterFilledRows(rows: Record<string, unknown>[]): Record<string, unknown>[] {
    return rows.filter((row) => Object.values(row).some((value) => this.hasContent(value)));
  }

  private hasContent(value: unknown): boolean {
    return value !== null && value !== undefined && String(value).trim() !== '';
  }

  private asNumber(value: unknown): number {
    return Number(value);
  }

  private asInteger(value: unknown, fallback = 0): number {
    const parsed = Number.parseInt(String(value ?? ''), 10);
    return Number.isFinite(parsed) ? parsed : fallback;
  }

  private asNullableInteger(value: unknown): number | null {
    if (!this.hasContent(value)) {
      return null;
    }

    const parsed = Number.parseInt(String(value), 10);
    return Number.isFinite(parsed) ? parsed : null;
  }

  private asNullableDecimal(value: unknown): number | null {
    if (!this.hasContent(value)) {
      return null;
    }

    const parsed = Number.parseFloat(String(value));
    return Number.isFinite(parsed) ? parsed : null;
  }

  private asNullableNumber(value: unknown): number | null {
    if (!this.hasContent(value)) {
      return null;
    }

    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : null;
  }

  private asNullableBoolean(value: unknown): boolean | null {
    if (value === null || value === undefined || value === '') {
      return null;
    }

    return value === true || value === 'true';
  }

  private normalizePeruPhone(value: unknown): string {
    const digits = String(value ?? '').replace(/\D+/g, '');
    if (!digits) {
      return '';
    }

    const normalized = digits.startsWith('51') ? digits.slice(2) : digits;
    return normalized.length === 9 && normalized.startsWith('9') ? normalized : '';
  }

  private latestPatientReport(patientId: number): { kind: 'colonoscopia' | 'eda'; id: number; createdAt: number } | null {
    const reports = [
      ...this.colonoscopias().filter((report) => report.paciente === patientId).map((report) => ({
        kind: 'colonoscopia' as const,
        id: report.id,
        createdAt: Date.parse(report.creado_en),
      })),
      ...this.edas().filter((report) => report.paciente === patientId).map((report) => ({
        kind: 'eda' as const,
        id: report.id,
        createdAt: Date.parse(report.creado_en),
      })),
    ];

    if (!reports.length) {
      return null;
    }

    return reports.reduce((latest, current) => (current.createdAt > latest.createdAt ? current : latest));
  }

  private today(): string {
    return new Date().toISOString().slice(0, 10);
  }

  private formatError(error: unknown): string {
    if (error && typeof error === 'object' && 'message' in error) {
      return String((error as { message: unknown }).message);
    }

    return 'Ocurrió un error inesperado.';
  }

  private resetWorkspaceState(): void {
    this.patients.set([]);
    this.personnel.set([]);
    this.procedureCatalog.set([]);
    this.colonoscopias.set([]);
    this.edas.set([]);
    this.images.set([]);
    this.lastColonoscopiaId.set(null);
    this.lastEdaId.set(null);
    this.statusMessage.set('Inicia sesión para cargar la información del sistema.');
    this.errorMessage.set(null);
    this.activeTab.set('resumen');
  }
}
