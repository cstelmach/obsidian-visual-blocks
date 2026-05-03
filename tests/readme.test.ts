import { readFileSync } from "node:fs";
import { resolve } from "node:path";

describe("README language-toggle documentation", () => {
  const readme = readFileSync(resolve(process.cwd(), "README.md"), "utf8");

  it("documents visualization-library toggles", () => {
    expect(readme).toContain("Visualization libraries");
    expect(readme).toContain("TikZ, Graphviz, D2, LilyPond, and SMILES");
  });

  it("documents cache retention for disabled libraries", () => {
    expect(readme).toContain("does **not** delete existing cache files");
  });

  it("documents the optional CLI --languages filter", () => {
    expect(readme).toContain("--languages tikz,d2,smiles");
    expect(readme).toContain("direct terminal commands process all supported languages");
  });

  it("documents the disabled-library troubleshooting path", () => {
    expect(readme).toContain("A block says the library is disabled");
  });
});
