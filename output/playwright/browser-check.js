async (existingPage) => {
  const isolated=await existingPage.context().browser().newContext();
  const page=await isolated.newPage();
  await page.goto('http://127.0.0.1:8987/index.html');
  try {
  const failures=[];
  const check=(ok,msg)=>{if(!ok)throw Error(msg)};
  page.on('pageerror', e=>failures.push(e.message));
  await page.evaluate(()=>{state=fresh();save()});
  await page.reload();
  await page.locator('[data-action="drive-mode"][data-mode="practice"]').click();
  await page.locator('#nav [data-view=baseline]').click();
  check(await page.getByRole('button',{name:'I’ve attempted — review rubric'}).isDisabled(),'Rubric visible before attempt');
  check(await page.locator('.callout').filter({hasText:'Review anchors'}).count()===0,'Answer key exposed');
  await page.getByRole('textbox',{name:'Your answer / reasoning / code'}).fill('Synthetic browser verification answer; not learner evidence.');
  await page.getByRole('button',{name:'I’ve attempted — review rubric'}).click();
  await page.getByRole('button',{name:'1 · Terms only'}).click();
  await page.reload();
  await page.locator('#nav [data-view=baseline]').click();
  check((await page.getByRole('textbox',{name:'Your answer / reasoning / code'}).inputValue()).includes('Synthetic browser'),'Answer not persisted');
  await page.locator('#nav [data-view=learn]').click();
  check(await page.getByText('Attempt before studying.').isVisible(),'Lessons failed to lock');
  await page.locator('#nav [data-view=baseline]').click();
  for(let i=0;i<30;i++){
    await page.getByRole('button',{name:new RegExp('^Question '+(i+1)+':')}).click();
    await page.getByRole('textbox',{name:'Your answer / reasoning / code'}).fill('Synthetic test attempt '+(i+1)+'. I do not know; this is UI verification.');
  }
  await page.getByRole('button',{name:'Finish baseline'}).click();
  check(await page.getByText('Confidence needs a denominator.').isVisible(),'Baseline finish failed');
  await page.locator('#nav [data-view=learn]').click();
  check(await page.locator('.deep-module').count()===5,'Lessons did not unlock');
  await page.getByRole('button',{name:'Code & build',exact:true}).click();
  const fixtureDownload=page.waitForEvent('download');
  await page.getByRole('button',{name:'Download Day 1 inventory CSV ↗'}).click();
  const csv=await fixtureDownload;
  check(csv.suggestedFilename()==='inventory.csv','CSV download filename incorrect');
  await page.getByLabel('Draft code / command or file reference').fill('# synthetic attempt');
  await page.getByLabel('Actual run evidence and limitations').fill('Synthetic browser check only; no Python execution claim.');
  for(const box of await page.getByRole('checkbox').all())await box.check();
  await page.getByRole('button',{name:'Daily assessment',exact:true}).click();
  await page.getByLabel('Python /100',{exact:true}).fill('75');
  await page.getByLabel('Python /100',{exact:true}).blur();
  await page.getByRole('button',{name:'Mark day completed'}).click();
  check(await page.getByRole('button',{name:'Reopen day'}).isVisible(),'Day completion failed');
  await page.locator('#nav [data-view=retest]').click();
  check(await page.getByText('Ready to retest',{exact:true}).isVisible(),'Weak question missing from retest');
  await page.getByLabel('New closed-book answer').fill('Synthetic retest attempt with mechanism, failure and test.');
  await page.getByRole('button',{name:'Attempt complete — review'}).click();
  await page.locator('.rating button').filter({hasText:/^3$/}).click();
  check((await page.getByText(/^Scheduled /).count())===1,'Spaced retest not scheduled');
  await page.locator('#nav [data-view=learn]').click();
  await page.getByLabel('Choose day').selectOption('2');
  await page.getByRole('button',{name:'A. Sensitivity alone.',exact:true}).click();
  check(await page.getByText('Mechanism gap. Try again after explaining why.').isVisible(),'Quiz feedback failed');
  await page.getByRole('button',{name:'C. None: false-positive rate and prevalence also matter.',exact:true}).click();
  check(await page.getByText('Correct concept check.').isVisible(),'Quiz correct answer failed');
  await page.locator('#threshold').fill('0.75');
  check((await page.locator('#threshold-results').innerText()).includes('2 / 1 / 6 / 3'),'Threshold confusion matrix incorrect');
  await page.getByLabel('Choose day').selectOption('6');
  await page.locator('#budget-candidateTokens').fill('1000');
  check((await page.locator('#budget-results').innerText()).includes('54.3%'),'Token-cost arithmetic incorrect');
  for(let i=1;i<=14;i++){
    await page.getByLabel('Choose day').selectOption(String(i));
    for(const name of ['Learn','Code & build','Design & defend','Daily assessment']){
      await page.getByRole('button',{name,exact:true}).click();
      check((await page.locator('#app').innerText()).length>150,'Empty day tab '+i+'/'+name);
    }
  }
  await page.locator('#nav [data-view=capstone]').click();
  check(await page.getByText('Build adapters, not a second language curriculum.',{exact:true}).isVisible(),'Python/Java plugin scope missing');
  await page.locator('#nav [data-view=interview]').click();
  await page.getByRole('button',{name:'Final simulation',exact:true}).click();
  check(await page.getByRole('button',{name:/^Round/}).count()===12,'Incorrect final round count');
  await page.getByLabel('Your first answer').fill('Synthetic timed answer');
  await page.getByRole('button',{name:'Next question →'}).click();
  check(await page.getByText('Round 2 · ML + statistics',{exact:true}).isVisible(),'Mock round advance failed');
  await page.locator('#nav [data-view=scores]').click();
  check(await page.locator('[data-final]').count()===17,'Final domain score count incorrect');
  const exported=page.waitForEvent('download');
  await page.getByRole('button',{name:'Export progress ↗'}).click();
  check((await exported).suggestedFilename().endsWith('.json'),'Export failed');
  const stored=await page.evaluate(()=>JSON.parse(localStorage.getItem('principal-ai-studio-v1')));
  check(Object.keys(stored.answers).length>=30,'Export state lacks baseline');
  await page.evaluate(()=>{state=fresh();save()});
  await page.reload();
  await page.setViewportSize({width:1440,height:1000});
  await page.screenshot({path:'output/playwright/desktop.png',fullPage:true});
  await page.setViewportSize({width:390,height:844});
  check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'Mobile horizontal overflow');
  await page.screenshot({path:'output/playwright/mobile.png',fullPage:true});
  check(failures.length===0,'Browser runtime errors: '+failures.join('; '));
  await page.evaluate(()=>{state=fresh();save()});
  await page.reload();
  return {status:'PASS',baselineQuestions:30,days:14,dayTabs:56,finalRounds:12,finalDomains:17,verified:['attempt gate','rubric unlock','persistence','CSV download','completion gate','retake schedule','quiz feedback','threshold arithmetic','token-cost arithmetic','capstone plugin scope','mock advancement','JSON export','mobile overflow','zero runtime errors'],testProgressCleared:true};
  } finally { await isolated.close(); }
}
