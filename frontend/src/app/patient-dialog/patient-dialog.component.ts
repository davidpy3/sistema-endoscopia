import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component, EventEmitter, Input, OnChanges, Output, SimpleChanges, inject } from '@angular/core';
import { ReactiveFormsModule, UntypedFormBuilder, Validators } from '@angular/forms';

import { Paciente } from '../models';

export type PatientDialogMode = 'create' | 'edit' | 'view';

export interface PatientFormValue {
  nombres: string;
  apellidos: string;
  dni: string;
  fecha_nacimiento: string;
  sexo: string;
  telefono: string;
}

@Component({
  selector: 'app-patient-dialog',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './patient-dialog.component.html',
  styleUrl: './patient-dialog.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PatientDialogComponent {
  private readonly fb = inject(UntypedFormBuilder);

  @Input() initialData: Paciente | null = null;
  @Input() mode: PatientDialogMode = 'create';

  @Output() readonly submitted = new EventEmitter<PatientFormValue>();
  @Output() readonly closed = new EventEmitter<void>();

  protected readonly sexoOptions = [
    { value: '', label: '—' },
    { value: 'M', label: 'Masculino' },
    { value: 'F', label: 'Femenino' },
  ];

  protected readonly form = this.fb.group({
    nombres: ['', Validators.required],
    apellidos: ['', Validators.required],
    dni: ['', [Validators.required, Validators.minLength(8), Validators.maxLength(8)]],
    fecha_nacimiento: [''],
    sexo: [''],
    telefono: [''],
  });

  ngOnChanges(_: SimpleChanges): void {
    this.syncForm();
  }

  protected get isReadOnly(): boolean {
    return this.mode === 'view';
  }

  protected get title(): string {
    if (this.mode === 'edit') {
      return 'Editar paciente';
    }
    if (this.mode === 'view') {
      return 'Datos del paciente';
    }
    return 'Nuevo paciente';
  }

  protected get submitLabel(): string {
    return this.mode === 'edit' ? 'Guardar cambios' : 'Guardar paciente';
  }

  protected get actionLabel(): string {
    return this.mode === 'edit' ? 'Editar' : 'Ver';
  }

  protected submit(): void {
    if (this.isReadOnly || this.form.invalid) {
      return;
    }

    const rawValue = this.form.getRawValue() as PatientFormValue;
    this.submitted.emit({
      ...rawValue,
      telefono: this.normalizePeruPhone(rawValue.telefono),
    });
    if (this.mode === 'create') {
      this.form.reset({ nombres: '', apellidos: '', dni: '', fecha_nacimiento: '', sexo: '', telefono: '' });
    }
  }

  protected reset(): void {
    this.syncForm();
  }

  protected close(): void {
    this.closed.emit();
  }

  private syncForm(): void {
    const value = this.initialData;
    const defaults = {
      nombres: value?.nombres ?? '',
      apellidos: value?.apellidos ?? '',
      dni: value?.dni ?? '',
      fecha_nacimiento: value?.fecha_nacimiento ?? '',
      sexo: value?.sexo ?? '',
      telefono: value?.telefono ?? '',
    };

    this.form.reset(defaults);
    if (this.isReadOnly) {
      this.form.disable({ emitEvent: false });
    } else {
      this.form.enable({ emitEvent: false });
    }
  }

  private normalizePeruPhone(value: string): string {
    const digits = String(value ?? '').replace(/\D+/g, '');
    if (!digits) {
      return '';
    }

    const normalized = digits.startsWith('51') ? digits.slice(2) : digits;
    return normalized.startsWith('9') && normalized.length === 9 ? normalized : '';
  }
}
