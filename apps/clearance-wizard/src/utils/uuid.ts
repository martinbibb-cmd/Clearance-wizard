/**
 * Simple UUID generator for pack and capture IDs
 */

/**
 * Generate a UUID v4
 * @returns UUID string in format xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx
 */
export function generateUUID(): string {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

/**
 * Generate a pack ID
 * @returns Pack ID in format pack-{uuid}
 */
export function generatePackId(): string {
  return `pack-${generateUUID()}`;
}

/**
 * Generate a capture ID
 * @returns Capture ID in format capture-{uuid}
 */
export function generateCaptureId(): string {
  return `capture-${generateUUID()}`;
}

/**
 * Validate UUID format
 * @param uuid UUID string to validate
 * @returns true if valid UUID format
 */
export function isValidUUID(uuid: string): boolean {
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
  return uuidRegex.test(uuid);
}
