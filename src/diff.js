const normalize = s => s.normalize('NFC').replace(/[\u00a0\t]+/g,' ').replace(/ {2,}/g,' ').trim();
export const lines = s => String(s ?? '').split(/\r?\n/).map(normalize).filter(Boolean);
export function compareDocs(a,b){
  const out=[];
  for(let page=0;page<Math.max(a.pages.length,b.pages.length);page++){
    if(page>=a.pages.length || page>=b.pages.length) out.push({page:page+1,before:page>=a.pages.length?'': 'Page present',after:page>=b.pages.length?'':'Page present',kind:'Page count'});
    const x=lines(a.pages[page]),y=lines(b.pages[page]),n=x.length,m=y.length;
    if(n*m>750000 || n+m>5000) throw Error('One page has too many extracted text lines. Try a smaller set of pages.');
    const lcs=new Uint16Array((n+1)*(m+1)),w=m+1;
    for(let i=n-1;i>=0;i--)for(let j=m-1;j>=0;j--) lcs[i*w+j]=x[i]===y[j]?lcs[(i+1)*w+j+1]+1:Math.max(lcs[(i+1)*w+j],lcs[i*w+j+1]);
    let i=0,j=0,removed=[],added=[];
    const flush=()=>{for(let k=0;k<Math.max(removed.length,added.length);k++)out.push({page:page+1,before:removed[k]?.text??'',after:added[k]?.text??'',beforeLine:removed[k]?.line??null,afterLine:added[k]?.line??null,kind:removed[k]&&added[k]?'Changed line':removed[k]?'Removed line':'Added line'}); removed=[];added=[];};
    while(i<n||j<m){if(i<n&&j<m&&x[i]===y[j]){flush();i++;j++}else if(j===m || (i<n&&lcs[(i+1)*w+j]>=lcs[i*w+j+1]))removed.push({text:x[i],line:++i});else added.push({text:y[j],line:++j});}
    flush();
    if(out.length>8000) throw Error('Too many differences for this preview. Try comparing fewer pages.');
  }
  return out;
}
export const sample={
  a:{name:'Approved oat-bites label (sample)',pages:['Original oat bites\nNet weight: 180 g\nIngredients: oats, dates, sunflower oil, sea salt.\nBatch code: OB042','Store in a cool, dry place.\nPack made from recycled paper.']},
  b:{name:'Printer’s oat-bites proof (sample)',pages:['Original oat bites\nNet weight: 160 g\nIngredients: oats, dates, canola oil, sea salt.\nBatch code: OB042','Store in a cool, dry place.\nPack made from recycled paper.\nPrinter reference: 221B']},
};
export const escape = x => String(x).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export function reportHtml({a,b,deltas,isSample,decisions={}}){
  const highlights = [new Set(),new Set()];
  for (const d of deltas) { if(d.beforeLine) highlights[0].add(d.page+':'+d.beforeLine); if(d.afterLine) highlights[1].add(d.page+':'+d.afterLine); }
  const noText = d => d.pages.flatMap((v,i)=>v.trim()?[]:[i+1]).join(', ') || 'none';
  return '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ProofDelta difference report</title><style>body{font:1rem/1.5 system-ui;max-width:68rem;padding:1rem;margin:auto;color:#102321}table{width:100%;border-collapse:collapse}th,td{border:1px solid #b7ccc3;text-align:left;padding:.5rem;overflow-wrap:anywhere}th{background:#e8f4ec}small{display:block}.pair{display:grid;grid-template-columns:1fr 1fr;gap:1rem}.pair>div{min-width:0}li{overflow-wrap:anywhere;padding:.2rem}.changed{background:#fff0c2}section{break-inside:avoid}@media(max-width:600px){.pair{grid-template-columns:1fr}}</style><body><h1>ProofDelta · text difference report</h1><p>'+ (isSample?'Fictional sample · ':'') +'Generated '+escape(new Date().toISOString())+'</p><p><strong>Approved:</strong> '+escape(a.name)+' ('+a.pages.length+' pages)<br><strong>Printer’s proof:</strong> '+escape(b.name)+' ('+b.pages.length+' pages)</p><p><strong>'+deltas.length+' detected differences.</strong> Pages with no extracted text: approved '+noText(a)+'; printer’s proof '+noText(b)+'. Review decisions record inspection, not print approval. Text only. Not print sign-off, barcode validation or compliance certification. Review the original proofs.</p><table><thead><tr><th>Page</th><th>Difference</th><th>Approved</th><th>Printer’s proof</th><th>Review decision</th></tr></thead><tbody>'+ deltas.map((d,i)=>'<tr><td>'+d.page+'</td><td>'+escape(d.kind)+'</td><td>'+escape(d.before||'No line')+'</td><td>'+escape(d.after||'No line')+'</td><td>'+escape(decisions[i]||'Not reviewed')+'</td></tr>').join('')+'</tbody></table><h2>Full extracted page context</h2><p>Pages are paired by page number. Line numbers refer to non-empty extracted lines. Highlighting marks text differences, not artwork changes.</p>'+Array.from({length:Math.max(a.pages.length,b.pages.length)},(_,i)=>'<section><h3>Page '+(i+1)+'</h3><div class=pair>'+[a,b].map((doc,side)=>'<div><h4>'+(side?'Printer’s proof':'Approved')+'</h4>'+(!Object.hasOwn(doc.pages,i)?'<p>Page not present</p>':lines(doc.pages[i]).length?'<ol>'+lines(doc.pages[i]).map((line,j)=>'<li'+(highlights[side].has((i+1)+':'+(j+1))?' class=changed':'')+'>'+escape(line)+'</li>').join('')+'</ol>':'<p>No selectable text on this page.</p>')+'</div>').join('')+'</div></section>').join('')+'</body></html>';
}
