// Development-only: npm install --no-save playwright && npx playwright install chromium
exports.launch=async()=>{
 if(process.env.STUDIO_USE_SPARTICUZ==='1'){
  const runtime=require('@sparticuz/chromium');
  return require('playwright-core').chromium.launch({executablePath:await runtime.executablePath(),args:runtime.args,headless:true});
 }
 return require('playwright').chromium.launch({headless:true,args:['--enable-unsafe-swiftshader']});
};
