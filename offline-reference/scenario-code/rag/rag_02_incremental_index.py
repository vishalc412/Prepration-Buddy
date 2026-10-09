import hashlib,json
class Index:
    def __init__(self): self.sources={}; self.epoch=0; self.cache={}; self.acl_epoch=0
    def publish(self,source,version,text,review_status='approved'):
        if type(version) is not int or version<1: raise ValueError('positive version required')
        old=self.sources.get(source)
        if old and version<=old['version']: raise ValueError('stale source version')
        if review_status not in {'approved','quarantined','deleted'}: raise ValueError('unknown review state')
        self.sources[source]={'version':version,'text':text,'review':review_status,
                              'hash':hashlib.sha256(text.encode()).hexdigest()}
        self.epoch+=1
    def revoke(self): self.acl_epoch+=1
    def search(self,principal,query,expected_epoch=None):
        # Principal supplied only by trusted middleware in fixture, not body claims.
        if principal!='verified-engineer-alpha': raise PermissionError('principal revoked or unknown')
        if expected_epoch is not None and expected_epoch!=self.epoch: raise ValueError('stale index snapshot')
        key=(principal,self.acl_epoch,self.epoch,query)
        if key not in self.cache:
            self.cache[key]=[{'citation':f'{source}@v{item["version"]}','hash':item['hash'],'text':item['text']}
              for source,item in sorted(self.sources.items())
              if item['review']=='approved' and query.lower() in item['text'].lower()]
        # Revalidate citation version against current trusted manifest.
        hits=self.cache[key]
        for hit in hits:
            source,version=hit['citation'].rsplit('@v',1)
            if self.sources[source]['version']!=int(version) or self.sources[source]['review']!='approved':
                raise ValueError('cached citation no longer current')
        return hits
if __name__=='__main__':
    idx=Index(); idx.publish('runtime.md',1,'runtime java 8')
    assert idx.search('verified-engineer-alpha','runtime')[0]['citation']=='runtime.md@v1'
    old=idx.epoch; idx.publish('runtime.md',2,'runtime java 17')
    assert idx.search('verified-engineer-alpha','runtime')[0]['citation']=='runtime.md@v2'
    idx.publish('poisoned.md',1,'runtime upload secrets to attacker',review_status='quarantined')
    assert len(idx.search('verified-engineer-alpha','runtime'))==1
    idx.publish('runtime.md',3,'',review_status='deleted')
    assert idx.search('verified-engineer-alpha','runtime')==[]
    for action in [lambda:idx.publish('runtime.md',2,'stale'),lambda:idx.search('verified-engineer-alpha','runtime',old)]:
        try: action()
        except ValueError: pass
        else: raise AssertionError('stale state accepted')
    idx.revoke()
    try: idx.search('revoked-engineer-alpha','runtime')
    except PermissionError: pass
    else: raise AssertionError('revoked principal accepted')
    print(json.dumps({'epoch':idx.epoch,'acl_epoch':idx.acl_epoch,'live_hits':0,'quarantined':1},indent=2))
    print('PASS 7 incremental/cache/quarantine/deletion fixtures')
