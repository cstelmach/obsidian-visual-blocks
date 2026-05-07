/**
 * Pure-function tests for src/render.ts argv builder + shell escape.
 * The actual subprocess spawn is smoke-tested at the user gate (it depends
 * on macOS PATH + Python install state).
 */
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import { buildSpawnArgs, buildSpawnEnv, shellEscape } from "../src/render";
import { DEFAULT_SETTINGS } from "../src/settings";

describe("shellEscape", () => {
  it("wraps a plain string in single quotes", () => {
    expect(shellEscape("hello")).toBe("'hello'");
  });

  it("escapes embedded single quotes via canonical POSIX trick", () => {
    expect(shellEscape("can't")).toBe("'can'\\''t'");
  });

  it("preserves spaces", () => {
    expect(shellEscape("a b c")).toBe("'a b c'");
  });

  it("preserves filesystem-unsafe characters intact inside quotes", () => {
    expect(shellEscape("$(rm -rf /)")).toBe("'$(rm -rf /)'");
    expect(shellEscape("`whoami`")).toBe("'`whoami`'");
    expect(shellEscape("&&&")).toBe("'&&&'");
  });

  it("handles empty string", () => {
    expect(shellEscape("")).toBe("''");
  });
});

describe("buildSpawnArgs (direct mode)", () => {
  const settings = { ...DEFAULT_SETTINGS, useLoginShell: false };

  it("returns [pythonPath, scriptPath, ...args]", () => {
    const r = buildSpawnArgs(settings, ["--all", "--force"]);
    expect(r.command).toBe("python3");
    expect(r.args).toEqual([
      "resources/scripts/python_single/render_cache.py",
      "--all",
      "--force",
    ]);
  });

  it("respects custom pythonPath (e.g., conda env)", () => {
    const conda = { ...settings, pythonPath: "/opt/miniconda/bin/python3" };
    const r = buildSpawnArgs(conda, ["FILE.md"]);
    expect(r.command).toBe("/opt/miniconda/bin/python3");
    expect(r.args).toEqual([
      "resources/scripts/python_single/render_cache.py",
      "FILE.md",
    ]);
  });
});

describe("buildSpawnArgs (login shell mode)", () => {
  const settings = { ...DEFAULT_SETTINGS, useLoginShell: true };

  it("wraps in $SHELL -lc with shell-escaped command line", () => {
    const r = buildSpawnArgs(settings, ["--sweep"], "/bin/zsh");
    expect(r.command).toBe("/bin/zsh");
    expect(r.args).toEqual([
      "-lc",
      "'python3' 'resources/scripts/python_single/render_cache.py' '--sweep'",
    ]);
  });

  it("falls back to /bin/zsh when shellEnv is missing and SHELL env is unset", () => {
    const orig = process.env.SHELL;
    delete process.env.SHELL;
    try {
      const r = buildSpawnArgs(settings, ["--all"]);
      expect(r.command).toBe("/bin/zsh");
    } finally {
      if (orig !== undefined) process.env.SHELL = orig;
    }
  });

  it("escapes paths with spaces correctly", () => {
    const sp = {
      ...settings,
      pythonPath: "python3",
      scriptPath: "scripts/render cache.py",
    };
    const r = buildSpawnArgs(sp, ["a file with spaces.md"], "/bin/zsh");
    expect(r.args[1]).toBe(
      "'python3' 'scripts/render cache.py' 'a file with spaces.md'",
    );
  });

  it("escapes paths with single quotes correctly", () => {
    const r = buildSpawnArgs(settings, ["it's-a-file.md"], "/bin/zsh");
    expect(r.args[1]).toContain("'it'\\''s-a-file.md'");
  });
});

describe("buildSpawnEnv", () => {
  it("passes the configured cache root to Python", () => {
    const env = buildSpawnEnv(
      {
        ...DEFAULT_SETTINGS,
        cacheRootPath: "resources/data/cache/custom-visual-blocks",
      },
      { PATH: "/usr/bin" },
    );
    expect(env.VISUAL_BLOCKS_CACHE_ROOT).toBe(
      "resources/data/cache/custom-visual-blocks",
    );
    expect(env.PATH).toBe("/usr/bin");
  });
});

describe("styles.css native cache-embed suppression", () => {
  const styles = readFileSync(resolve(process.cwd(), "styles.css"), "utf8");

  it("hides Obsidian native wrappers for plugin-owned cache wikilinks", () => {
    expect(styles).toContain(
      '.internal-embed[src*="resources/data/cache/visual-blocks/"]',
    );
    expect(styles).toContain(
      '.image-embed[src*="resources/data/cache/visual-blocks/"]',
    );
    expect(styles).toContain(
      '.markdown-embed[src*="resources/data/cache/visual-blocks/"]',
    );
    expect(styles).toContain(
      '.internal-embed[src*=".obsidian/plugins/visual-blocks/cache/"]',
    );
    expect(styles).toContain(
      '.image-embed[src*=".obsidian/plugins/visual-blocks/cache/"]',
    );
    expect(styles).toContain(
      '.markdown-embed[src*=".obsidian/plugins/visual-blocks/cache/"]',
    );
  });

  it("does not hide the plugin-rendered image class", () => {
    expect(styles).toContain(".visual-blocks-block img");
    expect(styles).toContain(
      'img[alt~="visual-blocks"]:not(.visual-blocks-img)',
    );
    expect(styles).not.toContain(".visual-blocks-img {\n    display: none");
  });
});
