"""ProofDelta: deterministic, silent illustrated product walkthrough.
Run from repository root: python launch/render_demo.py
Requires Pillow, ffmpeg, pdftoppm; uses only the fictional sample PDFs.
Art direction: ink-and-paper inspection desk. Cream paper, dark ink, vermilion
changes, teal decisions. One comparison per beat, short linear reveals,
static reading holds, hard cuts. No bounce, invented UI screenshots or music.
Output: 1280x720, 24 fps, 42 seconds, H.264/yuv420p. Not a screen recording.
"""
from pathlib import Path
import json, subprocess, math
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'tmp'/'launch'; OUT.mkdir(parents=True,exist_ok=True)
W,H,FPS,DURATION=1280,720,24,42
INK='#142C2B'; PAPER='#F4F0E7'; MUTED='#52645F'; RED='#A94230'; TEAL='#146D60'; LINE='#D4D7CB'
FONT=Path('/usr/share/fonts/truetype/dejavu')
def font(size,bold=False): return ImageFont.truetype(str(FONT/('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf')),size)
F={s:font(s) for s in [19,22,24,28,32,38,44,52,68,94]}; B={s:font(s,True) for s in [22,24,28,32,38,44,52,68,94]}
SCENES=[(0,4,'A tiny change. A closer look.'),(4,10,'Start with two PDFs.'),(10,17,'Catch the weight change.'),(17,23,'Keep the ingredient context.'),(23,30,'Work through every difference.'),(30,36,'Preview the checkout.'),(36,42,'Take the review with you.')]
(OUT/'timeline.json').write_text(json.dumps({'fps':FPS,'duration':DURATION,'silent':True,'format':'illustrated workflow, not screen recording','scenes':SCENES},indent=2))
for name in ['approved','printer']:
    dest=OUT/name
    if not dest.with_suffix('.png').exists(): subprocess.run(['pdftoppm','-f','1','-singlefile','-scale-to','900','-png',str(ROOT/'dist'/'samples'/f'{name}-oat-bites.pdf'),str(dest)],check=True)
PDFS={name:Image.open(OUT/f'{name}.png').convert('RGB') for name in ['approved','printer']}
def txt(d,xy,s,size=28,color=INK,bold=False):
    face=(B if bold else F)[size]
    if d.textbbox((0,0),s,font=face)[2]>W-xy[0]-54: raise ValueError('Text overflow: '+s)
    d.text(xy,s,font=face,fill=color)
def line(d,xy,fill=LINE,width=2): d.line(xy,fill=fill,width=width)
def sheet(d,x,y,w,h):
    d.rectangle((x+12,y+12,x+w+12,y+h+12),fill='#DDDCD2')
    d.rectangle((x,y,x+w,y+h),fill='#FFFEF9',outline=LINE,width=2)
def frame(n):
    t=n/FPS; idx=next(i for i,(a,b,_) in enumerate(SCENES) if a<=t<b); a,b,title=SCENES[idx]; local=t-a
    im=Image.new('RGB',(W,H),PAPER); d=ImageDraw.Draw(im)
    txt(d,(54,30),'ProofDelta',28,bold=True)
    txt(d,(690,35),'ILLUSTRATED DEMO  /  FICTIONAL FILES',19,MUTED)
    line(d,(54,82,1226,82))
    txt(d,(54,112),title,44,bold=True)
    txt(d,(54,655),'Selectable text only. Human review required.',22,MUTED)
    txt(d,(1040,655),f'{idx+1:02d} / 07',22,MUTED)
    if idx==0:
        txt(d,(56,212),'APPROVED',22,MUTED); txt(d,(682,212),'PRINTER’S PROOF',22,MUTED)
        txt(d,(54,265),'180 g',94,bold=True)
        if local>0.6:
            txt(d,(680,265),'160 g',94,RED,True)
            line(d,(680,390,1010,390),RED,6)
        txt(d,(56,470),'Packaging proof text comparison.',38)
        txt(d,(56,535),'Your PDFs are processed in your browser.',28,MUTED)
    elif idx==1:
        for x,name,label in [(150,'approved','Approved original'),(740,'printer','Printer’s proof')]:
            doc=PDFS[name].copy(); doc.thumbnail((330,405)); im.paste(doc,(x,206))
            d.rectangle((x,206,x+doc.width,206+doc.height),outline=LINE,width=2)
            txt(d,(x,168),label,24,bold=True)
        txt(d,(500,376),'COMPARE',22,TEAL,True)
        txt(d,(460,420),'2 pages each',22,MUTED)
    elif idx==2:
        txt(d,(56,178),'CHANGE 1 OF 3   ·   SOURCE PAGE 1',22,TEAL,True)
        for x,label,value,col in [(54,'APPROVED ORIGINAL','180 g',INK),(682,'PRINTER’S PROOF','160 g',RED)]:
            sheet(d,x,234,532,270);txt(d,(x+26,258),label,22,MUTED)
            txt(d,(x+26,310),'Net weight',28);txt(d,(x+26,365),value,68,col,True)
        txt(d,(54,551),'Compare the changed line in its page context.',28)
    elif idx==3:
        txt(d,(54,181),'CHANGE 2 OF 3   ·   SOURCE PAGE 1',22,TEAL,True)
        txt(d,(54,253),'Approved ingredients',28,MUTED)
        txt(d,(54,302),'sunflower oil',52,bold=True)
        txt(d,(54,416),'Proof ingredients',28,MUTED)
        txt(d,(54,465),'canola oil',52,RED,True)
        line(d,(54,544,420,544),RED,5)
        txt(d,(780,322),'A substitution',32,RED,True)
        txt(d,(780,370),'to follow up.',32,RED,True)
    elif idx==4:
        resolved=local>=2.0
        txt(d,(54,190),'3 / 3 reviewed' if resolved else '2 / 3 reviewed',38,TEAL,True)
        txt(d,(800,200),'2 for follow-up' if resolved else '1 for follow-up',28,TEAL)
        line(d,(54,256,1226,256))
        for y,desc,state in [(288,'P1 · Weight changed','Reviewed'),(368,'P1 · Ingredient changed','Follow up'),(448,'P2 · Printer reference added','Follow up' if resolved else 'Not reviewed')]:
            txt(d,(54,y),desc,28);txt(d,(974,y),state,24,TEAL if state!='Not reviewed' else MUTED)
        txt(d,(54,555),'J / K  navigate     R  reviewed     F  follow-up',28,bold=True)
        txt(d,(54,603),'Illustrative review choices. Reviewed does not mean approved.',22,MUTED)
    elif idx==5:
        txt(d,(54,194),'SIMULATION ONLY',28,RED,True)
        txt(d,(54,251),'A$39',94,bold=True)
        txt(d,(54,382),'Proposed one-off price',28,MUTED)
        txt(d,(54,459),'No card details. No money moves.',32)
        txt(d,(54,518),'Cancel returns to review; simulated success unlocks export.',24)
        txt(d,(54,573),'PayPal is not connected.',24,RED)
    elif idx==6:
        txt(d,(54,202),'HTML REVIEW REPORT',28,TEAL,True)
        for y,number,label in [(274,'01','Every detected text difference'),(355,'02','Review decisions and follow-up flags'),(436,'03','Full extracted page context')]:
            txt(d,(54,y),number,32,TEAL,True);txt(d,(136,y),label,32)
        line(d,(54,515,1226,515))
        txt(d,(54,550),'Building ProofDelta. Feedback welcome.',38,bold=True)
        txt(d,(54,604),'Prototype · React frontend · Rust service tested locally',22,MUTED)
    return im
cmd=['ffmpeg','-y','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','fast','-crf','21','-pix_fmt','yuv420p','-movflags','+faststart',str(OUT/'ProofDelta-demo.mp4')]
p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=(OUT/'ffmpeg.log').open('w'))
try:
    for n in range(FPS*DURATION): p.stdin.write(frame(n).tobytes())
finally: p.stdin.close()
if p.wait()!=0: raise RuntimeError('ffmpeg failed; inspect ffmpeg.log')
frame(12*FPS).save(OUT/'ProofDelta-cover.png')
contact=Image.new('RGB',(1280,4*360),PAPER)
for i,t in enumerate([2,6,13,19,27,33,39]): contact.paste(frame(t*FPS).resize((640,360)),((i%2)*640,(i//2)*360))
contact.save(OUT/'contact-sheet.jpg',quality=92)
print(OUT/'ProofDelta-demo.mp4')
