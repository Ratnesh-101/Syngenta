import { client, MOCK_MODE, mockDelay } from './client';
import { MOCK_DEVICES } from './mockData';
import type { Device } from '../types';

let mockDevices = [...MOCK_DEVICES];

export async function getDevices(): Promise<Device[]> {
  if (MOCK_MODE) return mockDelay(mockDevices);
  const { data } = await client.get<Device[]>('/devices/');
  return data;
}

export async function revokeDevice(device_id: string): Promise<void> {
  if (MOCK_MODE) {
    await mockDelay(null);
    mockDevices = mockDevices.filter((d) => d.device_id !== device_id);
    return;
  }
  await client.delete(`/devices/${device_id}`);
}
