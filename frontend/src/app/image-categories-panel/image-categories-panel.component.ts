import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component, Input, computed, signal } from '@angular/core';

import { ImagenEndoscopica } from '../models';

type ImageCategory = 'all' | 'colonoscopia' | 'eda' | 'endoscopia' | 'laparoscopia' | 'cpre' | 'otros';

@Component({
  selector: 'app-image-categories-panel',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './image-categories-panel.component.html',
  styleUrl: './image-categories-panel.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ImageCategoriesPanelComponent {
  private readonly imagesSignal = signal<ImagenEndoscopica[]>([]);

  @Input({ required: true })
  set images(value: ImagenEndoscopica[]) {
    this.imagesSignal.set(value ?? []);
  }

  protected readonly activeCategory = signal<ImageCategory>('all');

  protected readonly tabs = [
    { id: 'all' as const, label: 'Todas' },
    { id: 'colonoscopia' as const, label: 'Colonoscopía' },
    { id: 'eda' as const, label: 'EDA' },
    { id: 'endoscopia' as const, label: 'Endoscopia' },
    { id: 'laparoscopia' as const, label: 'Laparoscopía' },
    { id: 'cpre' as const, label: 'CPRE' },
    { id: 'otros' as const, label: 'Otros' },
  ];

  protected readonly filteredImages = computed(() => {
    const activeCategory = this.activeCategory();
    const images = this.imagesSignal();
    if (activeCategory === 'all') {
      return images;
    }

    return images.filter((image) => image.tipo_display?.toLowerCase() === activeCategory);
  });

  protected selectCategory(category: ImageCategory): void {
    this.activeCategory.set(category);
  }
}