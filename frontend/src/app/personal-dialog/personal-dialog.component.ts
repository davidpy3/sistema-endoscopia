import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component, EventEmitter, Input, OnChanges, Output, SimpleChanges, inject } from '@angular/core';
import { ReactiveFormsModule, UntypedFormBuilder, Validators } from '@angular/forms';

import { Personal } from '../models';

export type PersonalDialogMode = 'create' | 'edit' | 'view';

export interface PersonalFormValue {
  nombre_completo: string;
  rol: 'medico' | 'enfermera';
  colegiatura: string;
  activo: boolean;
}

@Component({
  selector: 'app-personal-dialog',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './personal-dialog.component.html',
  styleUrl: './personal-dialog.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PersonalDialogComponent {
  private readonly fb = inject(UntypedFormBuilder);

  @Input() initialData: Personal | null = null;
  @Input() mode: PersonalDialogMode = 'create';

  @Output() readonly submitted = new EventEmitter<PersonalFormValue>();
  @Output() readonly closed = new EventEmitter<void>();

  protected readonly form = this.fb.group({
    nombre_completo: ['', Validators.required],
    rol: ['medico', Validators.required],
    colegiatura: [''],
    activo: [true],
  });

  ngOnChanges(_: SimpleChanges): void {
    this.syncForm();
  }

  protected get isReadOnly(): boolean {
    return this.mode === 'view';
  }

  protected get title(): string {
    if (this.mode === 'edit') {
      return 'Editar personal';
    }
    if (this.mode === 'view') {
      return 'Datos del personal';
    }
    return 'Nuevo personal';
  }

  protected get submitLabel(): string {
    return this.mode === 'edit' ? 'Guardar cambios' : 'Guardar personal';
  }

  protected submit(): void {
    if (this.isReadOnly || this.form.invalid) {
      return;
    }

    this.submitted.emit(this.form.getRawValue() as PersonalFormValue);
    if (this.mode === 'create') {
      this.form.reset({ nombre_completo: '', rol: 'medico', colegiatura: '', activo: true });
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
      nombre_completo: value?.nombre_completo ?? '',
      rol: (value?.rol as 'medico' | 'enfermera') ?? 'medico',
      colegiatura: value?.colegiatura ?? '',
      activo: value?.activo ?? true,
    };

    this.form.reset(defaults);
    if (this.isReadOnly) {
      this.form.disable({ emitEvent: false });
    } else {
      this.form.enable({ emitEvent: false });
    }
  }
}
