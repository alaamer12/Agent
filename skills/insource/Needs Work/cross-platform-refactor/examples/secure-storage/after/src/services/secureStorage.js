// src/services/secureStorage.js  ✅ shared shell — defines the contract, zero platform logic
import { PlatformName, currentPlatformName } from '../platform/Platform';
import { iosSecureStorage } from './secureStorage.ios';
import { androidSecureStorage } from './secureStorage.android';
import { unsupportedSecureStorage } from './secureStorage.unsupported';

// The barrel: the ONLY place that switches on platform, and it switches on the
// closed PlatformName set from Platform.js — never a raw string literal.
function resolveSecureStorage() {
  switch (currentPlatformName()) {
    case PlatformName.IOS:
      return iosSecureStorage;
    case PlatformName.ANDROID:
      return androidSecureStorage;
    default:
      return unsupportedSecureStorage;
  }
}

export const secureStorage = resolveSecureStorage();
// call sites use: await secureStorage.save(key, value) / await secureStorage.get(key)
