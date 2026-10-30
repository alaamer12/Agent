// src/services/secureStorage.android.js  ✅ new file — Android's real implementation
import EncryptedStorage from 'react-native-encrypted-storage';

export const androidSecureStorage = {
  async save(key, value) {
    await EncryptedStorage.setItem(key, value);
  },
  async get(key) {
    return EncryptedStorage.getItem(key);
  },
};
