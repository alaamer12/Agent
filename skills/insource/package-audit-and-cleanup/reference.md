# Package Audit Reference

## Audit Script (Node.js)

This script can be used to scan a package for dependency usage. Save it to `scratch/audit.js` and run it with `node scratch/audit.js`.

```javascript
import fs from 'fs';
import path from 'path';

// CONFIGURATION
const PACKAGE_PATH = path.resolve('packages/my-package');
const SRC_DIRS = [path.join(PACKAGE_PATH, 'src')];
const CONFIG_FILES = [
    path.join(PACKAGE_PATH, 'babel.config.js'),
    path.join(PACKAGE_PATH, 'metro.config.js'),
    path.join(PACKAGE_PATH, 'app.json'),
    path.join(PACKAGE_PATH, 'tamagui.config.ts')
];

function getAllFiles(dirPath, arrayOfFiles) {
    if (!fs.existsSync(dirPath)) return arrayOfFiles || [];
    const files = fs.readdirSync(dirPath);
    arrayOfFiles = arrayOfFiles || [];

    files.forEach(function(file) {
        if (fs.statSync(dirPath + "/" + file).isDirectory()) {
            if (file !== 'node_modules' && file !== 'dist' && file !== '.turbo') {
                arrayOfFiles = getAllFiles(dirPath + "/" + file, arrayOfFiles);
            }
        } else {
            arrayOfFiles.push(path.join(dirPath, "/", file));
        }
    });

    return arrayOfFiles;
}

function checkUsage(lib) {
    const files = [];
    SRC_DIRS.forEach(p => files.push(...getAllFiles(p)));
    CONFIG_FILES.forEach(p => { if (fs.existsSync(p)) files.push(p); });

    for (const file of files) {
        if (file.endsWith('.ts') || file.endsWith('.tsx') || file.endsWith('.js') || file.endsWith('.jsx') || file.endsWith('.json')) {
            const content = fs.readFileSync(file, 'utf8');
            
            // Regex for various import patterns
            const importRegex = new RegExp(`from\\s+['"]${lib}(/.*)?['"]`, 'g');
            const requireRegex = new RegExp(`require\\(['"]${lib}(/.*)?['"]\\)`, 'g');
            const sideEffectImportRegex = new RegExp(`import\\s+['"]${lib}(/.*)?['"]`, 'g');
            
            if (importRegex.test(content) || requireRegex.test(content) || sideEffectImportRegex.test(content)) {
                return true;
            }
        }
    }
    return false;
}

const packageJsonPath = path.join(PACKAGE_PATH, 'package.json');
const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
const dependencies = Object.keys(packageJson.dependencies || {});

const report = {
    used: [],
    unused: []
};

for (const dep of dependencies) {
    // Skip workspace dependencies if you only want external ones, or keep them to check internal redundancy
    if (checkUsage(dep)) {
        report.used.push(dep);
    } else {
        report.unused.push(dep);
    }
}

console.log(JSON.stringify(report, null, 2));
```

## Common "Redundant" Patterns in this Repo

| Library | Redundant if... |
|---------|-----------------|
| `react-i18next` | Package uses `@kit/i18n` |
| `expo-haptics` | Package uses `@kit/shared` (check `utils/haptics.ts`) |
| `expo-router` | Package uses `@kit/features-shared` |
| `use-count-up` | Package uses `CountUpNumber` from `@snduk/primitives` |
| `nanoid` | Package can use `crypto.randomUUID()` or shared utils |

## Verification Commands

Run these from the root after making changes:

```powershell
# 1. Sync lockfile
bun install

# 2. Check types (specific package)
cd packages/my-package; bun run typecheck

# 3. Check types (all features)
bunx turbo run typecheck --filter="./packages/features/*"
```
