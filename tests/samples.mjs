import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {readPdf} from '../dist/pdf-engine.js';
import {compareDocs,reportHtml} from '../src/diff.js';
globalThis.DOMMatrix??=class{};globalThis.ImageData??=class{};globalThis.Path2D??=class{};
Uint8Array.prototype.toHex??=function(){return Buffer.from(this).toString('hex')};
Uint8Array.fromHex??=text=>new Uint8Array(Buffer.from(text,'hex'));
const docs=await Promise.all(['approved','printer'].map(async n=>readPdf(new File([await readFile(new URL('../dist/samples/'+n+'-oat-bites.pdf',import.meta.url))],n+'.pdf'))));
const deltas=compareDocs(...docs);
assert.equal(deltas.length,3);assert.deepEqual(deltas.map(d=>d.page),[1,1,2]);
for(const d of deltas){if(d.beforeLine)assert(d.before);if(d.afterLine)assert(d.after);}
const report=reportHtml({a:docs[0],b:docs[1],deltas,isSample:true,decisions:{0:'Reviewed',1:'Follow up'}});
assert(report.includes('Full extracted page context'));assert(report.includes('Follow up'));assert(report.includes('Not reviewed'));assert(report.includes('180 g'));assert(report.includes('160 g'));
const repeated=compareDocs({pages:['A\nx\nA']},{pages:['A\ny\nA']});assert.equal(repeated[0].beforeLine,2);assert.equal(repeated[0].afterLine,2);
const hostile=reportHtml({a:{name:'<img onerror=alert(1)>',pages:['<script>']},b:{name:'proof',pages:['& test']},deltas:[{page:1,kind:'Changed',before:'<script>',after:'& test'}],decisions:{0:'<script>'}});assert(!hostile.includes('<script>'));assert(!hostile.includes('<img '));
console.log('Sample PDF integration, line attribution, review export and escaping passed.');
