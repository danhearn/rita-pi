import { NextResponse } from "next/server";
import { getSnapshot } from "../../store";

export async function GET(
  _req: Request,
  { params }: { params: Promise<{ deviceId: string }> },
) {
  const { deviceId } = await params;
  const state = getSnapshot(deviceId);
  return NextResponse.json({
    device_id: deviceId,
    pendingCommand: state.pendingCommand,
    lastStatus: state.lastStatus,
    lastHeartbeat: state.lastHeartbeat,
  });
}
