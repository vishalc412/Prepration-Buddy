async existingPage => {
 const ctx=await existingPage.context().browser().newContext({viewport:{width:1440,height:1000}});
 const check=(ok,msg)=>{if(!ok)throw Error(msg)};
 try {
 const page=await ctx.newPage();await page.goto('http://127.0.0.1:8987/index.html');
 await page.getByRole('button',{name:'Open practical case studies →',exact:true}).click();await page.getByRole('button',{name:'Implement & test',exact:true}).click();
 await page.locator('#case-code').fill('Synthetic persisted case implementation');await page.locator('textarea[data-map="evidence"]').fill('Synthetic persisted case evidence');
 await page.getByRole('button',{name:'Defend decisions',exact:true}).click();await page.locator('#case-defense').fill('Synthetic persisted case defense');
 await page.locator('textarea[data-key="case-follow-case-modernization-0"]').fill('Synthetic persisted case follow-up');
 const wait=page.waitForEvent('download');await page.getByRole('button',{name:'Export progress ↗'}).click();const backup=await wait,stream=await backup.createReadStream();let body='';for await(const chunk of stream)body+=chunk.toString();const exported=JSON.parse(body);
 check(exported.code['case-modernization']==='Synthetic persisted case implementation'&&exported.evidence['case-modernization']==='Synthetic persisted case evidence'&&exported.answers['case-modernization']==='Synthetic persisted case defense'&&exported.notes['case-follow-case-modernization-0']==='Synthetic persisted case follow-up','Case export missing');
 page.once('dialog',d=>d.accept());await page.locator('#import-file').setInputFiles(await backup.path());check(await page.evaluate(()=>state.code['case-modernization']==='Synthetic persisted case implementation'&&state.answers['case-modernization']==='Synthetic persisted case defense'&&state.notes['case-follow-case-modernization-0']==='Synthetic persisted case follow-up'),'Case import failed');
 await page.locator('#nav [data-view="overview"]').click();await page.getByRole('button',{name:'Open practical case studies →',exact:true}).click();await page.locator('[data-action="case-select"][data-id="case-enterprise"]').click();await page.evaluate(()=>window.scrollTo(0,0));await page.screenshot({path:'output/playwright/buddy-practical-studio.png'});
 return {status:'PASS',caseExportImport:true,screenshot:'output/playwright/buddy-practical-studio.png',learnerStorageUntouched:true};
 } finally {await ctx.close()}
}
