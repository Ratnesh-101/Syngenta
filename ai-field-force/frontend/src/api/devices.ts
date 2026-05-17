import { client, MOCK_MODE, mockDelay } from './client';
import { MOCK_DEVICES } from './mockData';
import { adaptDevice } from './adapters';
import type { Device } from '../types';

let mockDevices = [...MOCK_DEVICES];

function currentDeviceId(): string | undefined {
  return localStorage.getItem('field_force_device_id') ?? undefined;
}

export async function getDevices(): Promise<Device[]> {
  if (MOCK_MODE) return mockDelay(mockDevices);
  const { data } = await client.get<unknown[]>('/devices/');
  const cur = currentDeviceId();
  return data.map((d) => adaptDevice(d as Parameters<typeof adaptDevice>[0], cur));
}

export async function revokeDevice(device_id: string): Promise<void> {
  if (MOCK_MODE) {
    await mockDelay(null);
    mockDevices = mockDevices.filter((d) => d.device_id !== device_id);
    return;
  }
  await client.delete(`/devices/${device_id}`);
}