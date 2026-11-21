const cl=(v,a=0,b=1)=>Math.max(a,Math.min(b,v));
const p=(t,a,d)=>cl((t-a)/d);
const eOut=x=>1-Math.pow(1-x,3);
const eIn=x=>x*x*x;
const eIO=x=>x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2;
const eBack=x=>{const c1=1.70158,c3=c1+1;return 1+c3*Math.pow(x-1,3)+c1*Math.pow(x-1,2);};
const $=id=>document.getElementById(id);
function tf(el,{x=0,y=0,s=1,r=0,o=1}={}){if(typeof el==='string')el=$(el);el.style.transform=`translate(${x}px,${y}px) scale(${s}) rotate(${r}deg)`;el.style.opacity=o;}
function rise(id,lt,a,d=.4,dist=120){const k=eOut(p(lt,a,d));tf(id,{y:(1-k)*dist,o:k});}
function slide(id,lt,a,d=.45,dx=-300){const k=eOut(p(lt,a,d));tf(id,{x:(1-k)*dx,o:k});}
function pop(id,lt,a,d=.5,r0=0){const k=p(lt,a,d);const e=eBack(k);tf(id,{s:k===0?.001:e,r:(1-e)*r0,o:cl(k*3)});}
function slam(id,lt,a,d=.3,r=0){const k=p(lt,a,d);tf(id,{s:k===0?.001:1+(1-eOut(k))*1.5,r:r,o:cl(k*3)});}
function fade(id,lt,a,d=.4){$(id).style.opacity=p(lt,a,d);}
function typeText(id,full,lt,a,d){const n=Math.round(cl((lt-a)/d)*full.length);$(id).textContent=full.slice(0,n);}
function count(id,to,lt,a,d,fmt=v=>Math.round(v)){$(id).textContent=fmt(to*eOut(p(lt,a,d)));}
function scenes(t,S,mode='rise'){S.forEach(([a,b],i)=>{const el=$('s'+(i+1));if(!el)return;const vis=(t>=a-0.201)&&(t<=b+0.001);if(!vis){el.style.opacity=0;return;}
 const e=i===0?1:eOut(p(t,a-0.2,0.35));const x=(i<S.length-1)?eIn(p(t,b-0.22,0.22)):0;let tr='',o=e*(1-x);
 if(mode==='rise')tr=`translateY(${(1-e)*60-x*80}px)`;
 if(mode==='slide'){tr=`translateX(${(1-e)*1080-x*1080}px)`;o=1;}
 if(mode==='zoom')tr=`scale(${0.85+0.15*e+x*0.3})`;
 if(mode==='flash')tr=`scale(${1+(1-e)*0.1}) skewX(${(1-e)*-8}deg)`;
 if(mode==='drop')tr=`translateY(${(1-e)*-200+x*200}px)`;
 el.style.opacity=o;el.style.transform=tr;});}
function L(t,S,k){return k===0?t:t-S[k][0]+0.25;}
function showCover(){document.querySelectorAll('.scene').forEach(e=>e.style.opacity=0);const c=$('cover');if(c){c.style.opacity=1;c.style.display='block';}}
// SFX em tempo local de cena: [cena(0..), t_local, tipo, ganho, param]; transições automáticas
function mkSFX(S,list,trans='swipe'){const o=[];S.forEach(([a,b],i)=>{if(i<S.length-1)o.push([b-0.22,trans,0.35]);});
 list.forEach(([k,lt,...r])=>o.push([k===0?lt:S[k][0]+lt-0.25,...r]));return o;}
