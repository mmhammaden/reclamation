import { Pipe, PipeTransform } from '@angular/core';
import { DatePipe } from '@angular/common';

@Pipe({ name: 'frDate', standalone: true })
export class FrDatePipe implements PipeTransform {
  private datePipe = new DatePipe('fr-FR');

  transform(value: string | Date | null | undefined): string {
    if (!value) return 'N/A';
    return this.datePipe.transform(value, 'dd/MM/yyyy, HH:mm') ?? 'N/A';
  }
}