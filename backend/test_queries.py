import urllib.request
import json

queries = {
    'A': 'Why did Line L3 miss its production target on August 4?',
    'B': 'What happened to machine M301 on August 4?',
    'C': 'Investigate the recurring temperature problems on M301.',
    'D': 'What should the supervisor do about the M301 overheating problem on August 4?',
    'E': 'Why did Line L3 have a high rejection rate on August 4?',
    'F': 'Investigate the production and quality problems on Line L3 on August 4.',
    'G': 'What was the exact financial cost of the M301 failure?',
    'H': 'Which operator was responsible for M301 during the overheating event?',
    'I': 'Why did Line L3 miss its production target on January 1, 2025?',
    'J': 'Why did Line L9 miss its production target on August 4?',
    'K': 'What is the weather today?'
}

base_url = 'http://127.0.0.1:8000/investigate'

print("=== RUNNING 11 TEST QUERY CASES ===\n")

for key, q in queries.items():
    data = json.dumps({'question': q}).encode('utf-8')
    req = urllib.request.Request(base_url, data=data, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as resp:
            r = json.loads(resp.read().decode())
            inv = r.get('investigation', {})
            print(f'[{key}] "{q}"')
            print(f'   => Status: {resp.status} SUCCESS')
            print(f'   => Scope: Line={inv.get("investigation_scope", {}).get("line")}, Date={inv.get("investigation_scope", {}).get("date")}')
            if inv.get('limitations'):
                print(f'   => Limitations: {inv.get("limitations")}')
            print()
    except urllib.error.HTTPError as e:
        err_body = json.loads(e.read().decode())
        print(f'[{key}] "{q}"')
        print(f'   => Status: {e.code} ({err_body.get("detail")})')
        print()
