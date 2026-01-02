import { NextRequest, NextResponse } from "next/server";
import { setStatus } from "../../store";

export async function POST(
  req: NextRequest,
  { params }: { params: Promise<{ deviceId: string }> },
) {
  const { deviceId } = await params;

  let body: {
    status_type?: string;
    timestamp?: string;
    data?: Record<string, unknown>;
  } = {};

  try {
    body = (await req.json()) as typeof body;
  } catch {
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400 });
  }

  if (!body.status_type) {
    return NextResponse.json({ error: "status_type is required" }, { status: 400 });
  }

  setStatus(deviceId, {
    device_id: deviceId,
    status_type: body.status_type,
    timestamp: body.timestamp,
    data: body.data ?? {},
  });

  return NextResponse.json({ ok: true });
}
