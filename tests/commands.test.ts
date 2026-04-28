/**
 * Pure-function tests for the cursor-block scanner used by refresh-block.
 * The actual command handlers (refreshBlock, refreshVault, etc.) are
 * smoke-tested at the user gate — they wire to Obsidian APIs that mock
 * poorly.
 */
import { findBlockAtCursorLine } from "../src/commands";

describe("findBlockAtCursorLine", () => {
  const sample = [
    "# Title",
    "",
    "Intro text.",
    "",
    "```tikz",
    "\\begin{tikzpicture}",
    "\\draw (0,0) -- (1,1);",
    "\\end{tikzpicture}",
    "```",
    "",
    "Middle text.",
    "",
    "```d2",
    "a -> b",
    "```",
    "",
    "More text.",
    "",
    "```graphviz",
    "digraph G { a -> b; }",
    "```",
    "",
    "End.",
  ].join("\n");

  it("returns null when cursor is outside any code block", () => {
    expect(findBlockAtCursorLine(sample, 0)).toBeNull(); // title line
    expect(findBlockAtCursorLine(sample, 2)).toBeNull(); // intro
    expect(findBlockAtCursorLine(sample, 10)).toBeNull(); // middle
    expect(findBlockAtCursorLine(sample, 22)).toBeNull(); // out-of-range
  });

  it("returns blockIdx 0 for cursor inside the first (tikz) block", () => {
    const r = findBlockAtCursorLine(sample, 6);
    expect(r).not.toBeNull();
    expect(r!.blockIdx).toBe(0);
    expect(r!.language).toBe("tikz");
    expect(r!.lineStart).toBe(4);
    expect(r!.lineEnd).toBe(8);
  });

  it("returns blockIdx 1 for cursor inside the second (d2) block", () => {
    const r = findBlockAtCursorLine(sample, 13);
    expect(r).not.toBeNull();
    expect(r!.blockIdx).toBe(1);
    expect(r!.language).toBe("d2");
  });

  it("returns blockIdx 2 for cursor inside the third (graphviz) block", () => {
    const r = findBlockAtCursorLine(sample, 19);
    expect(r).not.toBeNull();
    expect(r!.blockIdx).toBe(2);
    expect(r!.language).toBe("graphviz");
  });

  it("matches cursor on the opening fence line", () => {
    const r = findBlockAtCursorLine(sample, 4); // ```tikz line
    expect(r).not.toBeNull();
    expect(r!.blockIdx).toBe(0);
  });

  it("matches cursor on the closing fence line", () => {
    const r = findBlockAtCursorLine(sample, 8); // ``` (closing)
    expect(r).not.toBeNull();
    expect(r!.blockIdx).toBe(0);
  });

  it("ignores unsupported languages (e.g., python)", () => {
    const src = "```python\nprint(1)\n```";
    expect(findBlockAtCursorLine(src, 1)).toBeNull();
  });

  it("treats tikz-paused as tikz (D2.3)", () => {
    const src = [
      "```tikz-paused",
      "\\draw (0,0) circle (1);",
      "```",
    ].join("\n");
    const r = findBlockAtCursorLine(src, 1);
    expect(r).not.toBeNull();
    expect(r!.language).toBe("tikz");
    expect(r!.blockIdx).toBe(0);
  });

  it("recognizes lilypond and smiles", () => {
    const src = [
      "```lilypond",
      "{ c'4 }",
      "```",
      "",
      "```smiles",
      "CCO",
      "```",
    ].join("\n");
    expect(findBlockAtCursorLine(src, 1)!.language).toBe("lilypond");
    expect(findBlockAtCursorLine(src, 1)!.blockIdx).toBe(0);
    expect(findBlockAtCursorLine(src, 5)!.language).toBe("smiles");
    expect(findBlockAtCursorLine(src, 5)!.blockIdx).toBe(1);
  });

  it("blockIdx counts only supported languages, skipping unsupported ones", () => {
    const src = [
      "```python",       // 0  unsupported, NOT counted
      "x = 1",            // 1
      "```",              // 2
      "",                 // 3
      "```tikz",          // 4  blockIdx 0
      "\\draw;",          // 5
      "```",              // 6
      "",                 // 7
      "```d2",            // 8  blockIdx 1
      "a -> b",           // 9
      "```",              // 10
    ].join("\n");
    expect(findBlockAtCursorLine(src, 5)!.blockIdx).toBe(0);
    expect(findBlockAtCursorLine(src, 9)!.blockIdx).toBe(1);
  });
});
