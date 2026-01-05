//TODO: convert to Zustand store

export const CommandNames = [
  "unlock",
  "lock",
  "dispense",
  "register_fingerprint",
  "check_hand",
] as const;

export type CommandName = (typeof CommandNames)[number];

export type PendingCommand = {
  command: CommandName;
  params?: Record<string, unknown> | null;
  issuedAt: string;
};

export type DeviceStatus = {
  device_id: string;
  status_type: string;
  timestamp?: string;
  data?: Record<string, unknown>;
  receivedAt: string;
};

export type DeviceHeartbeat = {
  device_id: string;
  timestamp?: string;
  ip_address?: string;
  locked?: boolean;
  fingerprint_count?: number;
  receivedAt: string;
};

export type DeviceState = {
  pendingCommand: PendingCommand | null;
  lastStatus: DeviceStatus | null;
  lastHeartbeat: DeviceHeartbeat | null;
};

const devices = new Map<string, DeviceState>();

function validateCommand(
  command: string,
  params?: Record<string, unknown> | null,
): asserts command is CommandName {
  if (!CommandNames.includes(command as CommandName)) {
    throw new Error(`Invalid command: ${command}`);
  }

  if (command === "dispense") {
    const motorId = params?.motor_id;
    const segment = params?.segment;
    if (typeof motorId !== "number" || !Number.isInteger(motorId) || motorId < 0) {
      throw new Error("dispense requires numeric motor_id");
    }
    if (typeof segment !== "number" || !Number.isInteger(segment) || segment < 0) {
      throw new Error("dispense requires numeric segment");
    }
  }
}

export function getDeviceState(deviceId: string): DeviceState {
  if (!devices.has(deviceId)) {
    devices.set(deviceId, {
      pendingCommand: null,
      lastStatus: null,
      lastHeartbeat: null,
    });
  }
  return devices.get(deviceId)!;
}

export function setPendingCommand(
  deviceId: string,
  command: CommandName,
  params?: Record<string, unknown> | null,
) {
  const state = getDeviceState(deviceId);
  validateCommand(command, params ?? undefined);
  state.pendingCommand = {
    command,
    params: params ?? null,
    issuedAt: new Date().toISOString(),
  };
}

export function popPendingCommand(deviceId: string): PendingCommand | null {
  const state = getDeviceState(deviceId);
  const cmd = state.pendingCommand;
  state.pendingCommand = null; // clear on read to avoid replay
  return cmd;
}

export function peekPendingCommand(deviceId: string): PendingCommand | null {
  const state = getDeviceState(deviceId);
  return state.pendingCommand;
}

export function setStatus(deviceId: string, status: Omit<DeviceStatus, "receivedAt">) {
  const state = getDeviceState(deviceId);
  state.lastStatus = {
    ...status,
    device_id: deviceId,
    receivedAt: new Date().toISOString(),
  };
}

export function setHeartbeat(
  deviceId: string,
  heartbeat: Omit<DeviceHeartbeat, "receivedAt" | "device_id">,
) {
  const state = getDeviceState(deviceId);
  state.lastHeartbeat = {
    ...heartbeat,
    device_id: deviceId,
    receivedAt: new Date().toISOString(),
  };
}

export function getSnapshot(deviceId: string): DeviceState {
  return getDeviceState(deviceId);
}
