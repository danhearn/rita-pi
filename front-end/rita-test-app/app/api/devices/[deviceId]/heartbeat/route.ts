import { NextRequest, NextResponse } from "next/server";
import { setHeartbeat } from "../../store";

export async function POST(
  req: NextRequest,
  { params }: { params: Promise<{ deviceId: string }> },
) {
  const { deviceId } = await params;

  let body: {
    timestamp?: string;
    ip_address?: string;
    locked?: boolean;
    fingerprint_count?: number;
  } = {};

  try {
    body = (await req.json()) as typeof body;
  } catch {
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400 });
  }

  setHeartbeat(deviceId, {
    timestamp: body.timestamp,
    ip_address: body.ip_address,
    locked: body.locked,
    fingerprint_count: body.fingerprint_count,
  });

  return NextResponse.json({ ok: true });
}
