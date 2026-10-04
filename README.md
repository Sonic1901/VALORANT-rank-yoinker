<p align="center">
    <img src="assets/Logo.png" alt="Logo" width="160" height="160">
<h5 align="center"> VALORANT rank yoinker GUI</h5>

This fork combines the original tracker with the WebView2 desktop interface,
encounter history, party detection, and loadout viewer from several community
forks. It keeps the main tracker focused on ranks and match context: weapon
cosmetic columns and delta RR are intentionally not shown on the main page.

---

  <ol>
    <li><a href="#about-the-project">About The Project</a></li>
    <li><a href="#what-this-fork-adds">What This Fork Adds</a></li>
    <li><a href="#prerequisites">Prerequisites</a></li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#acknowledgements">Acknowledgements</a></li>
    <li><a href="#disclaimer">Disclaimer</a></li>
  </ol>


## About The Project

VALORANT rank yoinker GUI is a community fork of [zayKenyon's original
vRY](https://github.com/zayKenyon/VALORANT-rank-yoinker). It replaces the
terminal display with a desktop window powered by Microsoft Edge WebView2,
while preserving the original local-client rank tracking workflow.

![Tracker view](assets/tracker.png)

![Loadouts view](assets/loadouts-1.png)
![Loadouts details](assets/loadouts-2.png)

## Prerequisites

- **Microsoft Edge WebView2 Runtime** — required for the GUI to function.
  - Already included on **Windows 11**.
  - **Windows 10** users can download it from [Microsoft's website](https://developer.microsoft.com/en-us/microsoft-edge/webview2/).
- **Microsoft Visual C++ Libraries** — download from [here](https://github.com/abbodi1406/vcredist/releases).

The bundled installer checks for WebView2 and the Microsoft Visual C++ x64
runtime and downloads missing prerequisites from Microsoft's official
redistributable URLs. The portable ZIP does not perform this prerequisite
installation automatically.

## Usage

### Bundled Release:

1) Install the [prerequisites](#prerequisites) above if needed.
2) Obtain the `vry-{version}-setup.exe` installer from the person who built this fork.
3) Run the installer and choose an installation location.
4) Launch **vry** from the Start menu or desktop shortcut.

Releases are built from this repository using the included GitHub Actions workflow.

### Running from source:

1) Download Python [3.11](https://www.python.org/downloads/release/python-3119/) or [3.10](https://www.python.org/downloads/release/python-31011/), making sure it is added to PATH.
2) Download or clone this source folder.
3) Run **`INSTALL.bat`**. This creates an isolated `.venv` and installs the pinned dependencies.
4) Run **`START.bat`** to launch the WebView2 application. VALORANT may already be open.
5) Use **REFRESH** in the app header when you want the tracker to check
   whether VALORANT has changed menus. This only checks the current menu/state;
   it does not force a new rank, match, encounter, or loadout data collection.
6) If information is missing or incorrect after refresh, close and reopen
   the application so it starts a fresh tracking session.
7) Use **LOADOUTS** in the app header to open the local loadout page inside the application.
8) Keep the project folder together while running from source; the loadout page and
   bundled metadata are served from the `docs` directory.

### Compiling from source:

The included GitHub Actions workflow uses PyInstaller and Inno Setup to produce both
an onedir executable and an installer. To compile locally:

1) Install Python 3.11 and run **`INSTALL.bat`**.
2) Install [Inno Setup](https://jrsoftware.org/isinfo.php) if you want an installer.
3) Build the portable folder:

```powershell
.venv\Scripts\python.exe -m PyInstaller --noconsole --onedir --name vry `
  --add-data "vry-gui.html;." --add-data "docs;docs" --add-data "assets;assets" `
  --add-data "src;src" --add-data "updatescript.bat;." --icon=assets\Logo.ico `
  --collect-all webview --collect-all websocket_server launcher.py
```

4) Test the portable build in `dist\vry` by running `dist\vry\vry.exe`.
5) After the portable build works, compile the installer:

```powershell
iscc installer.iss /DMyAppVersion=0.1.0
```

The installer is written to `dist\vry-0.1.0-setup.exe`. The installer packages
the already-built `dist\vry` folder, so always rebuild PyInstaller before
creating an installer after source changes.

### Automatic updates

The packaged application checks the published releases for
[Sonic1901/VALORANT-rank-yoinker](https://github.com/Sonic1901/VALORANT-rank-yoinker)
when it starts. If a newer published release contains a portable ZIP, the
application asks whether to download and install it. The updater replaces the
current portable or installed files and then relaunches the application.

Draft releases, prereleases, and releases without a portable ZIP are ignored.
The first release must be published before update checks can find it. Do not
delete the portable ZIP from future releases.


### GitHub Actions:

The workflow in `.github/workflows/build.yml` builds tags or manually dispatched
runs on GitHub-hosted Windows runners. A successful run produces a portable ZIP
and an Inno Setup installer artifact. Friends can use either artifact; the installer
is easiest, while the portable ZIP does not require an installation step.

Create a version tag such as `0.1.0`, or run the workflow manually with a tag.
The workflow produces a portable ZIP and an Inno Setup installer.


## What about that Tweet?

The [Tweet](https://twitter.com/PlayVALORANT/status/1539728676815642624) outlines Riot's API policies. Applications are not allowed to expose data hidden by the game client. As of Version 1.262 of the original vRY, streamer mode is respected. This fork maintains that behaviour.


## Contributing

Contributions are **greatly appreciated**. Please open an issue first to discuss what you'd like to change.


## Acknowledgements

- [zayKenyon](https://github.com/zayKenyon) — original VALORANT rank yoinker and core tracker
- [fivepandasna/VALORANT-rank-yoinker](https://github.com/fivepandasna/VALORANT-rank-yoinker) — primary WebView2 GUI foundation and release/build structure
- [latenitekode/VALORANT-rank-yoinker](https://github.com/latenitekode/VALORANT-rank-yoinker) — request/presence improvements, encounter history, loadout page concepts, and complete loadout metadata conversion
- [resirch/VALORANT-rank-yoinker](https://github.com/resirch/VALORANT-rank-yoinker) — history-based party detection approach using shared competitive match IDs
- [Valorant-API.com](https://valorant-api.com/)
- [Hamper](https://hamper.dev/)
- [D3CRYPT](https://d3crypt360.pages.dev/)

## What This Fork Adds

The following features are included beyond the original tracker. The source fork
for each major addition is listed directly so the project history remains clear.

### Tracker and rank display

- **WebView2 desktop application** instead of a terminal-only interface —
  adapted from [fivepandasna's fork](https://github.com/fivepandasna/VALORANT-rank-yoinker).
- **Current-act ranked games played beside win rate**, for example `54% (120)`.
- **Current rank RR and leaderboard placement** on the same rank line for
  Immortal 1, Immortal 2, Immortal 3, and Radiant.
- **Peak rank episode/act display** with rank-matched styling.
- **Server/pod information** beside the current map.
- **Streamer-mode-aware name handling**, retained from the original
  [zayKenyon tracker](https://github.com/zayKenyon/VALORANT-rank-yoinker).

### Encounter and premade history

- **Personal match history** with overall wins, losses, games played, and win rate.
- **Recurring teammate and enemy encounters** with map, agent, relationship, age,
  and compact games-ago context.
- **With/against records** shown as separate W/L totals.
- **Premade history** with general results and queued-together results.
- **Rare encounter handling** for previous names.
- **Match-result updates** that convert temporary unknown results when Riot makes
  the completed match details available.
- These history and encounter features are based primarily on
  [latenitekode's fork](https://github.com/latenitekode/VALORANT-rank-yoinker),
  with additional result tracking and formatting in this fork.

### Party detection

- **History-based party detection** using shared recent competitive match IDs,
  adapted from [resirch's fork](https://github.com/resirch/VALORANT-rank-yoinker).
- **Current Riot party membership** is treated as authoritative when available.
- **Same-team verification and direct pair matching** reduce false grouping when
  multiple parties are on the same team.
- **Short-lived party-history caching** limits repeated Riot requests.

### In-app loadouts

- **LOADOUTS tab inside the desktop app**, rather than opening a separate browser.
- **Weapon and skin loadouts** including chromas, buddies, sprays, flex items,
  player cards, titles, agents, and agent artwork.
- **Automatic public asset metadata retrieval and caching** through
  [Valorant-API.com](https://valorant-api.com/), so new cosmetics do not need
  to be manually copied into the repository.
- The loadout page and metadata conversion are based on
  [latenitekode's fork](https://github.com/latenitekode/VALORANT-rank-yoinker).
- Weapon cosmetics are intentionally kept out of the main tracker table to
  preserve its compact rank-focused layout.

### Reliability and packaging

- **Single-instance protection** prevents multiple tracker backends from
  competing for the same local port or showing stale data.
- **REFRESH control** wakes the tracker to check for a VALORANT menu/state
  change without forcing a full data refresh. If displayed information remains
  missing or incorrect, reopen the application to start a fresh session.
- **Bounded retries, timeouts, backoff, malformed-payload guards, and runtime
  caches** reduce crashes and unnecessary repeated requests.
- **Atomic local history writes** reduce the chance of corrupting encounter data
  if the app closes during a save.
- **Windows per-monitor DPI awareness**, source launch scripts, isolated
  dependency installation, PyInstaller packaging, and an Inno Setup installer.
- The WebView2/release structure is based on
  [fivepandasna's fork](https://github.com/fivepandasna/VALORANT-rank-yoinker).

### Maintainer

Maintained by [Sonic1901](https://github.com/Sonic1901).

## Privacy, credentials, and publication

- This fork uses the locally running VALORANT/Riot Client to obtain short-lived
  session credentials. It does not contain or require the original author's
  developer API key.
- Never commit or distribute the Riot lockfile, access/entitlements tokens,
  `%APPDATA%\vry\logs`, `stats.json`, or screenshots containing player
  identifiers. These files can contain account or match data.
- Do not put a Riot developer API key in source code, an installer, a binary, or
  a public configuration file. Riot's current VALORANT policy says products must
  be registered, must provide player opt-in through RSO for personal data, and
  that personal-key applications are not supported.
- Before publishing or distributing this as a public VALORANT product, review
  the current [Riot VALORANT policy](https://developer.riotgames.com/docs/valorant)
  and [general developer policies](https://developer.riotgames.com/policies/general).
  The current local-client flow should not be presented as a substitute for
  Riot's approved RSO/production-key flow.


## Disclaimer

THIS PROJECT IS NOT ASSOCIATED OR ENDORSED BY RIOT GAMES. Riot Games, and all associated properties are trademarks or registered trademarks of Riot Games, Inc.

Whilst effort has been made to abide by Riot's API rules, you acknowledge that use of this software is done so at your own risk.
