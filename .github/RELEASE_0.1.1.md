## VALORANT Rank Yoinker 0.1.1

This maintenance release improves party detection and refreshes the packaged
Windows application for the Sonic1901 fork.

### Changes

- Detects newly formed enemy duos when one recent shared ranked match is
  confirmed by Riot's match-details roster.
- Keeps the stricter two-shared-match requirement for unverified history, which
  helps avoid grouping unrelated players.
- Keeps Riot's current party-presence data authoritative when it is available.
- Includes the repaired automatic updater for published releases from this
  repository.
- Adds example tracker and loadout screenshots to the project documentation.

### Downloads

- `vry-0.1.1-setup.exe` — recommended Windows installer.
- `vry-0.1.1-portable.zip` — portable onedir build.

### Notes

- VALORANT must be running for tracker data to be collected.
- If data is missing or incorrect, close and reopen the application.
- The **REFRESH** button checks the current menu/state and does not force a
  complete new Riot data collection.
