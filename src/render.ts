/**
 * obsidian-render-cache — Phase 9 subprocess wrapper.
 *
 * The Phase 9 commands (refresh-block, refresh-note, refresh-vault, sweep,
 * triggerOnSave) need to invoke `python3 render_cache.py …` from the
 * Obsidian Electron renderer. Two cross-platform challenges this module
 * solves:
 *
 *   1. macOS PATH inheritance. Electron renderer processes do NOT inherit
 *      the user's interactive shell PATH (well-known platform issue). A
 *      command like `python3` may resolve to /usr/bin/python3 (no rdkit)
 *      or fail entirely. We default to spawning through `$SHELL -lc` which
 *      forces the login shell to source ~/.zshrc / ~/.bashrc and inherit
 *      brew/conda init lines. User can override `pythonPath` to an absolute
 *      path AND/OR disable `useLoginShell` if their setup doesn't need it.
 *
 *   2. cwd. render_cache.py expects to run with cwd at the vault root so
 *      it can resolve markdown paths relative to the vault. We pass
 *      `app.vault.adapter.getBasePath()` (FileSystemAdapter) — works on
 *      desktop (the only platform that spawns; mobile auto-overrides to
 *      cache-only and never calls this module).
 *
 * The argv builder (`buildSpawnArgs`) is pure and unit-tested. The actual
 * spawn (`spawnRender`) is smoke-tested at the user gate.
 *
 * Streaming: spawnRender accepts an optional `onLine` callback that is
 * invoked once per line of stdout AND stderr. The refresh-vault command
 * uses this to surface real-time progress in a Notice.
 */
import { Notice } from "obsidian";
import type { RenderCacheSettings } from "./settings";

export interface SpawnArgs {
  command: string;
  args: string[];
}

/** Single-quote shell escape. Wraps the value in single quotes and escapes
 *  embedded single-quotes via `'\''` (the canonical POSIX trick). */
export function shellEscape(value: string): string {
  return "'" + value.replace(/'/g, "'\\''") + "'";
}

/** Build the spawn argv for `python3 <scriptPath> [args...]`.
 *
 * If `useLoginShell` is true, wraps the command into `<shell> -lc '<cmd>'`
 * so the user's PATH is inherited. The shell is chosen via `process.env.SHELL`
 * with /bin/zsh fallback (macOS default since Catalina).
 *
 * If `useLoginShell` is false, returns the direct argv `[pythonPath,
 * scriptPath, ...args]`. Useful when the user has set `pythonPath` to an
 * absolute path and doesn't need shell PATH inheritance.
 */
export function buildSpawnArgs(
  settings: RenderCacheSettings,
  scriptArgs: string[],
  shellEnv?: string,
): SpawnArgs {
  const direct = [settings.pythonPath, settings.scriptPath, ...scriptArgs];

  if (!settings.useLoginShell) {
    return { command: direct[0], args: direct.slice(1) };
  }

  const shell = shellEnv || process.env.SHELL || "/bin/zsh";
  // Build the shell command: pythonPath scriptPath args...
  const cmdLine = direct.map(shellEscape).join(" ");
  return { command: shell, args: ["-lc", cmdLine] };
}

/** Spawn the render command. Resolves with stdout text + exit code; rejects
 *  on spawn-level failure (ENOENT, etc.). Streams lines via onLine if given. */
export interface SpawnResult {
  exitCode: number;
  stdout: string;
  stderr: string;
}

export async function spawnRender(
  settings: RenderCacheSettings,
  scriptArgs: string[],
  cwd: string,
  onLine?: (line: string, source: "stdout" | "stderr") => void,
): Promise<SpawnResult> {
  // Lazy require to keep the module importable in test contexts where
  // child_process is fine (it ships with Node) but the import surface is
  // smaller.
  // eslint-disable-next-line @typescript-eslint/no-var-requires
  const child_process = require("child_process") as typeof import("child_process");

  const { command, args } = buildSpawnArgs(settings, scriptArgs);

  return new Promise((resolve, reject) => {
    const child = child_process.spawn(command, args, {
      cwd,
      env: { ...process.env },
      stdio: ["ignore", "pipe", "pipe"],
    });

    let stdoutAcc = "";
    let stderrAcc = "";
    let stdoutBuf = "";
    let stderrBuf = "";

    const flushBuf = (
      buf: string,
      acc: string,
      source: "stdout" | "stderr",
      isFinal: boolean,
    ): { buf: string; acc: string } => {
      const combined = buf + acc;
      const idx = combined.lastIndexOf("\n");
      if (idx === -1 && !isFinal) return { buf, acc: "" };
      const completeLines = isFinal ? combined : combined.slice(0, idx);
      const remaining = isFinal ? "" : combined.slice(idx + 1);
      if (onLine) {
        for (const line of completeLines.split("\n")) {
          if (line.length > 0) onLine(line, source);
        }
      }
      return { buf: remaining, acc: "" };
    };

    child.stdout?.on("data", (chunk: Buffer) => {
      const text = chunk.toString("utf8");
      stdoutAcc += text;
      const r = flushBuf(stdoutBuf, text, "stdout", false);
      stdoutBuf = r.buf;
    });

    child.stderr?.on("data", (chunk: Buffer) => {
      const text = chunk.toString("utf8");
      stderrAcc += text;
      const r = flushBuf(stderrBuf, text, "stderr", false);
      stderrBuf = r.buf;
    });

    child.on("error", (err) => {
      reject(err);
    });

    child.on("close", (exitCode) => {
      // Flush any final partial line.
      flushBuf(stdoutBuf, "", "stdout", true);
      flushBuf(stderrBuf, "", "stderr", true);
      resolve({
        exitCode: exitCode ?? -1,
        stdout: stdoutAcc,
        stderr: stderrAcc,
      });
    });
  });
}

/** Convenience: spawn and surface a Notice on failure. Returns success=true
 *  on exit code 0. */
export async function spawnRenderWithNotice(
  settings: RenderCacheSettings,
  scriptArgs: string[],
  cwd: string,
  successMessage?: string,
  onLine?: (line: string, source: "stdout" | "stderr") => void,
): Promise<boolean> {
  try {
    const result = await spawnRender(settings, scriptArgs, cwd, onLine);
    if (result.exitCode === 0) {
      if (successMessage) new Notice(successMessage, 4000);
      return true;
    }
    new Notice(
      `render_cache.py exited ${result.exitCode}.\n` +
        (result.stderr.trim().slice(0, 600) ||
          result.stdout.trim().slice(0, 600) ||
          "(no diagnostic output)"),
      8000,
    );
    return false;
  } catch (err) {
    new Notice(
      `Failed to spawn python: ${String(err)}.\n` +
        "Check the 'Python path' and 'Spawn through login shell' settings.",
      8000,
    );
    return false;
  }
}
