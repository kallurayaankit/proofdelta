import {readFile} from "node:fs/promises";
import assert from "node:assert/strict";
import {readPdf} from "../dist/pdf-engine.js";
// Modern PDF.js initializes transformation utilities eagerly. Text extraction
// doesn't use these canvas classes; the test runs PDF.js's Node fake worker.
globalThis.DOMMatrix ??= class {};
globalThis.ImageData ??= class {};
globalThis.Path2D ??= class {};
Uint8Array.prototype.toHex ??= function() { return Buffer.from(this).toString("hex"); };
Uint8Array.fromHex ??= text => new Uint8Array(Buffer.from(text,"hex"));
const file = async n => new File([await readFile(new URL(n,import.meta.url))],n);
assert.deepEqual(await readPdf(await file("normal.pdf")), {name:"normal.pdf",pages:["ProofDelta first line.\nSecond line 42.","Second page."]});
assert.deepEqual((await readPdf(await file("japanese.pdf"))).pages,["東京の文書"]);
await assert.rejects(readPdf(await file("locked.pdf")), /password protected/);
await assert.rejects(readPdf(await file("image.pdf")), /No selectable text/);
await assert.rejects(readPdf(await file("sample.png")), /does not appear/);
await assert.rejects(readPdf(new File(["%PDF-1.4 invalid"],"bad.pdf")), /damaged or unsupported/);
console.log("Six PDF text and failure cases passed.");
