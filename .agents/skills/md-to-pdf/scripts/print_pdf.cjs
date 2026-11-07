const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { pathToFileURL } = require("node:url");

function existingFile(candidates) {
  return candidates.find((candidate) => candidate && fs.existsSync(candidate));
}

function findPlaywrightPackages(root, maxDepth = 7) {
  if (!root || !fs.existsSync(root)) return [];
  const found = [];
  const walk = (directory, depth) => {
    if (depth > maxDepth) return;
    let entries;
    try {
      entries = fs.readdirSync(directory, { withFileTypes: true });
    } catch {
      return;
    }
    if (
      path.basename(directory) === "playwright" &&
      fs.existsSync(path.join(directory, "package.json"))
    ) {
      found.push(directory);
      return;
    }
    for (const entry of entries) {
      if (entry.isDirectory()) {
        walk(path.join(directory, entry.name), depth + 1);
      }
    }
  };
  walk(root, 0);
  return found;
}

function loadPlaywright() {
  const candidates = [];
  if (process.env.PLAYWRIGHT_MODULE) {
    candidates.push(process.env.PLAYWRIGHT_MODULE);
  }
  candidates.push(
    path.join(process.cwd(), "node_modules", "playwright"),
    path.join(__dirname, "..", "node_modules", "playwright"),
  );
  try {
    candidates.push(
      path.dirname(
        require.resolve("playwright/package.json", {
          paths: [process.cwd(), __dirname],
        }),
      ),
    );
  } catch {
    // Playwright is not in the normal Node resolution path.
  }

  const localAppData =
    process.env.LOCALAPPDATA || path.join(os.homedir(), "AppData", "Local");
  candidates.push(
    ...findPlaywrightPackages(
      path.join(localAppData, "pnpm", "store", "v11", "links", "@", "playwright"),
    ),
    ...findPlaywrightPackages(
      path.join(localAppData, "pnpm", "store", "v10", "links", "@", "playwright"),
    ),
  );

  for (const candidate of candidates) {
    try {
      return require(candidate);
    } catch {
      // Try the next candidate.
    }
  }
  throw new Error(
    "Playwright was not found. Install it in the project or set PLAYWRIGHT_MODULE to its package directory.",
  );
}

const { chromium } = loadPlaywright();

const manifestPath = path.resolve(
  process.argv[2] || path.join(".md-to-pdf-build", "manifest.json"),
);
const manifest = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
if (!Array.isArray(manifest.items)) {
  throw new Error(`Invalid manifest: expected an items array in ${manifestPath}`);
}

const onlyIndex = process.argv.indexOf("--only");
const offline = process.argv.includes("--offline");
const only =
  onlyIndex >= 0
    ? new Set(process.argv[onlyIndex + 1].split(",").map((item) => item.trim()))
    : null;
const selected = only
  ? manifest.items.filter((item) => only.has(item.stem))
  : manifest.items;
if (selected.length === 0) {
  throw new Error("No manifest items matched the requested --only selection.");
}

const metadata = manifest.metadata || {};
const escapeHtml = (value) =>
  String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");

const headerTemplate = `
  <div style="width:100%;padding:0 15mm;font-family:'Noto Sans SC','Microsoft YaHei',sans-serif;font-size:7.5pt;color:#657186;">
    <div style="display:flex;align-items:center;justify-content:space-between;padding-bottom:4px;border-bottom:0.5px solid #cdd7e6;">
      <span style="letter-spacing:0.06em;">${escapeHtml(metadata.headerLeft || "Markdown notes")}</span>
      <span>${escapeHtml(metadata.headerRight)}</span>
    </div>
  </div>`;

const footerTemplate = `
  <div style="width:100%;padding:0 15mm;font-family:'Noto Sans SC','Microsoft YaHei',sans-serif;font-size:8pt;color:#657186;">
    <div style="display:flex;align-items:center;justify-content:space-between;padding-top:4px;border-top:0.5px solid #cdd7e6;">
      <span>${escapeHtml(metadata.footerLeft)}</span>
      <span><span class="pageNumber"></span> / <span class="totalPages"></span></span>
    </div>
  </div>`;

function findBrowser() {
  const candidates = [
    process.env.EDGE_PATH,
    "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
    "C:/Program Files/Microsoft/Edge/Application/msedge.exe",
    "C:/Program Files/Google/Chrome/Application/chrome.exe",
    "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
  ];
  return existingFile(candidates);
}

async function render() {
  const executablePath = findBrowser();
  const browser = await chromium.launch({
    executablePath,
    headless: true,
  });
  const context = await browser.newContext({
    viewport: { width: 1280, height: 900 },
    offline,
  });

  try {
    for (const item of selected) {
      const page = await context.newPage();
      const consoleErrors = [];
      const pageErrors = [];
      page.on("console", (message) => {
        if (message.type() === "error") consoleErrors.push(message.text());
      });
      page.on("pageerror", (error) => pageErrors.push(error.message));

      await page.goto(pathToFileURL(item.html).href, {
        waitUntil: "networkidle",
        timeout: 120000,
      });
      await page.waitForFunction(
        () =>
          window.MathJax &&
          window.MathJax.startup &&
          window.MathJax.startup.promise,
        { timeout: 120000 },
      );
      await page.evaluate(async () => {
        await window.MathJax.startup.promise;
      });

      const stats = await page.evaluate(() => ({
        formulas: document.querySelectorAll(".math").length,
        rendered: document.querySelectorAll("mjx-container").length,
        mathErrors: document.querySelectorAll("mjx-merror").length,
        leakedTokens: (
          document.body.innerText.match(/CODEXPROTECTEDTOKEN/g) || []
        ).length,
      }));
      if (stats.leakedTokens !== 0) {
        throw new Error(`${item.stem}: ${stats.leakedTokens} leaked placeholders`);
      }
      if (stats.mathErrors !== 0) {
        throw new Error(`${item.stem}: ${stats.mathErrors} MathJax errors`);
      }
      if (stats.rendered < stats.formulas) {
        throw new Error(
          `${item.stem}: ${stats.formulas} formulas but ${stats.rendered} rendered`,
        );
      }

      fs.mkdirSync(path.dirname(item.pdf), { recursive: true });
      await page.pdf({
        path: item.pdf,
        format: metadata.pageSize || "A4",
        landscape: Boolean(metadata.landscape),
        printBackground: true,
        preferCSSPageSize: false,
        displayHeaderFooter: true,
        headerTemplate,
        footerTemplate,
        margin: {
          top: "16mm",
          right: "14mm",
          bottom: "17mm",
          left: "14mm",
        },
      });
      console.log(
        `PDF ${item.stem}: ${item.title} (${stats.rendered} formulas rendered)`,
      );
      if (consoleErrors.length) {
        console.warn(
          `Browser console warnings (${item.stem}): ${consoleErrors.join(" | ")}`,
        );
      }
      if (pageErrors.length) {
        throw new Error(
          `${item.stem}: browser page errors: ${pageErrors.join(" | ")}`,
        );
      }
      await page.close();
    }
  } finally {
    await browser.close();
  }
}

render().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
