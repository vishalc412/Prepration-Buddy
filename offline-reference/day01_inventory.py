from __future__ import annotations
import csv, json, math, os, re, statistics, sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator
FIELDS = ('repo_id','tenant_id','language','runtime_major','dependency_count','critical_cves','build_minutes','observed_at')
@dataclass(frozen=True)
class Row:
    repo_id: str
    tenant_id: str
    language: str
    runtime_major: int
    dependency_count: int
    critical_cves: int
    build_minutes: float
    observed_at: datetime

def integer(value: str, minimum: int) -> int:
    if not re.fullmatch(r'[0-9]+', value):
        raise ValueError('integer required')
    result = int(value)
    if result < minimum or result > 2**31-1:
        raise ValueError('integer outside supported range')
    return result

def normalize(raw: dict[str,str]) -> Row:
    values = {k: (raw.get(k) or '').strip() for k in FIELDS}
    if any(not v for v in values.values()):
        raise ValueError('required field missing')
    if values['language'] not in {'java','dotnet'}:
        raise ValueError('unsupported language')
    duration = float(values['build_minutes'])
    if not math.isfinite(duration) or duration < 0:
        raise ValueError('build duration must be finite and nonnegative')
    observed = datetime.fromisoformat(values['observed_at'].replace('Z','+00:00'))
    if observed.tzinfo is None:
        raise ValueError('timestamp must include timezone')
    return Row(values['repo_id'], values['tenant_id'], values['language'],
               integer(values['runtime_major'],1), integer(values['dependency_count'],0),
               integer(values['critical_cves'],0), duration, observed.astimezone(timezone.utc))

def ingest(path: Path) -> Iterator[tuple[int,Row|None,str|None]]:
    with path.open(newline='', encoding='utf-8') as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            return
        if set(FIELDS)-set(reader.fieldnames):
            raise ValueError('CSV header missing required columns')
        for line, raw in enumerate(reader,2):
            try:
                if None in raw:
                    raise ValueError('extra CSV fields')
                yield line, normalize(raw), None
            except (ValueError,TypeError,OverflowError) as exc:
                yield line, None, str(exc)

def report(path: Path) -> dict:
    latest: dict[tuple[str,str], tuple[int,Row]] = {}
    invalid, superseded = [], []
    total = valid = 0
    for line, row, error in ingest(path):
        total += 1
        if row is None:
            invalid.append({'line':line,'reason':error}); continue
        valid += 1
        key = (row.tenant_id,row.repo_id)
        previous = latest.get(key)
        if previous is None:
            latest[key]=(line,row)
        elif row.observed_at > previous[1].observed_at:
            superseded.append({'line':previous[0],'retained_line':line})
            latest[key]=(line,row)
        else:
            superseded.append({'line':line,'retained_line':previous[0]})
    rows = [r for _,r in latest.values()]
    summary = {}
    for tenant in sorted({r.tenant_id for r in rows}):
        durations = [r.build_minutes for r in rows if r.tenant_id==tenant]
        summary[tenant]={'count':len(durations),'mean':statistics.mean(durations),
                         'median':statistics.median(durations)}
    assert total == valid + len(invalid)
    assert valid == len(rows) + len(superseded)
    normalized=[]
    for row in rows:
        item=asdict(row); item['observed_at']=row.observed_at.isoformat()
        normalized.append(item)
    return {'counts':{'total':total,'valid':valid,'invalid':len(invalid),
                      'retained':len(rows),'superseded':len(superseded)},
            'invalid':invalid,'superseded':superseded,'tenants':summary,'rows':normalized}

def optional_parity(result: dict) -> None:
    import numpy as np
    import pandas as pd
    frame=pd.DataFrame(result['rows'])
    if frame.empty: return
    for tenant, expected in result['tenants'].items():
        values=frame.loc[frame.tenant_id==tenant,'build_minutes'].to_numpy()
        assert math.isclose(float(np.mean(values)),expected['mean'])
    grouped=frame.groupby('tenant_id').build_minutes.agg(['size','mean','median'])
    for tenant, expected in result['tenants'].items():
        assert int(grouped.loc[tenant,'size'])==expected['count']
        assert math.isclose(float(grouped.loc[tenant,'median']),expected['median'])

if __name__=='__main__':
    if len(sys.argv)!=3: raise SystemExit('usage: python day01_inventory.py inventory.csv report.json')
    source=Path(sys.argv[1]); destination=Path(sys.argv[2])
    if source.resolve()==destination.resolve(): raise SystemExit('output must differ from input')
    result=report(source)
    tmp=destination.with_suffix(destination.suffix+'.tmp')
    tmp.write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf-8')
    os.replace(tmp,destination)
    print(json.dumps(result['counts']))
