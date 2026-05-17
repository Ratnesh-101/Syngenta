import { client, MOCK_MODE, mockDelay, getErrorMessage } from './client';
import {
  MOCK_REP_AUTH,
  MOCK_MANAGER_AUTH,
} from './mockData';
import type { AuthResponse, OtpSendResponse, Rep } from '../types';

export async function loginWithPassword(identifier: string, password: string): Promise<AuthResponse> {
  if (MOCK_MODE) {
    await mockDelay(null);
    if (identifier.includes('manager')) return MOCK_MANAGER_AUTH;
    if (identifier === 'rep@syngenta.com' || identifier === '9999999999') return MOCK_REP_AUTH;
    throw new Error('Invalid credentials. Use rep@syngenta.com / syngenta123');
  }
  const { data } = await client.post<AuthResponse>('/auth/login/password', { identifier, password });
  return data;
}

export async function registerWithPassword(
  name: string, email: string, phone: string, password: string
): Promise<AuthResponse> {
  if (MOCK_MODE) {
    await mockDelay(null);
    return { ...MOCK_REP_AUTH, rep: { ...MOCK_REP_AUTH.rep, name, email, phone } };
  }
  const { data } = await client.post<AuthResponse>('/auth/register/password', { name, email, phone, password });
  return data;
}

export async function sendOtp(phone: string): Promise<OtpSendResponse> {
  if (MOCK_MODE) {
    await mockDelay(null, 600);
    return { message: 'OTP sent', dev_otp: '123456' };
  }
  const { data } = await client.post<OtpSendResponse>('/auth/otp/send', { phone });
  return data;
}

export async function verifyOtp(phone: string, code: string): Promise<AuthResponse> {
  if (MOCK_MODE) {
    await mockDelay(null, 500);
    if (code !== '123456') throw new Error('Invalid OTP. Use 123456 in demo mode.');
    return MOCK_REP_AUTH;
  }
  const { data } = await client.post<AuthResponse>('/auth/otp/verify', { phone, code });
  return data;
}

export async function loginWithGoogle(id_token: string): Promise<AuthResponse> {
  if (MOCK_MODE) {
    await mockDelay(null);
    return MOCK_REP_AUTH;
  }
  const { data } = await client.post<AuthResponse>('/auth/google/verify', { id_token });
  return data;
}

export async function getMe(): Promise<Rep> {
  if (MOCK_MODE) {
    await mockDelay(null, 200);
    const stored = localStorage.getItem('rep');
    if (stored) return JSON.parse(stored) as Rep;
    throw new Error('Not authenticated');
  }
  try {
    const { data } = await client.get<Rep>('/auth/me');
    return data;
  } catch (err) {
    throw new Error(getErrorMessage(err));
  }
}
