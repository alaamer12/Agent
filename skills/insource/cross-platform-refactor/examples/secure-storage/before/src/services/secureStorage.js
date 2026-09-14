// src/services/secureStorage.js  ❌ shared file, secretly platform-specific, AND plain JS (no static types)
import { Platform } from 'react-native';
import * as Keychain from 'react-native-keychain';
import EncryptedStorage from 'react-native-encrypted-storage';

export async function saveSecret(key, value) {
  if (Platform.OS === 'ios') {
    // iOS Keychain has its own API shape (service/account pairing)
    await Keychain.setGenericPassword(key, value, { service: key });
  } else if (Platform.OS === 'android') {
    // Android side uses a totally different encrypted-storage library
    await EncryptedStorage.setItem(key, value);
  }
  // any other platform (web, desktop): silently does nothing — nobody decided that on purpose
}

export async function getSecret(key) {
  if (Platform.OS === 'ios') {
    const creds = await Keychain.getGenericPassword({ service: key });
    return creds ? creds.password : null;
  } else if (Platform.OS === 'android') {
    return EncryptedStorage.getItem(key);
  }
  return null;
}
