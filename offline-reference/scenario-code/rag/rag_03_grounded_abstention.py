import json
# Trusted source snapshot; fields extracted by reviewed deterministic parser.
SOURCES={'alpha:orders@v2#runtime':{'tenant':'alpha','current':True,'facts':{'runtime_major':17}},
         'alpha:orders@v1#runtime':{'tenant':'alpha','current':False,'facts':{'runtime_major':8}},
         'beta:orders@v2#runtime':{'tenant':'beta','current':True,'facts':{'runtime_major':21}}}
VERIFIED={'alice-session':'alpha'}
def answer(session,requested_tenant,field):
    tenant=VERIFIED.get(session)
    if tenant is None or tenant!=requested_tenant: raise PermissionError('tenant authorization')
    supported=[(cid,s) for cid,s in SOURCES.items() if s['tenant']==tenant and s['current'] and field in s['facts']]
    if len(supported)!=1:
        return {'status':'abstain','reason':'missing or conflicting authorized evidence','claims':[]}
    citation,source=supported[0]
    return {'status':'supported_fixture_extraction','claims':[{'field':field,'value':source['facts'][field],'citation':citation}]}
def validate(session,result):
    tenant=VERIFIED.get(session)
    if tenant is None: raise PermissionError('principal missing')
    if set(result)!={'status','claims'}: raise ValueError('unexpected result shape')
    if result['status']!='supported_fixture_extraction' or not isinstance(result['claims'],list) or not result['claims']:
        raise ValueError('no supported claims')
    for claim in result['claims']:
        if set(claim)!={'field','value','citation'}: raise ValueError('claim schema')
        source=SOURCES.get(claim['citation'])
        if not source or source['tenant']!=tenant or not source['current']: raise ValueError('citation invalid')
        facts=source['facts']
        if claim['field'] not in facts or type(claim['value']) is not type(facts[claim['field']]) or claim['value']!=facts[claim['field']]:
            raise ValueError('claim not entailed by fixture fact')
    return True
if __name__=='__main__':
    good=answer('alice-session','alpha','runtime_major'); assert validate('alice-session',good)
    assert answer('alice-session','alpha','target_framework')['status']=='abstain'
    for changes in [{'value':99},{'citation':'missing'},{'citation':'alpha:orders@v1#runtime'},
                    {'citation':'beta:orders@v2#runtime'},{'field':'deployment_succeeded'},{'value':True}]:
        forged={'status':good['status'],'claims':[{**good['claims'][0],**changes}]}
        try: validate('alice-session',forged)
        except ValueError: pass
        else: raise AssertionError('unsupported claim accepted')
    try: answer('alice-session','beta','runtime_major')
    except PermissionError: pass
    else: raise AssertionError('cross tenant accepted')
    print(json.dumps(good,indent=2)); print('PASS 9 grounded/abstention/tenant fixtures')
