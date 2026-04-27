/**
 * obsidian-render-cache — Phase 8 plugin scaffold.
 *
 * Architecture: a viewer only. Renders happen at save time via
 * resources/scripts/python_single/render_cache.py (see SPEC §1.2 D04 —
 * Python is canonical writer, plugin reads only).
 *
 * For each registered language the plugin:
 *   1. Computes the canonical 16-char SHA-256 cache key from the block
 *      source (see hash.ts; byte-identical to Python compute_key per T12).
 *   2. Looks up the entry in attachments/cache/tikz/index.json by
 *      sourceHash (advisor: first match wins; identical-source duplicates
 *      have identical cached SVGs, so showing the same file twice is
 *      semantically correct).
 *   3. On hit + file exists: emits an <img src=getResourcePath(cachePath)>
 *      (SPEC §3.4 step 3, §3.6 step 4, T7).
 *   4. On miss: emits a platform-aware placeholder. Mobile shows
 *      "Open on desktop"; desktop shows a clickable "Cache miss" hint
 *      that opens a Notice (Phase 9 wires the actual render trigger).
 *
 * Phase 8 acceptance (SPEC §5 Phase 8 AC8.1–AC8.7):
 *   AC8.1 — plugin loads without console errors.
 *   AC8.2 — cached TikZ block displays inline in reading view.
 *   AC8.3 — uncached block shows placeholder.
 *   AC8.4 — Platform.isMobile placeholder reads "Open on desktop".
 *   AC8.5 — desktop placeholder is clickable (Phase 9 wires actual render).
 *   AC8.6 — TS hash matches Python hash (cross-language fixture test).
 *   AC8.7 — source mode untouched (codeblock processors only fire in
 *           reading view + live preview; Cmd+E shows raw markdown).
 */
import {
  MarkdownPostProcessorContext,
  Notice,
  Platform,
  Plugin,
} from "obsidian";
import { computeKey } from "./hash";

const LANGUAGES = ["tikz", "graphviz", "d2", "lilypond", "smiles"] as const;
type Lang = (typeof LANGUAGES)[number];

const INDEX_PATH = "attachments/cache/tikz/index.json";

interface BlockEntry {
  blockIdx: number;
  language: string;
  sourceHash: string;
  cachePath: string;
  outputBytes: number;
  outputFormat: string;
  renderedAt: string | null;
  rendererVersion: string;
  lastError: string | null;
}

interface IndexFile {
  schemaVersion?: number;
  rendererVersion?: string;
  preambleHashes: Record<string, string>;
  notes: Record<string, { blocks: BlockEntry[] }>;
}

export default class RenderCachePlugin extends Plugin {
  private index: IndexFile | null = null;

  async onload(): Promise<void> {
    await this.reloadIndex();

    for (const lang of LANGUAGES) {
      this.registerMarkdownCodeBlockProcessor(
        lang,
        async (source, el, ctx) => {
          try {
            await this.displayCachedBlock(source, lang, el, ctx);
          } catch (err) {
            this.renderError(el, lang, err);
          }
        },
      );
    }
    console.log(
      `obsidian-render-cache: loaded; processors registered for ${LANGUAGES.join(", ")}`,
    );
  }

  async onunload(): Promise<void> {
    console.log("obsidian-render-cache: unloaded");
  }

  /** Read attachments/cache/tikz/index.json into memory. Phase 8 calls this
   *  once at load. Phase 9 will refresh on file events. */
  async reloadIndex(): Promise<void> {
    try {
      const exists = await this.app.vault.adapter.exists(INDEX_PATH);
      if (!exists) {
        this.index = null;
        return;
      }
      const text = await this.app.vault.adapter.read(INDEX_PATH);
      this.index = JSON.parse(text) as IndexFile;
    } catch (err) {
      console.error("obsidian-render-cache: failed to load index", err);
      this.index = null;
    }
  }

  private async displayCachedBlock(
    source: string,
    lang: Lang,
    el: HTMLElement,
    ctx: MarkdownPostProcessorContext,
  ): Promise<void> {
    el.empty();
    const wrapper = el.createDiv({ cls: "render-cache-block" });

    if (!this.index) {
      this.renderPlaceholder(
        wrapper,
        lang,
        "Index not loaded. Run render_cache.py to (re)build the cache.",
        false,
      );
      return;
    }

    const preambleHash = this.index.preambleHashes[`<adapter:${lang}>`] ?? "";
    if (!preambleHash) {
      this.renderPlaceholder(
        wrapper,
        lang,
        `No preamble hash for "${lang}" in index. Run render_cache.py.`,
        false,
      );
      return;
    }

    const key = await computeKey(source, lang, {}, preambleHash);
    const entry = this.findEntry(ctx.sourcePath, key);

    if (!entry) {
      this.renderPlaceholder(wrapper, lang, this.missMessage(), Platform.isDesktop);
      return;
    }

    const fileExists = await this.app.vault.adapter.exists(entry.cachePath);
    if (!fileExists) {
      this.renderPlaceholder(
        wrapper,
        lang,
        `Cache miss: ${entry.cachePath} is in index but missing on disk.`,
        Platform.isDesktop,
      );
      return;
    }

    const src = this.app.vault.adapter.getResourcePath(entry.cachePath);
    wrapper.createEl("img", {
      cls: "render-cache-img",
      attr: {
        src,
        alt: `${lang}-cache`,
        loading: "lazy",
      },
    });
  }

  /** Find the index entry whose sourceHash matches the computed key.
   *  Iterates blocks in this note (advisor: first match wins; cachePaths
   *  for identical-source duplicates differ only by slot index, but the
   *  rendered SVG is byte-identical, so any matching cache file is correct
   *  to display).
   */
  private findEntry(sourcePath: string, key: string): BlockEntry | null {
    if (!this.index) return null;
    const note = this.index.notes[sourcePath];
    if (!note) return null;
    return note.blocks.find((b) => b.sourceHash === key) ?? null;
  }

  private missMessage(): string {
    if (Platform.isMobile) return "Cache miss — open on desktop to render.";
    return "Cache miss — click here for help (Phase 9 will wire click-to-render).";
  }

  private renderPlaceholder(
    parent: HTMLElement,
    lang: Lang,
    msg: string,
    clickable: boolean,
  ): void {
    const el = parent.createDiv({
      cls:
        "render-cache-placeholder" + (clickable ? " is-clickable" : ""),
    });
    el.createSpan({ cls: "render-cache-lang", text: lang });
    el.appendText(": " + msg);
    if (clickable) {
      el.onclick = () => {
        new Notice(
          "Phase 8 placeholder. To render, run:\n" +
            "  python3 resources/scripts/python_single/render_cache.py <FILE.md>\n" +
            "Phase 9 will add a 'Refresh this block' command.",
          6000,
        );
      };
    }
  }

  private renderError(el: HTMLElement, lang: Lang, err: unknown): void {
    el.empty();
    const div = el.createDiv({ cls: "render-cache-error" });
    div.appendText(
      `obsidian-render-cache: ${lang} block failed — ${String(err)}`,
    );
  }
}
