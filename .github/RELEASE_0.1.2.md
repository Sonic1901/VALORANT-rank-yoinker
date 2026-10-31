## VALORANT Rank Yoinker 0.1.2

This maintenance release fixes party detection for players who are not on your
friends list.

### Changes

- Detects your full party using Riot's party service, so every member is marked
  as in your party even if they are not on the account's friends list (for
  example, when playing on an alt account).
- Falls back to the previous friends-list presence detection if the party
  service is unavailable.
- Saves party members as premades in encounter history, so their win/loss
  records are tracked as queued-together games.

### Downloads

- `vry-0.1.2-setup.exe` — recommended Windows installer.
- `vry-0.1.2-portable.zip` — portable onedir build.

### Notes

- VALORANT must be running for tracker data to be collected.
- If data is missing or incorrect, close and reopen the application.
- The **REFRESH** button checks the current menu/state and does not force a
  complete new Riot data collection.
