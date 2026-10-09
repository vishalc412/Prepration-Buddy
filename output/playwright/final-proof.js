async existingPage => {
 const ctx=await existingPage.context().browser().newContext({viewport:{width:1440,height:1000}});
 try{const p=await ctx.newPage();await p.goto('http://127.0.0.1:8987/index.html');await p.getByRole('button',{name:'Explore revised JD drills →',exact:true}).click();await p.screenshot({path:'output/playwright/buddy-revised-jd-desktop.png',fullPage:false});return {status:'PASS',jdCards:await p.locator('[data-action="jd-select"]').count(),screenshot:'output/playwright/buddy-revised-jd-desktop.png'};}finally{await ctx.close()}
}
