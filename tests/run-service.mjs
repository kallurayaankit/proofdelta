import {spawn} from 'node:child_process';
const child=spawn('cargo',['run','--manifest-path','backend/Cargo.toml'],{stdio:['ignore','pipe','inherit']});
try{
  await new Promise((resolve,reject)=>{
    const timer=setTimeout(()=>reject(Error('Rust service did not become ready')),30000);
    child.on('error',reject);child.on('exit',code=>reject(Error('Service exited: '+code)));
    child.stdout.on('data',chunk=>{process.stdout.write(chunk);if(chunk.toString().includes('simulation only')){clearTimeout(timer);resolve();}});
  });
  await import('./service.mjs');
}finally{child.kill();}
