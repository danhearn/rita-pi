import { NextRequest, NextResponse } from "next/server";
import {
  CommandNames,
  CommandName,
  popPendingCommand,
  setPendingCommand,
} from "../../store";

export async function GET(
  _req: NextRequest,
  { params }: { params: Promise<{ deviceId: string }> },
) {
  const { deviceId } = await params;
  const command = popPendingCommand(deviceId);

  if (!command) {
    return NextResponse.json({ command: null });
  }

  return NextResponse.json({
    command: command.command,
    params: command.params ?? null,
  });
}

export async function POST(
  req: NextRequest,
  { params: routeParams }: { params: Promise<{ deviceId: string }> },
) {
  const { deviceId } = await routeParams;

  let body: { command?: string; params?: Record<string, unknown> } = {};
  try {
    body = (await req.json()) as typeof body;
  } catch {
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400 });
  }

  const { command, params: cmdParams } = body;

  if (!command || !CommandNames.includes(command as CommandName)) {
    return NextResponse.json({ error: "Invalid or missing command" }, { status: 400 });
  }

  try {
    setPendingCommand(deviceId, command as CommandName, cmdParams ?? null);
  } catch (error) {
    return NextResponse.json({ error: (error as Error).message }, { status: 400 });
  }

  return NextResponse.json({ ok: true, command, params: cmdParams ?? null });
}
