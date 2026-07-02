import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component, EventEmitter, forwardRef, HostBinding, Input, OnChanges, Output, SimpleChanges, computed, signal } from '@angular/core';
import { ControlValueAccessor, NG_VALUE_ACCESSOR } from '@angular/forms';

export interface SearchableSelectOption {
  value: unknown;
  label: string;
  description?: string;
}

@Component({
  selector: 'app-searchable-select',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './searchable-select.component.html',
  styleUrl: './searchable-select.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
  providers: [
    {
      provide: NG_VALUE_ACCESSOR,
      useExisting: forwardRef(() => SearchableSelectComponent),
      multi: true,
    },
  ],
})
export class SearchableSelectComponent implements ControlValueAccessor, OnChanges {
  @Input() label = '';
  @Input() placeholder = 'Buscar...';
  @Input() noResultsText = 'Sin resultados';
  @Input() options: SearchableSelectOption[] = [];
  @Input() helperText = '';

  @Output() readonly openedChange = new EventEmitter<boolean>();

  @HostBinding('class.disabled') get isDisabledHost(): boolean {
    return this.disabled();
  }

  protected readonly query = signal('');
  protected readonly isOpen = signal(false);
  protected readonly disabled = signal(false);
  protected readonly selectedValue = signal<unknown>(null);

  private onChange: (value: unknown) => void = () => undefined;
  private onTouched: () => void = () => undefined;

  protected readonly filteredOptions = computed(() => {
    const normalizedQuery = this.query().trim().toLowerCase();
    const options = this.options ?? [];

    if (!normalizedQuery) {
      return options;
    }

    return options.filter((option) => {
      const haystack = `${option.label} ${option.description ?? ''}`.toLowerCase();
      return haystack.includes(normalizedQuery);
    });
  });

  protected readonly selectedOption = computed(() => {
    const value = this.selectedValue();
    return this.options.find((option) => Object.is(option.value, value)) ?? null;
  });

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['options']) {
      this.syncQueryWithSelection();
    }
  }

  writeValue(value: unknown): void {
    this.selectedValue.set(value ?? null);
    this.syncQueryWithSelection();
  }

  registerOnChange(fn: (value: unknown) => void): void {
    this.onChange = fn;
  }

  registerOnTouched(fn: () => void): void {
    this.onTouched = fn;
  }

  setDisabledState(isDisabled: boolean): void {
    this.disabled.set(isDisabled);
    if (isDisabled) {
      this.isOpen.set(false);
    }
  }

  protected open(): void {
    if (this.disabled()) {
      return;
    }

    this.isOpen.set(true);
    this.openedChange.emit(true);
  }

  protected close(): void {
    this.isOpen.set(false);
    this.openedChange.emit(false);
    this.onTouched();

    if (!this.selectedOption()) {
      this.syncQueryWithSelection();
    }
  }

  protected onInput(event: Event): void {
    const input = event.target as HTMLInputElement;
    this.query.set(input.value);
    this.isOpen.set(true);
    this.openedChange.emit(true);
  }

  protected selectOption(option: SearchableSelectOption): void {
    this.selectedValue.set(option.value);
    this.query.set(option.label);
    this.onChange(option.value);
    this.isOpen.set(false);
    this.openedChange.emit(false);
    this.onTouched();
  }

  protected clearSelection(event: Event): void {
    event.stopPropagation();
    if (this.disabled()) {
      return;
    }

    this.selectedValue.set(null);
    this.query.set('');
    this.onChange(null);
    this.isOpen.set(true);
    this.openedChange.emit(true);
  }

  protected trackByValue(_: number, option: SearchableSelectOption): string {
    return `${typeof option.value}:${String(option.value)}`;
  }

  private syncQueryWithSelection(): void {
    const selected = this.selectedOption();
    this.query.set(selected?.label ?? '');
  }
}
