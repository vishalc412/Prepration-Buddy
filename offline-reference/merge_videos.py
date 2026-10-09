"""Merge reviewed tutorial selections without losing duplicate provenance.

This does not verify video playback, infer topic coverage or invent metadata.
Run before embed_content.py after updating either authored research shard.
"""
from copy import deepcopy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
shards = [json.loads((ROOT / name).read_text()) for name in
          ('video-foundations.json', 'video-advanced.json')]
rows = [row for shard in shards for row in shard['videos']]
assert len({row['id'] for row in rows}) == len(rows), 'Authored IDs must be globally unique'
merged = {}
for row in rows:
    if row['url'] not in merged:
        merged[row['url']] = deepcopy(row)
        merged[row['url']]['aliases'] = []
        continue
    target = merged[row['url']]
    target['aliases'].append(row['id'])
    for field in ('topics', 'days', 'evidence'):
        for value in row[field]:
            if value not in target[field]:
                target[field].append(deepcopy(value))
catalog = {'verifiedOn': max(shard['verifiedOn'] for shard in shards),
           'videos': list(merged.values())}
(ROOT / 'video-catalog.json').write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + '\n')
print(f"Merged {len(rows)} authored selections into {len(merged)} distinct tutorials.")
