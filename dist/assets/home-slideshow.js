(() => {
 const carousel=document.querySelector('.microscopy-slideshow');if(!carousel)return;
 const zh=document.documentElement.lang.startsWith('zh');
 const track=carousel.querySelector('.slideshow-track'),slides=[...carousel.querySelectorAll('.slideshow-slide')],dots=[...carousel.querySelectorAll('[data-slide]')],pause=carousel.querySelector('.slideshow-pause');
 const reduced=window.matchMedia('(prefers-reduced-motion: reduce)');
 let index=0,paused=reduced.matches,timer=null,hover=false,startX=null;
 carousel.setAttribute('aria-label',zh?'科研显微图像':'Research microscopy images');
 carousel.querySelector('.slideshow-prev').setAttribute('aria-label',zh?'上一张图像':'Previous image');
 carousel.querySelector('.slideshow-next').setAttribute('aria-label',zh?'下一张图像':'Next image');
 slides.forEach((s,i)=>{s.setAttribute('aria-label',zh?`第 ${i+1} 张，共 ${slides.length} 张`:`${i+1} of ${slides.length}`);s.querySelector('img').alt=zh?`科研显微图像 ${i+1}`:`Microscopy research image ${i+1}`;dots[i].setAttribute('aria-label',zh?`显示第 ${i+1} 张图像`:`Show image ${i+1}`);});
 function draw(){track.style.transform=`translateX(-${index*100}%)`;slides.forEach((s,i)=>s.setAttribute('aria-hidden',String(i!==index)));dots.forEach((d,i)=>d.setAttribute('aria-pressed',String(i===index)));pause.textContent=paused?(zh?'播放':'Play'):(zh?'暂停':'Pause');pause.setAttribute('aria-label',paused?(zh?'播放幻灯片':'Play slideshow'):(zh?'暂停幻灯片':'Pause slideshow'));}
 function schedule(){clearInterval(timer);timer=null;if(!paused&&!hover&&!document.hidden)timer=setInterval(()=>{index=(index+1)%slides.length;draw();},3000);}
 function go(n,manual=true){index=(n+slides.length)%slides.length;if(manual)paused=true;draw();schedule();}
 carousel.querySelector('.slideshow-prev').onclick=()=>go(index-1);carousel.querySelector('.slideshow-next').onclick=()=>go(index+1);
 dots.forEach((d,i)=>d.onclick=()=>go(i));pause.onclick=()=>{paused=!paused;draw();schedule();};
 carousel.addEventListener('mouseenter',()=>{hover=true;schedule();});carousel.addEventListener('mouseleave',()=>{hover=false;schedule();});
 carousel.addEventListener('focusin',()=>{paused=true;draw();schedule();});
 carousel.addEventListener('keydown',e=>{if(e.key==='ArrowLeft'||e.key==='ArrowRight'){e.preventDefault();go(index+(e.key==='ArrowRight'?1:-1));}});
 const view=carousel.querySelector('.slideshow-window');view.addEventListener('pointerdown',e=>{startX=e.clientX;});view.addEventListener('pointerup',e=>{if(startX!==null&&Math.abs(e.clientX-startX)>40)go(index+(e.clientX<startX?1:-1));startX=null;});view.addEventListener('pointercancel',()=>startX=null);
 document.addEventListener('visibilitychange',schedule);reduced.addEventListener('change',()=>{if(reduced.matches){paused=true;draw();schedule();}});
 draw();schedule();
})();
