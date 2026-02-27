# NSIS Installer Configuration for JARVIS AI Desktop

These settings configure the Windows installer builder. With this setup:

1. **Installer Features:**
   - Clean, standard Windows installation wizard
   - Desktop shortcut creation
   - Start menu shortcuts
   - Uninstaller with file cleanup
   - Application registry entry

2. **Backend Connection:**
   - Installer prompts for backend URL (default: localhost:9000)
   - Stores configuration in app directory
   - Frontend automatically connects to configured backend
   - Easy URL reconfiguration via startup script

3. **Installation Paths:**
   - Default: C:\Program Files\JARVIS AI\
   - User: C:\Users\{username}\AppData\Local\JARVIS AI\
   - Portable: Any location (no registry)

4. **Next Steps:**
   - Build installer with npm run build:nsis
   - Distributes as single .exe file (~200MB with all dependencies)
   - Users get automatic uninstall support
   - Can run backend separately, then install frontend
