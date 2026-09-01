/// <reference types="vite/client" />

import { createClient } from '@insforge/sdk';

const baseUrl = import.meta.env.VITE_INSFORGE_URL as string | undefined;
const anonKey = import.meta.env.VITE_INSFORGE_ANON_KEY as string | undefined;

export const insforge = baseUrl && anonKey ? createClient({ baseUrl, anonKey }) : null;

export const requireInsforge = () => {
  if (!insforge) {
    throw new Error('Authentication is not configured. Set the InsForge browser environment variables.');
  }
  return insforge;
};
