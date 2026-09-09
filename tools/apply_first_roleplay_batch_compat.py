from pathlib import Path

p=Path('tools/apply_first_roleplay_batch.py')
s=p.read_text(encoding='utf-8')
# Keep the earlier search-response correlation patch intact while applying batch one.
s=s.replace('private void sendSearchDoc(FirebaseUser me,DocumentSnapshot d){','private void sendSearchDoc(FirebaseUser me,DocumentSnapshot d,String q){')
s=s.replace('private void sendSearchResult(FirebaseUser me,QuerySnapshot snap){','private void sendSearchResult(FirebaseUser me,QuerySnapshot snap,String q){')
s=s.replace('out.put(\"action\",\"search\");','out.put(\"action\",\"search\");out.put(\"query\",q);')
s=s.replace('sendSearchDoc(me,snap.getDocuments().get(0))','sendSearchDoc(me,snap.getDocuments().get(0),q)')
exec(compile(s,str(p),'exec'),{})
print('Applied first roleplay batch with search-correlation compatibility')
