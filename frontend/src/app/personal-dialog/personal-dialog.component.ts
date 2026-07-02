import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component, EventEmitter, Output, inject } from '@angular/core';
import { ReactiveFormsModule, UntypedFormBuilder, Validators } from '@angular/forms';

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

  @Output() readonly submitted = new EventEmitter<PersonalFormValue>();
  @Output() readonly closed = new EventEmitter<void>();

  protected readonly form = this.fb.group({
    nombre_completo: ['', Validators.required],
    rol: ['medico', Validators.required],
    colegiatura: [''],
    activo: [true],
  });

  protected submit(): void {
    if (this.form.invalid) {
      return;
    }

    this.submitted.emit(this.form.getRawValue() as PersonalFormValue);
    this.form.reset({ nombre_completo: '', rol: 'medico', colegiatura: '', activo: true });
  }

  protected reset(): void {
    this.form.reset({ nombre_completo: '', rol: 'medico', colegiatura: '', activo: true });
  }

  protected close(): void {
    this.closed.emit();
  }
}
