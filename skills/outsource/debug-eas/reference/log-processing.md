# EAS Log Processing & Error Patterns

This reference document provides technical details on how to interpret EAS build logs and the specific filtering logic used by `scripts/clean_eas_logs.py`.

## Cleaner Implementation Details

The `clean_eas_logs.py` script uses the following logic to reduce noise:

### JSON Collapsing
Large configuration objects (like `app.json` or EAS internal configs) are detected and minimized into a single line to prevent them from pushing relevant logs out of the view buffer.

### Gradle Progress Filtering
In the `RUN_GRADLEW` phase, the following patterns are considered noise and stripped unless they contain error indicators:
- `> IDLE`
- `Building ...`
- `Starting ...`
- `Working ...`
- `Executing ...`
- `Finishing ...`

### Error Detection
When `--errors-only` is used, the script looks for:
- JSON `result` field equal to `error` or `failed`.
- Keywords in `msg`: `error`, `failed`, `exception`, `err:`.
- Phase completion markers where the status is not `success`.

## Common EAS Error Patterns

### Gradle Resolution Failures
**Symptom**: `RUN_GRADLEW` fails early with `Could not resolve all files for configuration`.
**Cause**: Usually a conflict between two native modules requiring different versions of the same dependency (e.g., `react-native-reanimated` vs `react-native-gesture-handler`).
**Resolution**: Check `node_modules` and consider using `yarn resolutions` or `npm overrides` in `package.json`.

### App Config Syntax Errors
**Symptom**: `READ_APP_CONFIG` fails with a JavaScript error.
**Cause**: Syntax error in `app.config.js` or a missing environment variable that the config file expects.
**Resolution**: Run `bunx expo config` locally to verify the configuration resolves correctly.

### Custom Tool Installation
**Symptom**: `INSTALL_CUSTOM_TOOLS` fails.
**Cause**: EAS builder cannot download a required tool (e.g., a specific NDK version or CLI).
**Resolution**: Often a transient Expo service issue, but can be caused by requesting an incompatible `image` in `eas.json`.
