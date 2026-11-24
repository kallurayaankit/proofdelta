import {build} from 'esbuild';
import {copyFile} from 'node:fs/promises';
await build({entryPoints:['src/app.jsx'],bundle:true,minify:true,format:'esm',outfile:'dist/app.js',define:{'process.env.NODE_ENV':'"production"'},external:['./pdf-engine.js']});
await copyFile('src/diff.js','dist/diff.js');
console.log('React workbench built. PDF engine remains lazy and browser-local.');
