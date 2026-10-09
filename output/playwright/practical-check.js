async existingPage => {
 const ctx=await existingPage.context().browser().newContext({viewport:{width:1440,height:1000}}),errors=[],remote=[],downloads=[];
 const check=(ok,msg)=>{if(!ok)throw Error(msg)};
 try {
 const page=await ctx.newPage();page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(/^https?:/.test(r.url())&&!r.url().startsWith('http://127.0.0.1:8987/'))remote.push(r.url())});
 await page.goto('http://127.0.0.1:8987/index.html');const html=await page.content();
 check(await page.evaluate(()=>OFFLINE.cases.length===4&&coverageRows().length===154&&DAYS.length===30&&state.hours===4),'Payload totals wrong');
 await page.getByRole('button',{name:'Open practical case studies →',exact:true}).click();
 check(await page.locator('.client-list [data-action="case-select"]').count()===4,'Missing projects');
 await page.getByRole('button',{name:'Challenge',exact:true}).click();
 const cases=await page.evaluate(()=>OFFLINE.cases.map(c=>({id:c.id,title:c.title,files:c.files.length})));
 for(const c of cases){
 await page.locator('[data-action="case-select"][data-id="'+c.id+'"]').click();check(await page.locator('#case-active h2').innerText()===c.title,'Case selection wrong');
 await page.getByRole('button',{name:'Implement & test',exact:true}).click();check(await page.locator('#case-reference details').count()===0,'Reference leaked before attempt');
 for(let i=1;i<=3;i++){await page.getByRole('button',{name:i===1?'Show hint':'Next hint',exact:true}).click();check((await page.locator('#case-active').innerText()).includes(i+'/3 hints'),'Hint did not advance')}
 check(await page.getByRole('button',{name:'Next hint',exact:true}).isDisabled(),'Hint not bounded');
 await page.locator('#case-code').fill('Synthetic browser test draft for '+c.id);check(await page.locator('#case-reference details').count()===c.files,'Attempt did not unlock all files');
 const zipWait=page.waitForEvent('download');await page.getByRole('button',{name:'Download complete reference project ZIP ↓',exact:true}).click();const download=await zipWait;downloads.push({id:c.id,name:download.suggestedFilename(),path:await download.path()});
 await page.locator('#case-reference details').first().locator('summary').click();const fileWait=page.waitForEvent('download');await page.locator('#case-reference details').first().getByRole('button').click();const individual=await fileWait;check((await individual.suggestedFilename()).length>0,'Individual download missing');
 await page.locator('textarea[data-map="evidence"]').fill('Synthetic UI evidence, not an execution receipt.');
 await page.getByRole('button',{name:'Defend decisions',exact:true}).click();check(await page.locator('#case-answer-support details').count()===0,'Defense leaked');
 await page.locator('#case-defense').fill('Synthetic browser defense.');check(await page.locator('#case-answer-support details').count()===1,'Defense gate failed');
 for(let i=0;i<2;i++){check(await page.locator('#case-follow-'+i+' details').count()===0,'Follow-up leaked');await page.locator('textarea[data-key="case-follow-'+c.id+'-'+i+'"]').fill('Synthetic independent follow-up.');check(await page.locator('#case-follow-'+i+' details').count()===1,'Follow-up gate failed')}
 }
 await page.reload();check(await page.evaluate(()=>OFFLINE.cases.every(c=>state.code[c.id].startsWith('Synthetic browser')&&state.answers[c.id]==='Synthetic browser defense.'&&state.evidence[c.id].startsWith('Synthetic UI'))),'Reload lost case work');
 await page.getByRole('button',{name:'Open practical case studies →',exact:true}).click();await page.getByRole('button',{name:'JD coverage audit',exact:true}).click();check(await page.locator('.coverage-list>details').count()===154,'Coverage rows missing');
 for(const q of ['TLS','TensorFlow','.NET','MCP']){await page.locator('#coverage-search').fill(q);check(await page.locator('.coverage-list>details').count()>0,'No coverage for '+q);check(await page.evaluate(()=>document.activeElement.id)==='coverage-search','Search lost focus')}
 await page.locator('#coverage-search').fill('no-match-qzx');check(await page.locator('.coverage-list>details').count()===0,'No-match filter failed');
 await page.locator('#coverage-search').fill('');await page.locator('[data-control="coverage-status"]').selectOption('credential/experience');check(await page.locator('.coverage-list>details').count()>0,'Credential gaps hidden');await page.locator('[data-control="coverage-status"]').selectOption('All');
 await page.getByRole('button',{name:'Case studies & implementations',exact:true}).click();await page.getByRole('button',{name:'Study',exact:true}).click();await page.locator('[data-action="case-select"][data-id="case-enterprise"]').click();
 for(const width of [1440,847,390]){await page.setViewportSize({width,height:1000});check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'Horizontal overflow at '+width);await page.getByRole('button',{name:'Implement & test',exact:true}).click();await page.locator('#case-reference details').first().locator('summary').click();check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'Code overflow at '+width);await page.getByRole('button',{name:'Understand the case',exact:true}).click()}
 await page.setViewportSize({width:1440,height:1000});await page.screenshot({path:'output/playwright/buddy-practical-enterprise.png'});
 const offline=await ctx.newPage();let offlineRequests=0;offline.on('request',r=>{if(/^https?:/.test(r.url()))offlineRequests++});await offline.setContent(html);check(await offline.evaluate(()=>OFFLINE.cases.length===4&&coverageRows().length===154),'Standalone payload failed');await offline.getByRole('button',{name:'Open practical case studies →',exact:true}).click();await offline.getByRole('button',{name:'Implement & test',exact:true}).click();check(await offline.locator('#case-reference details').count()>0,'Standalone reference failed');check(offlineRequests===0,'Standalone made remote requests');
 check(errors.length===0,'Runtime errors '+JSON.stringify(errors));check(remote.length===0,'Remote dependency '+JSON.stringify(remote));
 return {status:'PASS',cases:cases.length,mappedTopics:154,downloadProjects:downloads,viewports:[1440,847,390],offlineRequests,errors,remote};
 } catch(error) {await ctx.close();throw error}
 // Keep the isolated context until the parent verifies real downloaded ZIP bytes.
}
