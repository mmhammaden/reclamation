# reclamations_mobile
Application mobile ISCAE - Gestion des Réclamations (Étudiants)

## Getting Started

### Prerequisites
- Flutter SDK 3.12+
- Android SDK (for Android deployment)
- Physical Android device with USB debugging enabled (for physical device testing)

### Setup Mobile App
```bash
cd mobile
flutter pub get
```

---

## Running on Emulator vs Physical Device
The app uses environment variables to dynamically set the API URL.

### For Android Emulator
```bash
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000
```

### For Physical Android Device
```bash
flutter run --dart-define=API_BASE_URL=http://<YOUR_PC_IP>:8000
```
Replace `<YOUR_PC_IP>` with your computer's local IP address (e.g., `192.168.1.100`).

---

## Testing on Physical Device

### Method 1: USB Debugging (Recommended)
1. **Enable Developer Options on your Android device:**
   - Go to **Settings > About Phone**
   - Tap **"Build Number"** 7 times
   - Go back to **Settings > System > Developer Options**
   - Enable **"USB Debugging"**

2. **Connect your device via USB cable**

3. **Verify device detection:**
   ```bash
   flutter devices
   ```
   Your device should appear in the list.

4. **Run the app:**
   ```bash
   # From the project root
   flutter run --dart-define=API_BASE_URL=http://10.243.252.189:8000
   ```

---

### Method 2: Using APK File
1. **Build the APK:**
   ```bash
   flutter build apk --dart-define=API_BASE_URL=http://10.243.252.189:8000
   ```

2. **Find the APK:**
   - Location: `mobile/build/app/outputs/flutter-apk/app-release.apk`

3. **Transfer and install:**
   - Transfer the APK to your device
   - Enable **"Install from unknown sources"** in Settings
   - Install and open the app

---

### Method 3: Using ngrok (For external access)
If you need to test from outside your local network:
1. **Start ngrok tunnel:**
   ```bash
   ngrok http 8000
   ```

2. **Copy the HTTPS forwarding URL** (e.g., `https://abc123.ngrok.io`)

3. **Build with ngrok URL:**
   ```bash
   flutter build apk --dart-define=API_BASE_URL=https://abc123.ngrok.io
   ```

---

## Backend Setup
Ensure the backend is running and accessible:
```bash
# Using Docker (recommended)
docker-compose up --build

# Or without Docker
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Network Configuration
The backend must accept connections from your device. Add your IP to `ALLOWED_HOSTS` in `.env`:
```javascript
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,10.243.252.189,<YOUR_PC_IP>
```

---

## Environment Variables
The app supports the following build-time variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `API_BASE_URL` | Backend API URL | `http://10.243.252.189:8000` |

---

## Features
- Authentication with matricule and password (JWT)
- View student notes
- Create and manage reclamations
- Notification system
- Offline support with local caching

---

## Troubleshooting

### "Connexion au serveur impossible"
- Ensure backend is running: `docker-compose up -d` or `python manage.py runserver`
- Check your PC's IP address: `ipconfig` (Windows) or `ifconfig` (Linux/Mac)
- Verify device and PC are on the same network

### "Session expirée"
- Tokens expire after 15 minutes (access) or 7 days (refresh)
- Refresh happens automatically, or re-login

### Device not detected
- Check USB cable connection
- Install proper USB drivers for your device
- Accept debugging permission on device

---

## Known Issues & Workarounds

### Gradle Build Compatibility (Android SDK 36)
If you encounter build errors with `file_picker` or other plugins related to Android SDK compatibility:
1. **Use the pre-built APK** (if available from a previous successful build)
2. **Downgrade compileSdk** to 34 in `mobile/android/app/build.gradle.kts`:
   ```kotlin
   compileSdk = 34
   ```
   Then run:
   ```bash
   cd mobile && flutter clean && flutter run --dart-define=API_BASE_URL=http://10.243.252.189:8000
   ```
3. **Run directly on device** without building APK - this is the recommended approach for testing:
   ```bash
   flutter run --dart-define=API_BASE_URL=http://10.243.252.189:8000
   ```
   The `--dart-define` flag allows you to set the API URL at runtime without rebuilding the APK.

---

## Additional Notes
- For iOS testing, replace `10.0.2.2` with `localhost` in the API URL.
- Ensure the backend CORS settings allow requests from your device's IP or the ngrok URL.