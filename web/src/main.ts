import { bootstrapApplication } from '@angular/platform-browser';
import { appConfig } from './app/app.config';
import { AppComponent } from './app/app.component';

bootstrapApplication(AppComponent, appConfig).catch((err) => {
  // Sanitize error before logging to prevent log injection attacks
  const safeMessage = typeof err === 'object' && err !== null
    ? (err.message || err.toString?.() || 'Unknown error').replace(/[\n\r]/g, ' ').substring(0, 500)
    : String(err).replace(/[\n\r]/g, ' ').substring(0, 500);
  console.error('Application bootstrap failed:', safeMessage);
});
