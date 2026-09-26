// src/services/secureStorage.unsupported.js  ✅ new file — explicit, honest no-op
// Not a Capability (see references/principles.md) — secure storage is a Variant every
// platform SHOULD eventually support. This says "not implemented here yet" out loud
// instead of quietly returning null the same way a missing key would.
export const unsupportedSecureStorage = {
  async save() {
    if (__DEV__) console.warn('secureStorage: no implementation for this platform yet');
  },
  async get() {
    if (__DEV__) console.warn('secureStorage: no implementation for this platform yet');
    return null;
  },
};
