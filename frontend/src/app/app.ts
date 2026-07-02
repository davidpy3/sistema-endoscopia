import { CommonModule } from '@angular/common';
import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { ReactiveFormsModule, UntypedFormArray, UntypedFormBuilder, UntypedFormGroup, Validators } from '@angular/forms';
import { forkJoin, lastValueFrom } from 'rxjs';

import { EndoscopyApiService } from './endoscopy-api.service';
import { ImageCategoriesPanelComponent } from './image-categories-panel/image-categories-panel.component';
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
  PILORO_OPTIONS,
  SegmentOption,
  SEDATION_OPTIONS,
  SEXO_OPTIONS,
  SugerenciaColonoscopia,
  SugerenciaEDA,
} from './models';

type TabKey = 'resumen' | 'pacientes' | 'personal' | 'colonoscopias' | 'eda' | 'imagenes';

@Component({
  selector: 'app-root',
  imports: [CommonModule, ReactiveFormsModule, ImageCategoriesPanelComponent],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App implements OnInit {
  private readonly api = inject(EndoscopyApiService);
  private readonly fb = inject(UntypedFormBuilder);

  protected readonly tabs: Array<{ id: TabKey; label: string; description: string }> = [
    { id: 'resumen', label: 'Resumen', description: 'Métrica rápida y estado general' },
    { id: 'pacientes', label: 'Pacientes', description: 'Alta y consulta' },
    { id: 'personal', label: 'Personal', description: 'Médicos y enfermería' },
    { id: 'colonoscopias', label: 'Colonoscopías', description: 'Informe y borradores' },
    { id: 'eda', label: 'EDA', description: 'Informe y borradores' },
    { id: 'imagenes', label: 'Imágenes', description: 'Carga y consulta' },
  ];

  protected readonly activeTab = signal<TabKey>('resumen');
  protected readonly patientDialogOpen = signal(false);
  protected readonly personalDialogOpen = signal(false);
  protected readonly loading = signal(false);
  protected readonly statusMessage = signal('Sincroniza con el backend para empezar.');
  protected readonly errorMessage = signal<string | null>(null);

  protected readonly patients = signal<Paciente[]>([]);
  protected readonly personnel = signal<Personal[]>([]);
  protected readonly colonoscopias = signal<Colonoscopia[]>([]);
  protected readonly edas = signal<EDA[]>([]);
  protected readonly images = signal<ImagenEndoscopica[]>([]);

  protected readonly lastColonoscopiaId = signal<number | null>(null);
  protected readonly lastEdaId = signal<number | null>(null);

  protected readonly selectedImageFile = signal<File | null>(null);
  protected readonly selectedDraftFile = signal<File | null>(null);

  protected readonly doctors = computed(() =>
    this.personnel().filter((person) => person.rol === 'medico' && person.activo)
  );
  protected readonly nurses = computed(() =>
    this.personnel().filter((person) => person.rol === 'enfermera' && person.activo)
  );
  protected readonly stats = computed(() => ({
    patients: this.patients().length,
    personnel: this.personnel().length,
    colonoscopias: this.colonoscopias().length,
    edas: this.edas().length,
    images: this.images().length,
  }));

  protected readonly patientForm = this.createPatientForm();
  protected readonly personalForm = this.createPersonalForm();
  protected colonoscopiaForm = this.createColonoscopiaForm();
  protected edaForm = this.createEdaForm();
  protected readonly imageForm = this.createImageForm();
  protected readonly draftImportForm = this.fb.group({
    tipo: ['colonoscopia', Validators.required],
  });

  protected readonly sedationOptions = SEDATION_OPTIONS;
  protected readonly sexoOptions = SEXO_OPTIONS;
  protected readonly hillOptions = HILL_OPTIONS;
  protected readonly piloroOptions = PILORO_OPTIONS;
  protected readonly colonSegmentsData = COLON_SEGMENTS;
  protected readonly edaSegmentsData = EDA_SEGMENTS;

  async ngOnInit(): Promise<void> {
    await this.refreshAll();
  }

  protected setTab(tab: TabKey): void {
    this.activeTab.set(tab);
  }

  protected openPatientDialog(): void {
    this.patientDialogOpen.set(true);
  }

  protected closePatientDialog(): void {
    this.patientDialogOpen.set(false);
  }

  protected openPersonalDialog(): void {
    this.personalDialogOpen.set(true);
  }

  protected closePersonalDialog(): void {
    this.personalDialogOpen.set(false);
  }

  protected async refreshAll(): Promise<void> {
    this.loading.set(true);
    this.errorMessage.set(null);

    try {
      const payload = await lastValueFrom(
        forkJoin({
          patients: this.api.loadPatients(),
          personnel: this.api.loadPersonnel(),
          colonoscopias: this.api.loadColonoscopias(),
          edas: this.api.loadEdas(),
          images: this.api.loadImages(),
        })
      );

      this.patients.set(payload.patients);
      this.personnel.set(payload.personnel);
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

  protected async savePatient(): Promise<void> {
    if (this.patientForm.invalid) {
      this.statusMessage.set('Completa los campos del paciente antes de guardar.');
      return;
    }

    try {
      await lastValueFrom(this.api.create<Paciente>('pacientes', this.patientForm.getRawValue()));
      this.patientForm.reset({ nombres: '', apellidos: '', dni: '', fecha_nacimiento: '', sexo: '', telefono: '' });
      this.statusMessage.set('Paciente registrado correctamente.');
      this.closePatientDialog();
      await this.refreshAll();
    } catch (error) {
      this.errorMessage.set(this.formatError(error));
    }
  }

  protected async savePersonal(): Promise<void> {
    if (this.personalForm.invalid) {
      this.statusMessage.set('Completa los datos del personal antes de guardar.');
      return;
    }

    try {
      await lastValueFrom(this.api.create<Personal>('personal', this.personalForm.getRawValue()));
      this.personalForm.reset({ nombre_completo: '', rol: 'medico', colegiatura: '', activo: true });
      this.statusMessage.set('Personal registrado correctamente.');
      this.closePersonalDialog();
      await this.refreshAll();
    } catch (error) {
      this.errorMessage.set(this.formatError(error));
    }
  }

  protected async saveColonoscopia(): Promise<void> {
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

  protected onImageSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    this.selectedImageFile.set(input.files?.[0] ?? null);
  }

  protected onDraftSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    this.selectedDraftFile.set(input.files?.[0] ?? null);
  }

  protected resetPatientForm(): void {
    this.patientForm.reset({ nombres: '', apellidos: '', dni: '', fecha_nacimiento: '', sexo: '', telefono: '' });
  }

  protected resetPersonalForm(): void {
    this.personalForm.reset({ nombre_completo: '', rol: 'medico', colegiatura: '', activo: true });
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

  private createPatientForm() {
    return this.fb.group({
      nombres: ['', Validators.required],
      apellidos: ['', Validators.required],
      dni: ['', [Validators.required, Validators.minLength(8), Validators.maxLength(8)]],
      fecha_nacimiento: [''],
      sexo: [''],
      telefono: [''],
    });
  }

  private createPersonalForm() {
    return this.fb.group({
      nombre_completo: ['', Validators.required],
      rol: ['medico', Validators.required],
      colegiatura: [''],
      activo: [true],
    });
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

  private today(): string {
    return new Date().toISOString().slice(0, 10);
  }

  private formatError(error: unknown): string {
    if (error && typeof error === 'object' && 'message' in error) {
      return String((error as { message: unknown }).message);
    }

    return 'Ocurrió un error inesperado.';
  }
}
