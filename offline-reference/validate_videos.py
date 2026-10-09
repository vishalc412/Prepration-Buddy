"""Independent curated-video schema, provenance and offline embed checks.

python3 offline-reference/validate_videos.py [--html] [--self-test]
No remote requests, playback, package installation, models or browser storage.
Evidence checks establish source shape; human topic-fit review remains separate.
"""
from __future__ import annotations
import argparse
import copy
from collections import defaultdict
import datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent
YOUTUBE_HOSTS = {'www.youtube.com', 'youtube.com'}
# Extend only after reviewing the actual publisher/creator provenance.
FIRST_PARTY_HOSTS = YOUTUBE_HOSTS | {
    'youtu.be', 'www.3blue1brown.com', '3blue1brown.com', 'karpathy.ai',
    'www.andrewng.org', 'andrewng.org', 'www.deeplearning.ai', 'deeplearning.ai',
    'huggingface.co', 'www.pytorch.org', 'pytorch.org', 'docs.pytorch.org',
    'www.tensorflow.org', 'tensorflow.org', 'developers.google.com',
    'cloud.google.com', 'ai.google.dev', 'research.google', 'deepmind.google',
    'www.nvidia.com', 'nvidia.com', 'developer.nvidia.com', 'blogs.nvidia.com',
    'www.microsoft.com', 'microsoft.com', 'learn.microsoft.com',
    'www.openai.com', 'openai.com', 'developers.openai.com',
    'www.stanford.edu', 'stanford.edu', 'cs.stanford.edu', 'cs25.stanford.edu',
    'www.cs.cmu.edu', 'cs.cmu.edu', 'ocw.mit.edu', 'www.mit.edu',
    'www.fullstackdeeplearning.com', 'fullstackdeeplearning.com',
    'sebastianraschka.com', 'www.sebastianraschka.com', 'www.fast.ai', 'fast.ai',
    'course.fast.ai', 'www.langchain.com', 'langchain.com', 'academy.langchain.com',
    'modelcontextprotocol.io', 'www.anthropic.com', 'anthropic.com',
    'www.docker.com', 'docker.com', 'www.cncf.io', 'cncf.io',
    'kubernetes.io', 'www.spring.io', 'spring.io', 'aws.amazon.com',
    'www.javabrains.io', 'javabrains.io', 'arxiv.org',
    'www.freecodecamp.org', 'freecodecamp.org', 'statquest.org',
    'www.statquest.org', 'moderne.ai', 'www.moderne.ai',
    'cs336.stanford.edu', 'cs231n.stanford.edu',
    'www.cognitiverevolution.ai', 'community.deeplearning.ai',
    'www.pinecone.io', 'docs.weaviate.io', 'neo4j.com', 'genai.owasp.org',
}
FIRST_PARTY_GITHUB = {
    '/karpathy/nn-zero-to-hero', '/jbarrasa/goingmeta',
    '/OWASP-ASI/finbot-ctf-demo',
    '/pinecone-io/examples/blob/master/learn/search/semantic-search/cohere-rerank/compaq-reranking.ipynb',
}
FIRST_PARTY_LINKEDIN = {'/pulse/prompt-injection-owasp-top-10-llm-vandana-verma-hppcc'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def text(value, minimum, label):
    require(isinstance(value, str) and len(value.split()) >= minimum,
            f'{label}: at least {minimum} substantive words required')


def video_key(url):
    """Canonical destinations only; video identity is independent of title text."""
    require(isinstance(url, str), 'Video URL must be text')
    p = urlparse(url)
    require(p.scheme == 'https' and p.hostname in YOUTUBE_HOSTS
            and not p.username and not p.password and p.port in (None, 443)
            and not p.fragment, f'Not a direct canonical YouTube destination: {url}')
    q = parse_qs(p.query, keep_blank_values=True)
    if p.path == '/watch':
        require(set(q) == {'v'} and len(q['v']) == 1
                and re.fullmatch(r'[A-Za-z0-9_-]{11}', q['v'][0]) is not None,
                f'Video needs one exact 11-character watch ID: {url}')
        return 'video:' + q['v'][0]
    if p.path == '/playlist':
        require(set(q) == {'list'} and len(q['list']) == 1
                and re.fullmatch(r'PL[A-Za-z0-9_-]{16,98}', q['list'][0]) is not None,
                f'Playlist needs a concrete creator-published PL identifier: {url}')
        return 'playlist:' + q['list'][0]
    raise ValueError(f'Search, channel, short or embed URL is not a selected video: {url}')


def evidence(row, label):
    require(isinstance(row, dict), f'{label}: evidence object required')
    p = urlparse(row.get('url', ''))
    provenance = p.hostname in FIRST_PARTY_HOSTS or (
        p.hostname == 'github.com' and p.path.rstrip('/') in FIRST_PARTY_GITHUB) or (
        p.hostname == 'www.linkedin.com' and p.path.rstrip('/') in FIRST_PARTY_LINKEDIN)
    require(p.scheme == 'https' and provenance
            and not p.username and not p.password and p.port in (None, 443),
            f'{label}: publisher/creator evidence provenance needs review: {row.get("url")}')
    require('youtube.com/results' not in row.get('url', '') and 'google.com/search' not in row.get('url', ''),
            f'{label}: search results are not publication evidence')
    text(row.get('note'), 4, f'{label} evidence note')


def validate_rows(rows, merged=False):
    require(isinstance(rows, list) and rows, 'Nonempty video list required')
    seen = set()
    for row in rows:
        require(isinstance(row, dict), 'Video record must be an object')
        ident = row.get('id')
        require(isinstance(ident, str) and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{2,79}', ident)
                and ident not in seen, f'Video ID missing/unsafe/duplicated: {ident}')
        seen.add(ident)
        for field, minimum in [('title', 1), ('creator', 1), ('level', 1), ('format', 1),
                               ('why', 8), ('watchTask', 5), ('practiceTask', 5), ('caution', 4)]:
            text(row.get(field), minimum, f'{ident} {field}')
        require(row['level'] in {'foundation', 'intermediate', 'advanced'}, f'{ident}: level must match runtime filter options')
        video_key(row.get('url'))
        topics = row.get('topics')
        require(isinstance(topics, list) and topics
                and all(isinstance(t, str) and t.strip() for t in topics)
                and len(set(topics)) == len(topics), f'{ident}: distinct topic labels required')
        days = row.get('days')
        require(isinstance(days, list) and days
                and all(type(day) is int and 1 <= day <= 30 for day in days)
                and len(set(days)) == len(days), f'{ident}: unique course days 1–30 required')
        require(row['watchTask'].strip() != row['practiceTask'].strip(), f'{ident}: viewing and coding tasks must differ')
        require(isinstance(row.get('evidence'), list) and row['evidence'], f'{ident}: publication evidence missing')
        for e in row['evidence']:
            evidence(e, ident)
        verification = row.get('verification')
        require(verification == 'identity-and-topic', f'{ident}: verification must describe publication identity/topic only')
        require(row.get('titleKind') in (None, 'publisher-demo-label'), f'{ident}: unsupported title provenance')
        require(not any(re.search(r'(?:rating|quality.?score|star.?score|rank)', key, re.I) for key in row),
                f'{ident}: invented numeric quality field requires evidence')
        require(not re.search(r'\b(?:10|[0-9](?:\.\d+)?)\s*/\s*(?:5|10)\b',
                              row['why'] + ' ' + verification), f'{ident}: unsubstantiated video score')
        if merged:
            aliases = row.get('aliases', [])
            require(isinstance(aliases, list) and len(set(aliases)) == len(aliases)
                    and all(isinstance(a, str) and a and a != ident for a in aliases), f'{ident}: invalid merge aliases')
    if merged:
        aliases = [a for row in rows for a in row.get('aliases', [])]
        require(len(set(aliases)) == len(aliases) and not set(aliases) & seen,
                'Merge aliases duplicate or conflict with canonical video IDs')
        require(len({video_key(row['url']) for row in rows}) == len(rows), 'Merged catalog still has duplicate video/playlist destinations')
    return rows


def shard(name):
    data = json.loads((ROOT / name).read_text())
    return data['videos'] if isinstance(data, dict) else data


def check_merge(source, catalog):
    groups = defaultdict(list)
    for row in source:
        groups[video_key(row['url'])].append(row)
    require({video_key(r['url']) for r in catalog} == set(groups), 'Merged catalog omits/adds source destinations')
    for row in catalog:
        members = groups[video_key(row['url'])]
        require(row['id'] == members[0]['id'], f'{row["id"]}: merge must retain first authored ID')
        require(set(row.get('aliases', [])) == {m['id'] for m in members[1:]}, f'{row["id"]}: duplicate URL aliases missing')
        for field in ('topics', 'days'):
            require(set(row[field]) == {v for m in members for v in m[field]}, f'{row["id"]}: merge loses {field}')
        expected = {json.dumps(e, sort_keys=True) for m in members for e in m['evidence']}
        actual = {json.dumps(e, sort_keys=True) for e in row['evidence']}
        require(actual == expected, f'{row["id"]}: merge loses or invents evidence')
        # Keep the first publication's exact title/creator/task descriptions; a
        # conflicting duplicate title or publisher needs manual adjudication.
        for field in ('title', 'creator', 'why', 'watchTask', 'practiceTask', 'caution', 'verification', 'level', 'format'):
            require(row[field] == members[0][field], f'{row["id"]}: unexplained merge change in {field}')
        require(row.get('titleKind') == members[0].get('titleKind'), f'{row["id"]}: merge loses title provenance')


def audit(html=False):
    source = shard('video-foundations.json') + shard('video-advanced.json')
    validate_rows(source)
    groups = defaultdict(list)
    for row in source:
        groups[video_key(row['url'])].append(row['id'])
    report = {'status': 'PASS', 'authored_rows': len(source), 'unique_destinations': len(groups),
              'duplicate_groups': [ids for ids in groups.values() if len(ids) > 1],
              'mapped_days': sorted({day for row in source for day in row['days']}),
              'limits': ['Publication identity/topic evidence does not certify playback availability or teaching quality.',
                         'No video was played, embedded, downloaded or automatically scored.',
                         'The local tutorial remains usable without following optional online links.']}
    require(report['mapped_days'] == list(range(1, 31)), 'Curated source catalog must cover all 30 course days')
    if html:
        page = (ROOT.parent / 'index.html').read_text()
        embedded, _ = json.JSONDecoder().raw_decode(page.split('const OFFLINE = ', 1)[1])
        data = embedded.get('videos')
        require(isinstance(data, dict), 'Embedded video catalog must be an object')
        datetime.date.fromisoformat(data.get('verifiedOn', ''))
        catalog = validate_rows(data.get('videos'), merged=True)
        check_merge(source, catalog)
        runtime = (ROOT / 'video-studio.js').read_text()
        require(runtime.strip() in page, 'Video runtime differs from source')
        require(not re.search(r'\b(?:fetch|WebSocket|EventSource)\s*\(|XMLHttpRequest|<iframe', runtime),
                'Curated runtime requires external content/network execution')
        # Inert regexes strip older search links. Test rendered anchors instead
        # of treating those source literals as active destinations.
        report['rendered_guidance'] = rendered_checks(embedded)
        report.update(embedded_parity='PASS', merged_videos=len(catalog),
                      artifact_sha256=hashlib.sha256(page.encode()).hexdigest(), artifact_bytes=len(page.encode()))
    return report


def rendered_checks(embedded):
    payload = {'data': embedded, 'scripts': [(ROOT / name).read_text()
               for name in ['jd-studio.js', 'practical-studio.js', 'video-studio.js']]}
    script = r"""
const fs=require('node:fs'),vm=require('node:vm');const input=JSON.parse(fs.readFileSync(0,'utf8'));
const esc=v=>String(v??'').replace(/[&<>"']/g,x=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[x]));
const ctx={OFFLINE:input.data,NAV:[],state:{notes:{},answers:{},code:{},evidence:{},day:1},esc,
 list:xs=>'<ul>'+xs.map(x=>'<li>'+esc(x)+'</li>').join('')+'</ul>',heading:()=>'',studyMode:()=>true,
 overviewView:()=>'<div class="cockpit-lanes">',teacherView:()=>'',render:()=>{},go:()=>{},save:()=>{},
 document:{addEventListener:()=>{},getElementById:()=>null,querySelector:()=>null},
 TextEncoder,DataView,Uint8Array,Blob,URL,setTimeout:()=>{}};
vm.createContext(ctx);for(const source of input.scripts)vm.runInContext(source,ctx,{timeout:1000});
let panels=0,links=0;const missing=[];
function check(html,label,focused=true){if(typeof html!=='string')throw Error(label+' did not render');
 const urls=[...html.matchAll(/<a\b[^>]*\bhref="([^"]+)"/g)].map(x=>x[1]);
 if(urls.some(u=>u.includes('youtube.com/results')))throw Error(label+' retains active search anchor');
 if(/<iframe|<img[^>]+(?:youtube|ytimg)/i.test(html))throw Error(label+' embeds remote video/media');
 links+=urls.length;panels++;if(focused&&!html.includes('Watch selected tutorial')&&!html.includes('Open selected playlist'))missing.push(label);}
for(const day of input.data.lessons)for(const mod of day.modules)check(ctx.learningLinks(day.day,null,mod.title),'day'+day.day+': '+mod.title);
for(const q of input.data.client)check(ctx.clientSources(q),q.id);
for(const q of input.data.jd){ctx.state.notes['jd-selected']=q.id;check(ctx.jdView(),q.id)}
for(const c of input.data.cases)check(ctx.practicalCase(c),c.id);
for(const track of ['Python','Async Python','FastAPI','Django','Flask','RAG','Agents','Evaluation'])check(ctx.learningLinks(1,track),track);
for(const v of input.data.videos.videos)if(v.titleKind==='publisher-demo-label'){
 const card=ctx.tutorialCard(v);if(!/publisher[^<]*label/i.test(card))throw Error(v.id+' omits publisher-label disclosure');}
let compact=0;
for(const day of input.data.lessons)for(const mod of day.modules){
 const card=ctx.teacherTutorialLinks(day.day,null,mod.title);
 const urls=[...card.matchAll(/<a\b[^>]*\bhref="([^"]+)"/g)].map(x=>x[1]);
 if(urls.length!==1||!input.data.videos.videos.some(v=>v.url===urls[0]))throw Error('Compact guidance lacks selected destination: '+mod.title);
 if(/<iframe|youtube\.com\/results/i.test(card))throw Error('Compact guidance embeds/searches remote video');compact++;}
check(ctx.tutorialLibrary(),'library',false);
process.stdout.write(JSON.stringify({status:'PASS',panels,anchors:links,unfocused:missing,compact_guidance:compact,
 boundary:'actual guidance/card/JD/case source rendered in isolated Node; no browser/learner storage'}));
"""
    result = subprocess.run(['node', '-e', script], input=json.dumps(payload),
                            capture_output=True, text=True, timeout=20, check=True)
    return json.loads(result.stdout)


def self_test():
    # Boundary cases test meaningful URL identity, domain and playlist contracts.
    assert video_key('https://www.youtube.com/watch?v=abcdefgh_-1') == 'video:abcdefgh_-1'
    assert video_key('https://youtube.com/playlist?list=PLabcdefghij0123456789') == 'playlist:PLabcdefghij0123456789'
    invalid = ['http://youtube.com/watch?v=abcdefgh_-1', 'https://youtube.com/results?search_query=Mamba',
               'https://youtube.com/watch?v=short', 'https://youtube.com/watch?v=abcdefgh_-1&v=abcdefgh_-1',
               'https://youtube.com/watch?v=abcdefgh_-1&list=PLabcdefghij0123456789',
               'https://youtube.com.evil.example/watch?v=abcdefgh_-1', 'https://youtube.com/@publisher',
               'https://youtube.com/embed/abcdefgh_-1', 'https://youtube.com/playlist?list=',
               'https://youtube.com/playlist?list=generic', 'https://user@youtube.com/watch?v=abcdefgh_-1']
    for url in invalid:
        try:
            video_key(url)
        except ValueError:
            pass
        else:
            raise AssertionError(f'Invalid destination accepted: {url}')
    base = {'id': 'video-one', 'url': 'https://www.youtube.com/watch?v=abcdefgh_-1',
            'title': 'Specific published lesson', 'creator': 'Publisher', 'topics': ['python'], 'days': [1],
            'level': 'foundation', 'format': 'lecture',
            'why': 'This explains the precise generator mechanism needed for streaming records.',
            'watchTask': 'Trace one suspended generator and its next yielded record.',
            'practiceTask': 'Write a bounded generator and assert its incremental consumption.',
            'caution': 'Publication identity verified; playback and every code line remain untested.',
            'evidence': [{'url': 'https://www.youtube.com/watch?v=abcdefgh_-1', 'note': 'Publisher page identifies the lesson and creator.'}],
            'verification': 'identity-and-topic'}
    validate_rows([base])
    second = copy.deepcopy(base)
    second.update(id='video-two', topics=['async'], days=[2])
    merged = copy.deepcopy(base)
    merged.update(aliases=['video-two'], topics=['python', 'async'], days=[1, 2])
    validate_rows([merged], merged=True)
    check_merge([base, second], [merged])
    negative = 0
    for field, bad in [('topics', ['python']), ('days', [1]), ('aliases', []), ('evidence', [])]:
        broken = copy.deepcopy(merged)
        broken[field] = bad
        try:
            check_merge([base, second], [broken])
        except ValueError:
            negative += 1
        else:
            raise AssertionError(f'Merge silently lost {field}')
    for field, bad in [('days', [True]), ('verification', 'perfect'), ('evidence', [])]:
        broken = copy.deepcopy(base)
        broken[field] = bad
        try:
            validate_rows([broken])
        except ValueError:
            negative += 1
        else:
            raise AssertionError(f'Invalid metadata accepted: {field}')
    return {'status': 'PASS', 'URL_boundary_tests': len(invalid) + 2,
            'merge_and_metadata_negative_tests': negative}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--html', action='store_true')
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    try:
        print(json.dumps(self_test() if args.self_test else audit(args.html), indent=2))
    except (ValueError, KeyError, TypeError, OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
        print(json.dumps({'status': 'FAIL', 'error': str(error)}, indent=2))
        raise SystemExit(1)
