import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component, EventEmitter, Output, inject } from '@angular/core';
import { ReactiveFormsModule, UntypedFormBuilder, Validators } from '@angular/forms';

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

  protected submit(): void {
    if (this.form.invalid) {
      return;
    }

    this.submitted.emit(this.form.getRawValue() as PatientFormValue);
    this.form.reset({ nombres: '', apellidos: '', dni: '', fecha_nacimiento: '', sexo: '', telefono: '' });
  }

  protected reset(): void {
    this.form.reset({ nombres: '', apellidos: '', dni: '', fecha_nacimiento: '', sexo: '', telefono: '' });
  }

  protected close(): void {
    this.closed.emit();
  }
}
