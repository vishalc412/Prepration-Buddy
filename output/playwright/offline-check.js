async (existingPage) => {
  const browser = existingPage.context().browser();
  const isolated = await browser.newContext({viewport:{width:1440,height:1000}});
  const errors=[],remote=[];
  const check=(ok,msg)=>{if(!ok)throw Error(msg)};
  let offlineContext;
  try {
    await isolated.addInitScript(() => {
      if(!localStorage.getItem('principal-ai-studio-v1')) localStorage.setItem('principal-ai-studio-v1',JSON.stringify({version:1,day:1,hours:4,answers:{b1:'Preserved existing learner answer'},code:{1:'# Preserved Python draft'},notes:{capstone:'Preserved capstone note'},finalScores:{Python:true,Statistics:'   '}}));
    });
    const page=await isolated.newPage();
    page.on('pageerror',e=>errors.push(e.message));
    page.on('request',r=>{if(/^https?:/.test(r.url())&&!r.url().startsWith('http://127.0.0.1:8987/'))remote.push(r.url())});
    await page.goto('http://127.0.0.1:8987/index.html');
    check(await page.getByText('84 hours across 14 days.',{exact:false}).isVisible(),'Six-hour overview missing');
    const initial=await page.evaluate(()=>({hours:state.hours,answer:state.answers.b1,code:state.code[1],capstone:state.notes.capstone,invalidScores:Object.keys(state.finalScores).length,study:studyMode()}));
    check(initial.hours===6&&initial.answer==='Preserved existing learner answer'&&initial.code==='# Preserved Python draft'&&initial.capstone==='Preserved capstone note','Version migration lost existing progress');
    check(initial.invalidScores===0&&initial.study,'Migration score validation or study default wrong');
    const totals=await page.evaluate(()=>({modules:OFFLINE.lessons.reduce((s,d)=>s+d.modules.length,0),hints:OFFLINE.lessons.reduce((s,d)=>s+d.modules.reduce((a,m)=>a+m.hints.length,0),0),baseline:OFFLINE.answers.baseline.length,daily:OFFLINE.answers.daily.flat().length,final:OFFLINE.answers.final.length,design:OFFLINE.answers.design.length,labs:OFFLINE.labs.length,minutes:STUDY_BLOCKS.reduce((s,b)=>s+b[1],0)}));
    check(JSON.stringify(totals)===JSON.stringify({modules:70,hints:210,baseline:30,daily:70,final:12,design:14,labs:14,minutes:360}),'Coverage mismatch');
    const nav=async v=>{const b=page.locator('#nav [data-view="'+v+'"]');if(!await b.isVisible())await page.locator('#tools-menu>summary').click();await b.click()};
    await nav('baseline');
    await page.getByRole('button',{name:/^Question 2:/}).click();
    check(await page.locator('.suggested-answer').count()===1,'Study answer requires attempt');
    await page.locator('.suggested-answer > summary').click();
    check((await page.locator('.suggested-answer .detail-body').first().innerText()).length>200,'Suggested answer empty');
    await page.locator('[data-action="drive-mode"][data-mode="practice"]').click();
    check(await page.locator('.suggested-answer').count()===0,'Practice answer not gated');
    check(await page.locator('[data-action="reveal"]').isDisabled(),'Practice rubric not gated');
    await page.getByLabel('Your answer / reasoning / code').fill('Synthetic attempt for UI validation; not learner evidence.');
    await page.locator('[data-action="reveal"]').click();
    check(await page.locator('.suggested-answer').count()===1,'Practice answer did not unlock');
    await page.locator('[data-action="drive-mode"][data-mode="study"]').click();
    await nav('teacher');
    check(await page.locator('[data-action="teacher-stage"]').count()===6,'Teacher blocks missing');
    await page.locator('[data-action="local-hint"]').click();
    check(await page.getByText('Local hints · 1/3',{exact:true}).isVisible(),'Progressive hint failed');
    await page.getByLabel('Question or topic').fill('calibration');
    await page.locator('[data-action="teacher-search"]').click();
    check(await page.locator('#teacher-search-results details').count()>0,'Local search empty');
    await page.locator('[data-action="teacher-stage"][data-index="1"]').click();
    await page.getByLabel('Teacher module').selectOption('1');
    const quiz=await page.evaluate(()=>lessonData(state.day).modules[teacherModule(state.day)].check.answer);
    await page.locator('[data-action="module-hint"]').click();
    check(await page.locator('.deep-module').evaluate(el=>el.open),'Hint collapsed lesson');
    await page.locator('[data-action="module-answer"][data-choice="'+((quiz+1)%3)+'"]').click();
    check(await page.getByText('Revisit the mechanism.',{exact:true}).isVisible(),'Wrong quiz lacks feedback');
    await page.locator('[data-action="module-answer"][data-choice="'+quiz+'"]').click();
    check(await page.getByText('Correct fixed-answer check.',{exact:true}).isVisible(),'Correct quiz lacks feedback');
    await page.locator('[data-action="teacher-record"]').click();
    check((await page.locator('[data-action="teacher-stage"][data-index="1"]').innerText()).includes('recorded complete'),'Teacher progress missing');
    await page.locator('[data-action="teacher-stage"][data-index="3"]').click();
    await page.locator('.reference-solution > summary').click();
    await page.getByText('day01_inventory.py · python',{exact:true}).click();
    const downloadPromise=page.waitForEvent('download');
    await page.getByRole('button',{name:'Download day01_inventory.py',exact:true}).click();
    check((await downloadPromise).suggestedFilename()==='day01_inventory.py','Reference download wrong');
    check((await page.getByLabel('Draft code / command or file reference').inputValue())==='# Preserved Python draft','Reference overwrote learner code');
    await nav('answers');
    await page.getByLabel('Answer group').selectOption('Lab solutions');
    await page.getByLabel('Answer day').selectOption('12');
    check((await page.locator('#app').innerText()).includes('1 matching entries.'),'Filtered lab count wrong');
    check(await page.locator('.reference-solution').count()===1,'Filtered labs wrong');
    await page.getByLabel('Answer group').selectOption('Baseline');
    await page.getByLabel('Answer day').selectOption('All');
    check(await page.locator('.suggested-answer').count()===30,'Baseline answer bank incomplete');
    await page.getByLabel('Search local content').fill('mutable');
    check(await page.locator('.suggested-answer').count()>0&&await page.locator('.suggested-answer').count()<30,'Answer search failed');
    await nav('learn');
    for(let n=1;n<=14;n++) {
      await page.getByLabel('Choose day').selectOption(String(n));
      for(const name of ['Learn','Code & build','Design & defend','Daily assessment']) {
        await page.getByRole('button',{name,exact:true}).click();
        check((await page.locator('#app').innerText()).length>200,'Empty daily view '+n+'/'+name);
      }
    }
    // Every local module quiz has a reachable question, feedback and fixed answer.
    await nav('teacher');
    for(let n=1;n<=14;n++) {
      await page.getByLabel('Teacher day').selectOption(String(n));
      await page.locator('[data-action="teacher-stage"][data-index="1"]').click();
      const modules=await page.getByLabel('Teacher module').locator('option').count();
      for(let i=0;i<modules;i++) {
        await page.getByLabel('Teacher module').selectOption(String(i));
        const correct=await page.evaluate(()=>lessonData(state.day).modules[teacherModule(state.day)].check.answer);
        await page.locator('[data-action="module-answer"][data-choice="'+correct+'"]').click();
        check(await page.getByText('Correct fixed-answer check.',{exact:true}).isVisible(),'Quiz feedback missing '+n+'/'+i);
        check(await page.locator('.deep-module .learning-links a[href*="youtube.com/watch"]').count()>0,'Module video missing '+n+'/'+i);
        check(await page.locator('.deep-module .learning-links a[href]:not([href*="youtube"])').count()>0,'Module docs missing '+n+'/'+i);
      }
    }
    await nav('interview');
    await page.getByRole('button',{name:'Final simulation',exact:true}).click();
    check(await page.getByRole('button',{name:/^Round/}).count()===12,'Final rounds incomplete');
    check(await page.locator('.suggested-answer').count()===1,'Final suggested answer missing');
    await nav('capstone');
    check(await page.getByText('Suggested behavioral answers · truthful templates',{exact:true}).isVisible(),'Story guidance missing');
    await nav('scores');
    check(await page.locator('[data-final]').count()===17,'Domain count wrong');
    const exportPromise=page.waitForEvent('download');
    await page.getByRole('button',{name:'Export progress ↗'}).click();
    check((await exportPromise).suggestedFilename().endsWith('.json'),'Backup download failed');
    await page.reload();
    const restored=await page.evaluate(()=>({hint:state.notes['hint-b1'],quiz:state.notes['module-quiz-1-1'],block:state.notes['teacher-complete-1-1'],answer:state.answers.b1,code:state.code[1],hours:state.hours}));
    check(restored.hint==='1'&&restored.quiz===String(quiz)&&restored.block==='yes'&&restored.answer===initial.answer&&restored.code===initial.code&&restored.hours===6,'Teacher progress did not persist');
    await nav('teacher');
    await page.getByLabel('Teacher day').selectOption('1');
    await page.locator('[data-action="teacher-stage"][data-index="1"]').click();
    await page.setViewportSize({width:1440,height:1000});
    await page.screenshot({path:'output/playwright/offline-desktop.png'});
    await page.setViewportSize({width:390,height:844});
    check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'Mobile horizontal overflow');
    await page.screenshot({path:'output/playwright/offline-mobile.png'});
    // Verify every interactive section after disabling network.
    await isolated.setOffline(true);
    for(const v of ['overview','roadmap','baseline','learn','teacher','interview','retest','capstone','scores','resources','answers'])await nav(v);
    check(remote.length===0,'Remote dependencies: '+remote.join(', '));
    const html=await page.content();
    // Fresh JavaScript realm: standalone document boots while browser fully offline.
    offlineContext=await browser.newContext({offline:true});
    const offlinePage=await offlineContext.newPage();
    offlinePage.on('pageerror',e=>errors.push(e.message));
    await offlinePage.setContent(html);
    check(await offlinePage.getByRole('button',{name:'Start local teacher →'}).isVisible(),'Standalone offline bootstrap failed');
    await offlinePage.locator('#nav [data-view="teacher"]').click();
    await offlinePage.locator('[data-action="local-hint"]').click();
    check(await offlinePage.getByText('Local hints · 1/3',{exact:true}).isVisible(),'Fresh offline hints failed');
    check(errors.length===0,'Runtime errors: '+errors.join('; '));
    return {status:'PASS',...totals,days:14,dayTabs:56,quizzesExercised:70,remoteRequests:remote.length,runtimeErrors:errors.length,isolatedStorage:true,verified:['six-hour migration preserves answers/code/notes','Study answers immediately available','Practice gate and reveal','progressive hints','targeted wrong/correct quiz feedback','teacher block persistence','local search','reference downloads preserve drafts','filtered answer bank','all daily tabs','all 70 module quizzes','12 final rounds','17 score domains','truthful story templates','JSON export','mobile no overflow','network-disabled navigation','fresh standalone offline bootstrap']};
  } finally {if(offlineContext)await offlineContext.close();await isolated.close()}
}
