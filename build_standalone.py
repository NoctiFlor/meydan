from pathlib import Path
import re,json,base64
root=Path(__file__).parent;dist=root/'dist'
def bundle(name,ns,remap={}):
 s=(dist/'vendor'/name).read_text(encoding='utf-8');exports=[]
 def exp(m):
  for item in m.group(1).split(','):
   parts=re.split(r'\s+as\s+',item.strip())
   if parts[0]:exports.append((parts[-1],parts[0]))
  return ''
 s=re.sub(r'export\s*\{([\s\S]*?)\};?',exp,s)
 for name in re.findall(r'export function (\w+)',s):exports.append((name,name))
 s=s.replace('export function ','function ')
 if 'export class SoftwareRenderer' in s:s=s.replace('export class SoftwareRenderer','class SoftwareRenderer');exports.append(('SoftwareRenderer','SoftwareRenderer'))
 def imp(m):
  members,source=m.groups();target='THREE' if source=='three' else remap[source]
  if members.startswith('* as '):return 'const '+members[5:]+'='+target+';'
  return 'const {'+re.sub(r'\s+as\s+',':',members[1:-1])+'}='+target+';'
 s=re.sub(r'import\s+(\{[\s\S]*?\}|\* as \w+)\s+from\s+[\'\"]([^\'\"]+)[\'\"];',imp,s)
 return 'const '+ns+'=(()=>{\n'+s+'\nreturn {'+','.join(a+':'+b for a,b in exports)+'};})();\n'
js=bundle('three.module.js','THREE')+bundle('BufferGeometryUtils.js','BufferUtils')+bundle('GLTFLoader.js','GLTFTools',{'./BufferGeometryUtils.js':'BufferUtils'})+bundle('OrbitControls.js','OrbitTools')+bundle('SkeletonUtils.js','SkeletonTools')+bundle('SoftwareRenderer.js','SoftTools')
js+=(dist/'gameplay.js').read_text(encoding='utf-8')+'\n'
game=(dist/'game.js').read_text(encoding='utf-8');game=re.sub(r'^import .*?;\n','',game,flags=re.M);js+='const {GLTFLoader}=GLTFTools;const {OrbitControls}=OrbitTools;const {clone,retargetClip}=SkeletonTools;const {SoftwareRenderer}=SoftTools;\n'+game
assets={p.name:base64.b64encode(p.read_bytes()).decode() for p in (dist/'assets').glob('*.glb')}
beatmaps={p.stem:json.loads(p.read_text(encoding='utf-8')) for p in (dist/'beatmaps').glob('*.json')}
html=(root/'shell.html').read_text(encoding='utf-8').replace('<script type="module" src="./game.js"></script>','<script>window.EMBEDDED_ASSETS='+json.dumps(assets)+';window.EMBEDDED_BEATMAPS='+json.dumps(beatmaps)+';</script><script>\n'+js.replace('</script','<\\/script')+'\n</script>')
(dist/'index.html').write_text(html,encoding='utf-8');(root/'MEYDAN.html').write_text(html,encoding='utf-8');print('Standalone HTML:',len(html),'bytes')
