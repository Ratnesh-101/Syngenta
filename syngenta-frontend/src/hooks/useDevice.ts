import { useMemo } from 'react';

const DEVICE_KEY = 'field_force_device_id';
const DEVICE_NAME_KEY = 'field_force_device_name';

function detectPlatform(): string {
  const ua = navigator.userAgent;
  if (/android/i.test(ua)) return 'android';
  if (/iphone|ipad|ipod/i.test(ua)) return 'ios';
  if (/win/i.test(ua)) return 'windows';
  if (/mac/i.test(ua)) return 'macos';
  return 'web';
}

function generateDeviceName(platform: string): string {
  const names: Record<string, string> = {
    android: 'Android Phone',
    ios: 'iPhone',
    windows: 'Windows PC',
    macos: 'Mac',
    web: 'Web Browser',
  };
  return names[platform] ?? 'Unknown Device';
}

export function useDevice() {
  const deviceId = useMemo(() => {
    let id = localStorage.getItem(DEVICE_KEY);
    if (!id) {
      id = crypto.randomUUID();
      localStorage.setItem(DEVICE_KEY, id);
    }
    return id;
  }, []);

  const devicePlatform = useMemo(() => detectPlatform(), []);

  const deviceName = useMemo(() => {
    let name = localStorage.getItem(DEVICE_NAME_KEY);
    if (!name) {
      name = generateDeviceName(devicePlatform);
      localStorage.setItem(DEVICE_NAME_KEY, name);
    }
    return name;
  }, [devicePlatform]);

  return { deviceId, deviceName, devicePlatform };
}
