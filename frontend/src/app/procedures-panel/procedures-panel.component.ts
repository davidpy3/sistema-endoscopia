import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component, EventEmitter, Input, Output, computed, signal } from '@angular/core';

import { ImageCategoriesPanelComponent } from '../image-categories-panel/image-categories-panel.component';
import { ImagenEndoscopica, ProcedureCatalogItem } from '../models';

type ProcedureSection = 'procedimientos' | 'imagenes';

type ProcedureSectionTab = {
  id: ProcedureSection;
  label: string;
  description: string;
};

const PROCEDURE_TABS: ProcedureSectionTab[] = [
  { id: 'procedimientos', label: 'Catálogo', description: 'Tipos disponibles' },
  { id: 'imagenes', label: 'Imágenes', description: 'Galería y consulta' },
];

@Component({
  selector: 'app-procedures-panel',
  standalone: true,
  imports: [CommonModule, ImageCategoriesPanelComponent],
  templateUrl: './procedures-panel.component.html',
  styleUrl: './procedures-panel.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ProceduresPanelComponent {
  private readonly proceduresSignal = signal<ProcedureCatalogItem[]>([]);
  private readonly imagesSignal = signal<ImagenEndoscopica[]>([]);
  protected readonly imagesList = computed(() => this.imagesSignal());

  @Input({ required: true })
  set procedures(value: ProcedureCatalogItem[]) {
    this.proceduresSignal.set(value ?? []);
  }

  @Input({ required: true })
  set images(value: ImagenEndoscopica[]) {
    this.imagesSignal.set(value ?? []);
  }

  @Input() activeSection: ProcedureSection = 'procedimientos';

  @Output() readonly sectionChange = new EventEmitter<ProcedureSection>();

  protected readonly tabs = computed(() => PROCEDURE_TABS);

  protected readonly filteredProcedures = computed(() => this.proceduresSignal());

  protected selectCategory(category: ProcedureSection): void {
    this.sectionChange.emit(category);
  }

}