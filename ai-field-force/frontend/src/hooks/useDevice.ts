import { useMemo } from 'react';

const DEVICE_KEY = 'field_force_device_id';
const DEVICE_NAME_KEY = 'field_force_device_name';

function detectPlatform(): 'android' | 'ios' | 'web' {
  const ua = navigator.userAgent;
  if (/android/i.test(ua)) return 'android';
  if (/iphone|ipad|ipod/i.test(ua)) return 'ios';
  return 'web';
}

function generateDeviceName(platform: string): string {
  const names: Record<string, string> = {
    android: 'Android Phone',
    ios: 'iPhone',
    web: 'Web Browser',
  };
  return names[platform] ?? 'Web Browser';
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