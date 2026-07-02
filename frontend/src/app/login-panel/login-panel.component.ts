import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { ReactiveFormsModule, UntypedFormBuilder, Validators } from '@angular/forms';

import { AuthService } from '../auth.service';

@Component({
  selector: 'app-login-panel',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './login-panel.component.html',
  styleUrl: './login-panel.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LoginPanelComponent {
  private readonly fb = inject(UntypedFormBuilder);
  protected readonly auth = inject(AuthService);

  protected readonly form = this.fb.group({
    username: ['', Validators.required],
    password: ['', Validators.required],
  });

  protected async submit(): Promise<void> {
    if (this.form.invalid) {
      return;
    }

    await this.auth.login(this.form.getRawValue() as { username: string; password: string });
    this.form.reset({ username: '', password: '' });
  }
}
