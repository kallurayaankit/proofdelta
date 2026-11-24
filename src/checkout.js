// Static preview: local simulation. Local Rust server opts in with a meta tag.
// No file contents, names, extracted text, or review decisions are transmitted.
export async function simulateCheckout(){
  if(document.querySelector('meta[name="proofdelta-service"]')?.content==='rust-local'){
    const response=await fetch('/api/checkout/simulate',{method:'POST',headers:{'X-ProofDelta-Simulation':'1'}});
    if(!response.ok)throw Error('Simulation failed');
    const receipt=await response.json();
    if(receipt.mode!=='simulation'||receipt.charged!==false||receipt.unlocked!==true)throw Error('Invalid simulation receipt');
    return receipt;
  }
  return {mode:'simulation',charged:false,unlocked:true,currency:'AUD',amount_minor:3900};
}
