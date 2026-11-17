// Copyright © 2026 Christopher Snow
import fs from 'node:fs/promises';
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {esc,header,footer,renderHome,renderLesson} from './layout.mjs';
const course=JSON.parse(await fs.readFile('src/course.json','utf8'));
const {lessons,modules}=course;
await fs.rm('dist',{recursive:true,force:true});
await fs.mkdir('dist/lessons',{recursive:true});
execFileSync('python3',['scripts/execute.py'],{stdio:'inherit'});
const worked=JSON.parse(await fs.readFile('.cache/worked.json','utf8'));
// Content-addressed assets keep newly deployed markup and interaction code in sync.
const assets={};
for(const file of ['app.js','style.css','worker.js','editor.mjs','rich-text.mjs'])assets[file]=await fs.readFile('src/'+file,'utf8');
assets['worker.js']=assets['worker.js'].replace('const figureHelper = null;', 'const figureHelper = '+JSON.stringify(await fs.readFile('scripts/figure_style.py','utf8'))+';');
assets['style.css']+='\n'+await fs.readFile('src/quiet.css','utf8');
const version=createHash('sha256').update(Object.values(assets).join('\n')).digest('hex').slice(0,12);
for(const [file,content]of Object.entries(assets)){
 await fs.writeFile('dist/'+file,content);
 const dot=file.lastIndexOf('.');const name=file.slice(0,dot)+'.'+version+file.slice(dot);
 let published=content;
 for(const module of ['editor.mjs','rich-text.mjs'])published=published.replaceAll("'./"+module+"'","'./"+module.replace('.', '.'+version+'.')+"'");
 if(file==='app.js')published=published.replace("'worker.js'","'worker."+version+".js'");
 await fs.writeFile('dist/'+name,published);
}

await fs.mkdir('dist/vendor',{recursive:true});
for(const file of ['katex.mjs','katex.min.css'])await fs.copyFile('node_modules/katex/dist/'+file,'dist/vendor/'+file);
await fs.cp('node_modules/katex/dist/fonts','dist/vendor/fonts',{recursive:true});
await fs.copyFile('node_modules/katex/LICENSE','dist/vendor/KATEX-LICENSE.txt');
await fs.copyFile('src/course.json','dist/course.json');
await fs.cp('src/fonts','dist/fonts',{recursive:true});
await fs.cp('python','dist/python',{recursive:true});
await fs.writeFile('dist/worked-environment.json',JSON.stringify(worked.environment,null,2));
await fs.writeFile('dist/.nojekyll','');
await fs.writeFile('dist/favicon.svg','<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 36 36"><rect width="36" height="36" rx="10" fill="#315bf6"/><path d="m10 25 8-15 8 15M13 20h10" fill="none" stroke="white" stroke-width="2" stroke-linecap="round"/><circle cx="18" cy="10" r="3" fill="#a6c4ff"/></svg>');
const shell=(title,body,p='')=>`<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="color-scheme" content="light dark"><meta name="description" content="Learn causal inference through 18 short Python investigations. Explore observational comparisons, causal diagrams, adjustment and identification assumptions."><title>${esc(title)} · Causal Inference Lab</title><link rel="icon" href="${p}favicon.svg"><link rel="stylesheet" href="${p}vendor/katex.min.css"><link rel="stylesheet" href="${p}style.${version}.css"><script>try{document.documentElement.dataset.theme=localStorage.getItem('cil:theme')||'light'}catch{}</script><script type="module" src="${p}app.${version}.js"></script></head><body>${header(p)}${body}${footer(p)}</body></html>`;
await fs.writeFile('dist/index.html',shell('What would happen if we changed it?' ,renderHome(course)));
for(const [i,l]of lessons.entries()){
 const code=await fs.readFile('python/'+l.code,'utf8');
 const record=worked.lessons[l.slug];
 const figures=[];
 for(const [j,svg]of record.figures.entries()){
  const filename=l.slug+'-'+j+'.svg';await fs.writeFile('dist/lessons/'+filename,svg);
  const narrowFilename=l.slug+'-'+j+'-narrow.svg';await fs.writeFile('dist/lessons/'+narrowFilename,record.figures_narrow[j]);
  figures.push(`<figure class="worked-figure"><picture><source media="(max-width:700px)" srcset="${narrowFilename}"><img class="plot" src="${filename}" alt="${esc(l.plot)}" loading="lazy"></picture><figcaption><a href="${filename}" target="_blank" rel="noopener">Open full-size figure ↗</a></figcaption></figure>`);
 }
 const body=renderLesson({lesson:{...l,worked:record},index:i,lessons,modules,code,figures});
 await fs.writeFile('dist/lessons/'+l.slug+'.html',shell(l.title,body,'../'));
}
const notes=await fs.readFile('src/field-notes.html','utf8');
await fs.writeFile('dist/field-notes.html',shell('Field notes',notes));
execFileSync('python3',['scripts/prepare-runtime.py'],{stdio:'inherit'});
await fs.rm('.preview/causal-inference-lab',{recursive:true,force:true});
await fs.mkdir('.preview/causal-inference-lab',{recursive:true});
await fs.cp('dist','.preview/causal-inference-lab',{recursive:true});
console.log(`Built ${lessons.length} investigations, overview, field notes and a self-hosted stats runtime.`);
