async (existingPage) => {
  const isolated=await existingPage.context().browser().newContext({viewport:{width:1440,height:1000}});
  const page=await isolated.newPage();
  await page.goto('http://127.0.0.1:8987/index.html');
  try {
  const check=(ok,msg)=>{if(!ok)throw Error(msg)};
  await page.setViewportSize({width:1440,height:1000});
  await page.evaluate(()=>{state=fresh();save();render()});
  const backup=await page.evaluate(()=>{
    const s=fresh();s.answers.b1='Backup restore proof';s.ratings.b1=2;s.code['java-12']='class Fixture {}';s.notes['quiz-1']='1';s.notes['teacher-stage-1']='2';s.notes['module-quiz-1-0']='1';s.dayScores[1]={Python:75};return s;
  });
  page.once('dialog',d=>d.accept());
  await page.locator('#import-file').setInputFiles({name:'progress.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(backup))});
  await page.getByRole('button',{name:'03 Baseline assessment'}).click();
  check(await page.getByLabel('Your answer / reasoning / code').inputValue()==='Backup restore proof','Import did not restore answer');
  await page.reload();
  check(await page.evaluate(()=>state.ratings.b1===2&&state.code['java-12']==='class Fixture {}'&&state.dayScores[1].Python===75&&state.notes['teacher-stage-1']==='2'&&state.notes['module-quiz-1-0']==='1'),'Import persistence failed');
  const before=await page.evaluate(()=>JSON.stringify(state));
  await page.locator('#import-file').setInputFiles({name:'bad.json',mimeType:'application/json',buffer:Buffer.from('{"version":1,"dayScores":{"1":"invalid"}}')});
  check((await page.locator('#toast').innerText()).includes('Import failed'),'Malformed import accepted');
  check(await page.evaluate(()=>JSON.stringify(state))===before,'Malformed import altered progress');
  await page.locator('#import-file').setInputFiles({name:'bad-json.json',mimeType:'application/json',buffer:Buffer.from('{oops')});
  check((await page.locator('#toast').innerText()).includes('Import failed'),'Broken JSON accepted');
  await page.evaluate(()=>{state=fresh();save();render()});
  await page.getByRole('button',{name:'02 14-day roadmap'}).click();
  check(await page.locator('.day-card').count()===14,'Roadmap day count');
  await page.getByLabel('Search skills').fill('Python');
  check(await page.locator('tbody tr').count()>0,'Matrix search failed');
  await page.getByLabel('Priority group').selectOption('A');
  check((await page.locator('tbody').innerText()).includes('Python'),'Matrix priority filter failed');
  await page.locator('#nav [data-view=resources]').click();
  check(await page.getByText('Current .NET modernization guidance',{exact:true}).isVisible(),'Updated research missing');
  check(await page.getByRole('link',{name:'Microsoft: Upgrade Assistant deprecation and current path ↗'}).count()>0,'Current .NET source missing');
  await page.evaluate(()=>{state=fresh();save();render()});
  await page.getByRole('button',{name:'01 Overview'}).click();
  await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
  await page.screenshot({path:'output/playwright/desktop.png'});
  return {status:'PASS',verified:['progress import','restored persistence','malformed schema rejected without mutation','broken JSON rejected','matrix search/filter','current research reference'],testContext:'isolated; existing browser storage untouched'};
  } finally { await isolated.close(); }
}
