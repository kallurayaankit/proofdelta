from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
pdfmetrics.registerFont(TTFont("Sample", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("Sample-Bold", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))
from pathlib import Path
root=Path(__file__).resolve().parents[1]/'dist'/'samples'
root.mkdir(exist_ok=True)
for proof in (False,True):
    name='printer-oat-bites.pdf' if proof else 'approved-oat-bites.pdf'
    c=canvas.Canvas(str(root/name),pagesize=(600,500),invariant=1)
    c.setTitle('Fictional oat bites packaging sample')
    pages=[['Original oat bites',f'Net weight: {160 if proof else 180} g',f'Ingredients: oats, dates, {"canola" if proof else "sunflower"} oil, sea salt.','Batch code: OB042'],['Store in a cool, dry place.','Pack made from recycled paper.']+(['Printer reference: 221B'] if proof else [])]
    for i,lines in enumerate(pages):
        c.setFillColor(HexColor('#eaf0e9'));c.rect(0,0,600,500,fill=1,stroke=0)
        c.setStrokeColor(HexColor('#45685b'));c.roundRect(28,28,544,444,12,stroke=1,fill=0)
        c.setFillColor(HexColor('#14352c'));c.setFont('Sample-Bold',12)
        c.drawString(52,433,'PROOFDELTA / FICTIONAL SAMPLE')
        y=365
        for j,line in enumerate(lines):
            c.setFont('Sample-Bold' if j==0 else 'Sample',24 if j==0 and i==0 else 12)
            c.drawString(52,y,line);y-=44
        c.setFont('Sample',11);c.drawString(52,60,f'Not for production. Synthetic text for review testing. / Page {i+1}')
        c.showPage()
    c.save()
print('Two synthetic, two-page sample PDFs generated.')
