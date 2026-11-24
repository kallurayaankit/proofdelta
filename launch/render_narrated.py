"""Render the Raya edition at the narration's natural speed.
Run: python launch/render_narrated.py
Inputs (local only): tmp/launch/raya/narration-original.wav and
speech-metadata.json containing paragraphs and HeyGen original_characters.
Original audio stays unmodified. No voice cloning or synthesis occurs here.
"""
from pathlib import Path
import json, math, subprocess, sys
from PIL import Image
sys.dont_write_bytecode = True
import render_demo as art
ROOT=Path(__file__).resolve().parents[1]; P=ROOT/'tmp/launch/raya'
data=json.loads((P/'speech-metadata.json').read_text())
chars=data['characters']; text=''.join(x['text'] for x in chars)
assert text=='\n\n'.join(data['paragraphs'])
meta=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(P/'narration-original.wav')]))
duration=float(meta['format']['duration']); count=math.ceil(duration*art.FPS)
starts=[];offset=0
for para in data['paragraphs']:
    starts.append(float(chars[offset]['start_time']));offset+=len(para)+2
starts[0]=0.0
bounds=[round(t*art.FPS) for t in starts]+[count]
assert all(a<b for a,b in zip(bounds,bounds[1:]))
timeline={'fps':art.FPS,'duration':duration,'frames':count,'audio_speed':1.0,'scene_start_frames':bounds[:-1],
          'scene_start_seconds':[n/art.FPS for n in bounds[:-1]],'timing_source':'HeyGen character alignment; exact script matched',
          'review_limitations':'No full listening or real-time audiovisual playback available; alignment, frames and encoded streams checked.'}
(P/'edit-timeline.json').write_text(json.dumps(timeline,indent=2))
# Small gain-only adjustment preserves voice, speed, pitch and dynamics.
a=json.loads((P/'loudness.json').read_text());gain=min(-16-float(a['input_i']),-1.5-float(a['input_tp']))
cmd=['ffmpeg','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1280x720','-r',str(art.FPS),'-i','-',
     '-i',str(P/'narration-original.wav'),'-map','0:v:0','-map','1:a:0','-c:v','libx264','-preset','fast','-crf','21',
     '-pix_fmt','yuv420p','-af',f'volume={gain:.3f}dB','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',
     str(ROOT/'launch/media/ProofDelta-Raya-Voice.mp4')]
p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=(P/'render.log').open('w'))
def graphic(n):
    idx=next(i for i in range(7) if bounds[i]<=n<bounds[i+1])
    # Retiming applies only to the authored graphic, never to narration.
    frac=(n-bounds[idx])/(bounds[idx+1]-bounds[idx])
    old_start,old_end,_=art.SCENES[idx]
    old_frame=min(math.ceil(old_end*art.FPS)-1,int((old_start+frac*(old_end-old_start))*art.FPS))
    return art.frame(old_frame)
try:
    for n in range(count):p.stdin.write(graphic(n).tobytes())
finally:p.stdin.close()
assert p.wait()==0,'FFmpeg render failed'
contact=Image.new('RGB',(1280,1440),art.PAPER)
for i in range(7):
    midpoint=(bounds[i]+bounds[i+1])//2
    contact.paste(graphic(midpoint).resize((640,360)),((i%2)*640,(i//2)*360))
contact.save(P/'review.jpg',quality=92)
print(json.dumps({'duration':duration,'frames':count,'gain_db':gain,'scene_starts':timeline['scene_start_seconds']}))
