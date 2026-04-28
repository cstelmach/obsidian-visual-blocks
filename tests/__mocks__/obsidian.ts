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
  addSettingTab(_tab: unknown): void {}
  loadData(): Promise<unknown> {
    return Promise.resolve(undefined);
  }
  saveData(_data: unknown): Promise<void> {
    return Promise.resolve();
  }
}

export class PluginSettingTab {
  containerEl: HTMLElement;
  app: unknown;
  constructor(app: unknown, _plugin: unknown) {
    this.app = app;
    this.containerEl = {} as HTMLElement;
  }
  display(): void {}
}

export class Setting {
  constructor(_containerEl: unknown) {}
  setName(_n: string): this { return this; }
  setDesc(_d: string): this { return this; }
  addText(_cb: unknown): this { return this; }
  addToggle(_cb: unknown): this { return this; }
  addDropdown(_cb: unknown): this { return this; }
  addButton(_cb: unknown): this { return this; }
}

export class Modal {
  app: unknown;
  contentEl: HTMLElement;
  containerEl: HTMLElement;
  constructor(app: unknown) {
    this.app = app;
    this.contentEl = {} as HTMLElement;
    this.containerEl = {} as HTMLElement;
  }
  open(): void {}
  close(): void {}
  onOpen(): void {}
  onClose(): void {}
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
  isMacOS: true,
};

export class FileSystemAdapter {
  getBasePath(): string { return "/vault"; }
}

export class TFile {
  path = "";
  extension = "md";
}

export class App {}
