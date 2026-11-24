// ProofDelta: PDF.js runs entirely in this tab and a same-origin module worker.
// Only static parser assets are loaded. File bytes are passed to PDF.js, never fetched or posted.
const MAX_BYTES = 30 * 1024 * 1024;
const MAX_PAGES = 200;
const MAX_TEXT_LENGTH = 4_000_000;
const engine = () => import("./pdfjs/pdf.min.mjs");
const indexes = () => Promise.all([
  import("./pdfjs/cmaps-index.mjs"),
  import("./pdfjs/standard_fonts-index.mjs"),
]);
const cmapChunks = [
  () => import("./pdfjs/cmaps-0.mjs"),
  () => import("./pdfjs/cmaps-1.mjs"),
  () => import("./pdfjs/cmaps-2.mjs"),
  () => import("./pdfjs/cmaps-3.mjs"),
];
const fontChunks = [
  () => import("./pdfjs/standard_fonts-0.mjs"),
  () => import("./pdfjs/standard_fonts-1.mjs"),
];

class BundledBinaryDataFactory {
  async fetch({kind, filename}) {
    const [cmaps, fonts] = await indexes();
    const loaders = kind === "cMapUrl" ? cmapChunks :
      kind === "standardFontDataUrl" ? fontChunks : null;
    const index = kind === "cMapUrl" ? cmaps.default : fonts.default;
    if (!loaders || !Object.hasOwn(index, filename)) {
      throw new Error("PDF decoding resource is unavailable.");
    }
    const table = (await loaders[index[filename]]()).default;
    return Uint8Array.from(atob(table[filename]), character => character.charCodeAt(0));
  }
}

function pageText(items) {
  const lines = [];
  let line = "";
  let prev = null;
  for (const item of items) {
    if (typeof item.str !== "string") continue;
    const text = item.str.replace(/[\u0000\u0001]/g, "");
    if (prev && line && text && item.transform && prev.transform) {
      const baselineShift = Math.abs(item.transform[5] - prev.transform[5]);
      const height = Math.max(item.height || 0, prev.height || 0, 1);
      const gap = item.transform[4] - prev.transform[4] - (prev.width || 0);
      const ordinaryHorizontal = Math.abs(item.transform[1]) < 0.01 &&
        Math.abs(prev.transform[1]) < 0.01 &&
        item.dir !== "rtl" && prev.dir !== "rtl";
      if (ordinaryHorizontal && baselineShift > height * 0.6) {
        lines.push(line.trimEnd());
        line = "";
      } else if (ordinaryHorizontal && gap > height * 0.18 && !/\s$/.test(line) && !/^\s/.test(text)) {
        line += " ";
      }
    }
    line += text;
    if (item.hasEOL) {
      lines.push(line.trimEnd());
      line = "";
    }
    prev = item.hasEOL ? null : item;
  }
  if (line) lines.push(line.trimEnd());
  return lines.join("\n").trim();
}

export async function readPdf(file) {
  if (!file || typeof file.arrayBuffer !== "function") throw new Error("Choose a PDF file.");
  if (file.size > MAX_BYTES) throw new Error("This PDF exceeds the 30 MB limit.");
  const name = typeof file.name === "string" ? file.name : "Document.pdf";
  const bytes = new Uint8Array(await file.arrayBuffer());
  if (bytes.byteLength > MAX_BYTES) throw new Error("This PDF exceeds the 30 MB limit.");
  if (!new TextDecoder().decode(bytes.subarray(0, 1024)).includes("%PDF-")) {
    throw new Error("This file does not appear to be a PDF.");
  }

  let parser;
  try {
    parser = await engine();
    parser.GlobalWorkerOptions.workerSrc = new URL("./pdfjs/pdf.worker.min.mjs", import.meta.url).href;
  } catch {
    throw new Error("The local PDF reader could not load. Try reloading in a current browser.");
  }

  let job;
  try {
    job = parser.getDocument({
      data: bytes,
      BinaryDataFactory: BundledBinaryDataFactory,
      cMapPacked: true,
      useWorkerFetch: false,
      useWasm: false,
      enableXfa: false,
      isEvalSupported: false,
      disableFontFace: true,
      useSystemFonts: false,
      stopAtErrors: true,
      verbosity: parser.VerbosityLevel.ERRORS,
    });
    const document = await job.promise;
    if (document.numPages > MAX_PAGES) throw new PdfReadError("This PDF exceeds the 200-page limit.");
    const pages = [];
    let length = 0;
    for (let index = 1; index <= document.numPages; index += 1) {
      const page = await document.getPage(index);
      const content = await page.getTextContent();
      const text = pageText(content.items);
      length += text.length;
      if (length > MAX_TEXT_LENGTH) throw new PdfReadError("This PDF exceeds the extractable text limit.");
      pages.push(text);
      page.cleanup();
    }
    if (!pages.some(Boolean)) {
      throw new PdfReadError("No selectable text was found. Scanned or image-only PDFs require OCR, which is not included.");
    }
    return {name, pages};
  } catch (error) {
    if (error instanceof PdfReadError) throw error;
    if (error?.name === "PasswordException") {
      throw new Error("This PDF is password protected. Open or unlock it yourself, then choose an unprotected copy.");
    }
    if (error?.name === "InvalidPDFException") {
      throw new Error("This PDF is damaged or unsupported. Try saving a new text-based PDF.");
    }
    throw new Error("Text could not be extracted from this PDF. Try a supported PDF with selectable text.", {cause: error});
  } finally {
    if (job) await job.destroy().catch(() => {});
  }
}

class PdfReadError extends Error {}
