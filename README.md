# Halla RU — Russian localization add-on

Russian interface translation for **Halla Desktop v1.1.37**. A native Qt 6.8.3
plug-in that leaves the official `Halla.exe` binary unchanged.

## Build

Open [Actions → Build Halla RU native addon](../../actions/workflows/build-addon.yml)
and run the workflow. A push touching code/translations also runs it automatically.

Download the artifact `Halla-RU-0.2.0-Windows-x64`; unpack its outer ZIP to
get `Halla-RU-0.2.0.halla-addon` and its SHA256 checksum.

In Halla: **Add-ons → Manage add-ons → Install package**; select the
`.halla-addon`, approve the native code warning and restart Halla entirely.

## Editing translations

Manual Portuguese→Russian and English→Russian overrides are stored as a
regular gzip file: `translations/overrides.json.gz`. Extract it using
`gzip -dk` or Python `gzip.decompress` to edit its JSON contents, then
recompress and push. CI expands it before running tests. All other source files
are plain text in this repository.

On each build, `scripts/build_catalog.py` combines manual Russian overrides
with the original Halla `translations/halla_en.ts`. Where a manual translation
is missing, official English is used as a fallback. The installed JSON catalog
may also be edited locally; restart Halla to reload.

## Security and compatibility

- No DLL injection, OS hooks, network calls, process enumeration, or microphone access.
- Capabilities are empty in the plugin manifest. **This is not sandboxing.**
  Native Halla plug-ins execute in the Halla process with the same permissions.
- Uses `QTranslator` directly, not an official Halla localization plug-in API.
- Match the Qt minor version of the client (6.8.3 for Halla v1.1.37).
- The generated DLL is unsigned and not independently runtime-tested yet.
- This translates application strings only, not the Windows installer.

Upstream SDK: https://github.com/GroupHalla/Halla/tree/v1.1.37/sdk
