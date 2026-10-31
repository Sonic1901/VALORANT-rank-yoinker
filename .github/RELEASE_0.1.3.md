## VALORANT Rank Yoinker 0.1.3

This maintenance release fixes the automatic updater for installer builds.

### Changes

- Fixes automatic updates for installs under Program Files. The updater now
  asks for administrator permission when it cannot write to the install folder,
  instead of silently relaunching the old version.
- Shows an error message, and keeps the downloaded update, if an update could
  not be installed. Details are saved to `%AppData%\vry\update.log`.
- Removes the "The batch file cannot be found." message shown after updating.
- Fixes a crash when the application is opened before VALORANT is running.

### Upgrading from 0.1.1 or 0.1.2

The updater in earlier versions cannot update installs under Program Files.
If you used the installer, download and run `vry-0.1.3-setup.exe` once.
Future updates will then install automatically.

### Downloads

- `vry-0.1.3-setup.exe` — recommended Windows installer.
- `vry-0.1.3-portable.zip` — portable onedir build.

### Notes

- VALORANT must be running for tracker data to be collected.
- If data is missing or incorrect, close and reopen the application.
- The **REFRESH** button checks the current menu/state and does not force a
  complete new Riot data collection.
