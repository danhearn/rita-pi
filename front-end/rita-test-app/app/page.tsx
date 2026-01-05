"use client";

import { useEffect, useMemo, useState } from "react";

type CommandName =
  | "unlock"
  | "lock"
  | "dispense"
  | "register_fingerprint"
  | "check_hand";

type PendingCommand = {
  command: CommandName;
  params?: Record<string, unknown> | null;
  issuedAt?: string;
};

type DeviceStatus = {
  device_id: string;
  status_type: string;
  timestamp?: string;
  data?: Record<string, unknown>;
  receivedAt?: string;
};

type DeviceHeartbeat = {
  device_id: string;
  timestamp?: string;
  ip_address?: string;
  locked?: boolean;
  fingerprint_count?: number;
  receivedAt?: string;
};

type DeviceSnapshot = {
  device_id: string;
  pendingCommand: PendingCommand | null;
  lastStatus: DeviceStatus | null;
  lastHeartbeat: DeviceHeartbeat | null;
};

const DEFAULT_DEVICE_ID = "pi-001";

async function postCommand(deviceId: string, payload: { command: CommandName; params?: Record<string, unknown> | null }) {
  const res = await fetch(`/api/devices/${deviceId}/commands`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data?.error || "Failed to send command");
  }
  return res.json();
}

export default function Home() {
  const [deviceId, setDeviceId] = useState(DEFAULT_DEVICE_ID);
  const [snapshot, setSnapshot] = useState<DeviceSnapshot | null>(null);
  const [motorId, setMotorId] = useState("1");
  const [segment, setSegment] = useState("0");
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSending, setIsSending] = useState(false);

  const latestStatusLabel = useMemo(() => {
    if (!snapshot?.lastStatus) return "No status yet";
    const status = snapshot.lastStatus;
    return `${status.status_type}${status.timestamp ? ` @ ${status.timestamp}` : ""}`;
  }, [snapshot]);

  useEffect(() => {
    let mounted = true;

    const load = async () => {
      try {
        const res = await fetch(`/api/devices/${deviceId}/state`);
        if (!res.ok) return;
        const data = (await res.json()) as DeviceSnapshot;
        if (mounted) setSnapshot(data);
      } catch {
        // Ignore transient fetch errors during polling
      }
    };

    load();
    const id = setInterval(load, 5000);
    return () => {
      mounted = false;
      clearInterval(id);
    };
  }, [deviceId]);

  const handleSend = async (command: CommandName, params?: Record<string, unknown> | null) => {
    setError(null);
    setMessage(null);
    setIsSending(true);
    try {
      await postCommand(deviceId, { command, params: params ?? null });
      setMessage(`Command sent: ${command}`);
      // Refresh snapshot to show new pending command
      const res = await fetch(`/api/devices/${deviceId}/state`);
      if (res.ok) {
        const data = (await res.json()) as DeviceSnapshot;
        setSnapshot(data);
      }
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setIsSending(false);
    }
  };

  const handleDispense = async () => {
    const motorNum = Number(motorId);
    const segmentNum = Number(segment);
    await handleSend("dispense", { motor_id: motorNum, segment: segmentNum });
  };

  const formatJson = (value: unknown) => JSON.stringify(value, null, 2);

  const formatTime = (value?: string) => {
    if (!value) return "-";
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return value;
    return date.toLocaleString();
  };

  return (
    <div className="min-h-screen bg-zinc-50 text-zinc-900">
      <div className="mx-auto flex max-w-5xl flex-col gap-8 px-6 py-10">
        <header className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-wide text-blue-600">Rita Pi</p>
            <h1 className="text-3xl font-bold">Rita Test Environment</h1>
            <p className="text-sm text-zinc-600">For controlling and debugging Rita devices</p>
          </div>
          <div className="flex items-center gap-2">
            <label className="text-sm text-zinc-700" htmlFor="deviceId">
              Device ID
            </label>
            <input
              id="deviceId"
              value={deviceId}
              onChange={(e) => setDeviceId(e.target.value.trim())}
              className="h-9 rounded-md border border-zinc-300 px-3 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>
        </header>

        {message && (
          <div className="rounded-md border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-800">
            {message}
          </div>
        )}
        {error && (
          <div className="rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
          <section className="rounded-xl border border-zinc-200 bg-white p-5 shadow-sm">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-lg font-semibold">Commands</h2>
              {isSending && <span className="text-xs text-zinc-500">Sending…</span>}
            </div>
            <div className="flex flex-wrap gap-3">
              <button
                onClick={() => handleSend("unlock")}
                className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 disabled:opacity-50"
                disabled={isSending}
              >
                Unlock
              </button>
              <button
                onClick={() => handleSend("lock")}
                className="rounded-md bg-zinc-800 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-zinc-900 disabled:opacity-50"
                disabled={isSending}
              >
                Lock
              </button>
              <button
                onClick={() => handleSend("register_fingerprint")}
                className="rounded-md bg-amber-500 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-amber-600 disabled:opacity-50"
                disabled={isSending}
              >
                Register Fingerprint
              </button>
              <button
                onClick={() => handleSend("check_hand")}
                className="rounded-md border border-zinc-300 px-4 py-2 text-sm font-medium text-zinc-800 shadow-sm hover:border-zinc-400 disabled:opacity-50"
                disabled={isSending}
              >
                Check Hand
              </button>
            </div>

            <div className="mt-6 rounded-lg border border-dashed border-zinc-200 p-4">
              <h3 className="mb-3 text-sm font-semibold text-zinc-700">Dispense</h3>
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
                <label className="flex items-center gap-2 text-sm text-zinc-700">
                  Motor ID
                  <input
                    type="number"
                    min={0}
                    value={motorId}
                    onChange={(e) => setMotorId(e.target.value)}
                    className="h-9 w-24 rounded-md border border-zinc-300 px-3 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                  />
                </label>
                <label className="flex items-center gap-2 text-sm text-zinc-700">
                  Segment
                  <input
                    type="number"
                    min={0}
                    value={segment}
                    onChange={(e) => setSegment(e.target.value)}
                    className="h-9 w-24 rounded-md border border-zinc-300 px-3 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                  />
                </label>
                <button
                  onClick={handleDispense}
                  className="rounded-md bg-emerald-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-emerald-700 disabled:opacity-50"
                  disabled={isSending}
                >
                  Dispense
                </button>
              </div>
            </div>
          </section>

          <section className="rounded-xl border border-zinc-200 bg-white p-5 shadow-sm">
            <h2 className="mb-4 text-lg font-semibold">Device State</h2>
            <div className="space-y-3 text-sm text-zinc-800">
              <div className="flex items-center justify-between rounded-lg bg-zinc-50 px-3 py-2">
                <span className="text-zinc-600">Pending command</span>
                <span className="font-medium">
                  {snapshot?.pendingCommand?.command ?? "None"}
                </span>
              </div>
              <div className="flex items-center justify-between rounded-lg bg-zinc-50 px-3 py-2">
                <span className="text-zinc-600">Last status</span>
                <span className="font-medium">{latestStatusLabel}</span>
              </div>
              <div className="rounded-lg bg-zinc-50 px-3 py-2">
                <div className="flex items-center justify-between">
                  <span className="text-zinc-600">Heartbeat</span>
                  <span className="font-medium">
                    {snapshot?.lastHeartbeat?.timestamp
                      ? formatTime(snapshot.lastHeartbeat.timestamp)
                      : "No heartbeat"}
                  </span>
                </div>
                {snapshot?.lastHeartbeat?.ip_address && (
                  <p className="text-xs text-zinc-600">IP: {snapshot.lastHeartbeat.ip_address}</p>
                )}
                {typeof snapshot?.lastHeartbeat?.fingerprint_count === "number" && (
                  <p className="text-xs text-zinc-600">
                    Fingerprints: {snapshot.lastHeartbeat.fingerprint_count}
                  </p>
                )}
                {typeof snapshot?.lastHeartbeat?.locked === "boolean" && (
                  <p className="text-xs text-zinc-600">
                    Locked: {snapshot.lastHeartbeat.locked ? "yes" : "no"}
                  </p>
                )}
              </div>
            </div>
          </section>
        </div>

        <section className="rounded-xl border border-zinc-200 bg-white p-5 shadow-sm">
          <h2 className="mb-3 text-lg font-semibold">Raw Data</h2>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
            <div>
              <p className="mb-2 text-sm font-medium">Pending Command</p>
              <pre className="h-44 overflow-auto rounded-lg bg-zinc-50 p-3 text-xs text-zinc-800">
{formatJson(snapshot?.pendingCommand ?? {})}
              </pre>
            </div>
            <div>
              <p className="mb-2 text-sm font-medium">Last Status</p>
              <pre className="h-44 overflow-auto rounded-lg bg-zinc-50 p-3 text-xs text-zinc-800">
{formatJson(snapshot?.lastStatus ?? {})}
              </pre>
            </div>
            <div>
              <p className="mb-2 text-sm font-medium">Last Heartbeat</p>
              <pre className="h-44 overflow-auto rounded-lg bg-zinc-50 p-3 text-xs text-zinc-800">
{formatJson(snapshot?.lastHeartbeat ?? {})}
              </pre>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
