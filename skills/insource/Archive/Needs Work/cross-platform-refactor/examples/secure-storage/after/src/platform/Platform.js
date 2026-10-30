// src/platform/Platform.js  ✅ new file — explicit closed set of platform values.
// Plain JS has no compiler to catch a typo like 'Android' vs 'android' scattered across
// twenty files, so define ONE canonical, frozen set of values every other file imports
// from instead of writing raw string literals. (A TypeScript codebase would express this
// as `type PlatformName = 'ios' | 'android' | 'unsupported';` instead — same idea, enforced
// by the compiler rather than by convention. See references/principles.md "Platform".)
export const PlatformName = Object.freeze({
  IOS: 'ios',
  ANDROID: 'android',
  UNSUPPORTED: 'unsupported',
});

export function currentPlatformName() {
  // The ONE function in this whole feature allowed to ask the OS/runtime directly.
  const { Platform } = require('react-native');
  if (Platform.OS === 'ios') return PlatformName.IOS;
  if (Platform.OS === 'android') return PlatformName.ANDROID;
  return PlatformName.UNSUPPORTED;
}
