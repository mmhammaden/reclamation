import { Component, Input } from '@angular/core';
import { NgClass } from '@angular/common';

@Component({
  selector: 'app-loading-spinner',
  standalone: true,
  imports: [NgClass],
  template: `
    <div class="flex items-center justify-center" [class]="containerClass">
      <div class="animate-spin rounded-full border-t-2 border-b-2"
           [ngClass]="spinnerClasses">
      </div>
      @if (text) {
        <span class="ml-3 text-sm text-gray-500">{{ text }}</span>
      }
    </div>
  `,
})
export class LoadingSpinnerComponent {
  @Input() size: 'sm' | 'md' | 'lg' = 'md';
  @Input() text?: string;
  @Input() color?: string;
  @Input() containerClass = 'py-8';

  get spinnerClasses(): Record<string, boolean> {
    const sizes = {
      sm: 'h-5 w-5',
      md: 'h-8 w-8',
      lg: 'h-12 w-12',
    };
    const sizeClass = sizes[this.size as keyof typeof sizes] || sizes.md;
    return {
      [sizeClass]: true,
      'border-primary-600': !this.color,
    };
  }
}