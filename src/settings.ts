/**
 * obsidian-render-cache — Phase 9 settings + types.
 *
 * Settings are intentionally narrow:
 *   • mode            — view-time behaviour (hybrid / cache-only / live)
 *   • pythonPath      — default "python3"; override with absolute path when
 *                       Python lives in a conda env (Electron renderer does
 *                       NOT inherit the user's shell PATH on macOS)
 *   • scriptPath      — vault-relative path to render_cache.py
 *   • triggerOnSave   — desktop only; re-render on file modify
 *   • useLoginShell   — macOS only; spawn through `$SHELL -lc` to inherit
 *                       the user's PATH (homebrew, conda init, etc.)
 *
 * Mode cycle:
 *   hybrid → cache-only → live → hybrid
 *
 * Mobile auto-overrides effective mode to `cache-only` regardless of the
 * stored setting (SPEC §3.6 / AC9.9 / D03 — iOS sandbox cannot spawn).
 *
 * The Settings UI is smoke-tested at the user gate; the pure helpers below
 * (nextMode, effectiveMode, missMessage, isPlaceholderClickable) are
 * unit-tested directly.
 */
import { App, PluginSettingTab, Setting } from "obsidian";
import type RenderCachePlugin from "./main";

export type RenderMode = "hybrid" | "cache-only" | "live";

export interface RenderCacheSettings {
  mode: RenderMode;
  pythonPath: string;
  scriptPath: string;
  triggerOnSave: boolean;
  useLoginShell: boolean;
}

export const DEFAULT_SETTINGS: RenderCacheSettings = {
  mode: "hybrid",
  pythonPath: "python3",
  scriptPath: "resources/scripts/python_single/render_cache.py",
  triggerOnSave: true,
  useLoginShell: true,
};

export const MODE_CYCLE: readonly RenderMode[] = [
  "hybrid",
  "cache-only",
  "live",
] as const;

export function nextMode(mode: RenderMode): RenderMode {
  const i = MODE_CYCLE.indexOf(mode);
  if (i === -1) return "hybrid";
  return MODE_CYCLE[(i + 1) % MODE_CYCLE.length];
}

/** Mobile is always `cache-only` regardless of setting (D03 / AC9.9). */
export function effectiveMode(
  settings: RenderCacheSettings,
  isMobile: boolean,
): RenderMode {
  if (isMobile) return "cache-only";
  return settings.mode;
}

/** Cache-miss placeholder text. Mobile-aware via `isMobile`; cache-only text
 *  is shared across desktop+mobile (it's intrinsic to the mode, not the
 *  platform). */
export function missMessage(
  effective: RenderMode,
  lang: string,
  isMobile: boolean,
): string {
  if (isMobile) {
    return `${lang}: Cache miss — open on desktop to render.`;
  }
  if (effective === "cache-only") {
    return `${lang}: Cache miss — cache-only mode; switch to hybrid or live to render.`;
  }
  // hybrid or live, on desktop
  return `${lang}: Cache miss — click to render.`;
}

/** Whether the placeholder is clickable (desktop + a mode that can render). */
export function isPlaceholderClickable(
  effective: RenderMode,
  isMobile: boolean,
): boolean {
  if (isMobile) return false;
  return effective === "hybrid" || effective === "live";
}

export class RenderCacheSettingTab extends PluginSettingTab {
  private readonly plugin: RenderCachePlugin;

  constructor(app: App, plugin: RenderCachePlugin) {
    super(app, plugin);
    this.plugin = plugin;
  }

  display(): void {
    const { containerEl } = this;
    containerEl.empty();
    containerEl.createEl("h2", { text: "Render Cache settings" });

    new Setting(containerEl)
      .setName("Render mode")
      .setDesc(
        "hybrid: show cached SVG, placeholder on miss (clickable). " +
          "cache-only: never invoke Python. " +
          "live: re-render every block on every load (desktop). " +
          "Mobile is always cache-only.",
      )
      .addDropdown((d) =>
        d
          .addOption("hybrid", "hybrid (recommended)")
          .addOption("cache-only", "cache-only")
          .addOption("live", "live (desktop only)")
          .setValue(this.plugin.settings.mode)
          .onChange(async (value) => {
            this.plugin.settings.mode = value as RenderMode;
            await this.plugin.saveSettings();
          }),
      );

    new Setting(containerEl)
      .setName("Python path")
      .setDesc(
        "Absolute path to the python3 used to invoke render_cache.py. " +
          "Default: python3 (resolved via login shell). Override if Python " +
          "is in a conda env (e.g., /opt/homebrew/Caskroom/miniconda/base/bin/python3).",
      )
      .addText((t) =>
        t
          .setPlaceholder("python3")
          .setValue(this.plugin.settings.pythonPath)
          .onChange(async (v) => {
            this.plugin.settings.pythonPath = v.trim() || "python3";
            await this.plugin.saveSettings();
          }),
      );

    new Setting(containerEl)
      .setName("Script path (vault-relative)")
      .setDesc(
        "Vault-relative path to render_cache.py. Default works for the " +
          "Obsidian vault layout used by this plugin's author.",
      )
      .addText((t) =>
        t
          .setPlaceholder(DEFAULT_SETTINGS.scriptPath)
          .setValue(this.plugin.settings.scriptPath)
          .onChange(async (v) => {
            this.plugin.settings.scriptPath =
              v.trim() || DEFAULT_SETTINGS.scriptPath;
            await this.plugin.saveSettings();
          }),
      );

    new Setting(containerEl)
      .setName("Re-render on save")
      .setDesc(
        "Desktop only. When a markdown file with a supported codeblock " +
          "is saved, automatically run render_cache.py on it.",
      )
      .addToggle((t) =>
        t
          .setValue(this.plugin.settings.triggerOnSave)
          .onChange(async (v) => {
            this.plugin.settings.triggerOnSave = v;
            await this.plugin.saveSettings();
          }),
      );

    new Setting(containerEl)
      .setName("Spawn through login shell ($SHELL -lc)")
      .setDesc(
        "Recommended on macOS. Electron renderer process doesn't inherit " +
          "the user's shell PATH; routing through a login shell picks up " +
          "homebrew, conda init, etc. Disable if it causes spawn failures.",
      )
      .addToggle((t) =>
        t
          .setValue(this.plugin.settings.useLoginShell)
          .onChange(async (v) => {
            this.plugin.settings.useLoginShell = v;
            await this.plugin.saveSettings();
          }),
      );
  }
}
