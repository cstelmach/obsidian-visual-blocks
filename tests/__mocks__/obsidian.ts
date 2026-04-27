/* Minimal jest mock for the `obsidian` runtime API.
 * The hash port is pure (no Obsidian deps), but main.ts imports `Plugin` etc.
 * Add stubs as tests grow. */

export class Plugin {
  app: unknown;
  manifest: unknown;
  registerMarkdownCodeBlockProcessor(_lang: string, _fn: unknown): void {}
  addCommand(_cmd: unknown): void {}
  addStatusBarItem(): HTMLElement {
    return {} as HTMLElement;
  }
  registerEvent(_e: unknown): void {}
}

export class Notice {
  constructor(_msg: string, _timeout?: number) {}
}

export interface MarkdownPostProcessorContext {
  sourcePath: string;
  getSectionInfo(el: HTMLElement): { lineStart: number; lineEnd: number; text: string } | null;
}

export const Platform = {
  isMobile: false,
  isDesktop: true,
};

export const TFile = class {};
