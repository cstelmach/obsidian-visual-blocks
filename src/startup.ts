import { buildLanguageFilterArgs } from "./languages";
import type { RenderCacheSettings } from "./settings";

export type StartupAutoRefreshReason =
  | "disabled"
  | "mobile"
  | "cooldown"
  | "due";

export interface StartupAutoRefreshDecision {
  shouldRun: boolean;
  reason: StartupAutoRefreshReason;
}

export function startupAutoRefreshDelayMs(
  settings: RenderCacheSettings,
): number {
  return Math.max(0, settings.startupRefreshDelaySeconds) * 1000;
}

export function startupAutoRefreshCooldownMs(
  settings: RenderCacheSettings,
): number {
  return Math.max(0, settings.startupRefreshMinIntervalHours) * 60 * 60 * 1000;
}

export function shouldRunStartupAutoRefresh(
  settings: RenderCacheSettings,
  isMobile: boolean,
  nowMs: number,
): StartupAutoRefreshDecision {
  if (isMobile) return { shouldRun: false, reason: "mobile" };
  if (!settings.autoRefreshOnStartup) {
    return { shouldRun: false, reason: "disabled" };
  }

  const lastRun = settings.startupRefreshLastRunAt;
  if (lastRun !== null) {
    const elapsed = nowMs - lastRun;
    if (elapsed >= 0 && elapsed < startupAutoRefreshCooldownMs(settings)) {
      return { shouldRun: false, reason: "cooldown" };
    }
  }

  return { shouldRun: true, reason: "due" };
}

export function startupAutoRefreshArgs(
  settings: RenderCacheSettings,
): string[] | null {
  const languageArgs = buildLanguageFilterArgs(settings.enabledLanguages);
  if (!languageArgs) return null;
  return ["--all", ...languageArgs];
}
