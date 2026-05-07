import {
  shouldRunStartupAutoRefresh,
  startupAutoRefreshArgs,
  startupAutoRefreshDelayMs,
} from "../src/startup";
import { DEFAULT_SETTINGS } from "../src/settings";

describe("startup auto-refresh policy", () => {
  it("does not run by default because the feature is opt-in", () => {
    expect(
      shouldRunStartupAutoRefresh(DEFAULT_SETTINGS, false, Date.now()).shouldRun,
    ).toBe(false);
  });

  it("runs on desktop when enabled and no prior startup refresh is recorded", () => {
    const decision = shouldRunStartupAutoRefresh(
      { ...DEFAULT_SETTINGS, autoRefreshOnStartup: true },
      false,
      1_000_000,
    );
    expect(decision).toEqual({ shouldRun: true, reason: "due" });
  });

  it("never runs on mobile even when enabled", () => {
    const decision = shouldRunStartupAutoRefresh(
      { ...DEFAULT_SETTINGS, autoRefreshOnStartup: true },
      true,
      1_000_000,
    );
    expect(decision.shouldRun).toBe(false);
    expect(decision.reason).toBe("mobile");
  });

  it("skips runs inside the configured cooldown window", () => {
    const settings = {
      ...DEFAULT_SETTINGS,
      autoRefreshOnStartup: true,
      startupRefreshMinIntervalHours: 6,
      startupRefreshLastRunAt: 1_000_000,
    };
    const fiveHoursLater = 1_000_000 + 5 * 60 * 60 * 1000;
    expect(
      shouldRunStartupAutoRefresh(settings, false, fiveHoursLater),
    ).toEqual({ shouldRun: false, reason: "cooldown" });
  });

  it("runs after the configured cooldown window has elapsed", () => {
    const settings = {
      ...DEFAULT_SETTINGS,
      autoRefreshOnStartup: true,
      startupRefreshMinIntervalHours: 6,
      startupRefreshLastRunAt: 1_000_000,
    };
    const sevenHoursLater = 1_000_000 + 7 * 60 * 60 * 1000;
    expect(
      shouldRunStartupAutoRefresh(settings, false, sevenHoursLater),
    ).toEqual({ shouldRun: true, reason: "due" });
  });

  it("builds a changed-only vault render command, not a forced rerender", () => {
    expect(startupAutoRefreshArgs(DEFAULT_SETTINGS)).toEqual([
      "--all",
      "--languages",
      "tikz,graphviz,d2,lilypond,smiles",
    ]);
    expect(startupAutoRefreshArgs(DEFAULT_SETTINGS)).not.toContain("--force");
  });

  it("uses the configured startup delay in milliseconds", () => {
    expect(
      startupAutoRefreshDelayMs({
        ...DEFAULT_SETTINGS,
        startupRefreshDelaySeconds: 300,
      }),
    ).toBe(300_000);
  });
});
