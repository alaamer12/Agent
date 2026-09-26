// src/services/secureStorage.ios.js  ✅ new file — iOS's real implementation
import * as Keychain from 'react-native-keychain';

export const iosSecureStorage = {
  async save(key, value) {
    await Keychain.setGenericPassword(key, value, { service: key });
  },
  async get(key) {
    const creds = await Keychain.getGenericPassword({ service: key });
    return creds ? creds.password : null;
  },
};
