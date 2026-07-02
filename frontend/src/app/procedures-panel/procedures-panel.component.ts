import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component, ElementRef, EventEmitter, Input, OnChanges, Output, SimpleChanges, ViewChild, computed, signal } from '@angular/core';
import { ReactiveFormsModule, UntypedFormGroup } from '@angular/forms';

import { ProcedureCatalogItem } from '../models';

type ProcedureCategory = 'all' | 'endoscopia' | 'colonoscopia' | 'laparoscopia' | 'cpre' | 'otros';

type ProcedureCategoryTab = {
  id: ProcedureCategory;
  label: string;
  description: string;
};

const PROCEDURE_TABS: ProcedureCategoryTab[] = [
  { id: 'all', label: 'Todas', description: 'Catálogo completo' },
  { id: 'endoscopia', label: 'Endoscopia', description: 'Endoscopia digestiva alta' },
  { id: 'colonoscopia', label: 'Colonoscopía', description: 'Estudio de colon' },
  { id: 'laparoscopia', label: 'Laparoscopía', description: 'Exploración mínimamente invasiva' },
  { id: 'cpre', label: 'CPRE', description: 'Endoscopia terapéutica avanzada' },
  { id: 'otros', label: 'Otros', description: 'Otros procedimientos' },
];

@Component({
  selector: 'app-procedures-panel',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './procedures-panel.component.html',
  styleUrl: './procedures-panel.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ProceduresPanelComponent implements OnChanges {
  private readonly proceduresSignal = signal<ProcedureCatalogItem[]>([]);

  @ViewChild('fileInput') private readonly fileInput?: ElementRef<HTMLInputElement>;

  @Input({ required: true })
  set procedures(value: ProcedureCatalogItem[]) {
    this.proceduresSignal.set(value ?? []);
  }

  @Input({ required: true })
  imageForm: UntypedFormGroup | null = null;

  @Input() selectedImageFile: File | null = null;

  @Input() canWrite = false;

  @Input() resetToken = 0;

  @Output() readonly imageSelected = new EventEmitter<File | null>();
  @Output() readonly uploadRequested = new EventEmitter<void>();
  @Output() readonly resetRequested = new EventEmitter<void>();

  protected readonly activeCategory = signal<ProcedureCategory>('all');

  protected readonly tabs = computed(() => {
    const availableCategories = new Set(this.proceduresSignal().map((procedure) => procedure.code as ProcedureCategory));
    return PROCEDURE_TABS.filter((tab) => tab.id === 'all' || availableCategories.has(tab.id));
  });

  protected readonly filteredProcedures = computed(() => {
    const activeCategory = this.activeCategory();
    const procedures = this.proceduresSignal();

    if (activeCategory === 'all') {
      return procedures;
    }

    return procedures.filter((procedure) => procedure.code === activeCategory);
  });

  protected readonly canUploadImages = computed(() => this.activeCategory() === 'colonoscopia' || this.activeCategory() === 'endoscopia');

  protected readonly uploadProcedureLabel = computed(() => {
    if (this.activeCategory() === 'colonoscopia') {
      return 'Colonoscopía';
    }

    if (this.activeCategory() === 'endoscopia') {
      return 'EDA';
    }

    return 'Selecciona Colonoscopía o EDA para subir imágenes';
  });

  protected selectCategory(category: ProcedureCategory): void {
    this.activeCategory.set(category);
    this.syncUploadProcedureType();
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['resetToken'] && !changes['resetToken'].firstChange) {
      this.clearFileInput();
    }

    this.syncUploadProcedureType();
  }

  protected onImageFileChange(event: Event): void {
    const input = event.target as HTMLInputElement;
    this.imageSelected.emit(input.files?.[0] ?? null);
  }

  protected submitImage(): void {
    this.uploadRequested.emit();
  }

  protected resetImage(): void {
    this.resetRequested.emit();
    this.clearFileInput();
  }

  private syncUploadProcedureType(): void {
    if (!this.imageForm || !this.canUploadImages()) {
      return;
    }

    const uploadType = this.activeCategory() === 'colonoscopia' ? 'colonoscopia' : 'eda';
    this.imageForm.get('tipo')?.setValue(uploadType, { emitEvent: false });
  }

  private clearFileInput(): void {
    if (this.fileInput) {
      this.fileInput.nativeElement.value = '';
    }
  }
}