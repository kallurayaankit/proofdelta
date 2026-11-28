"""Simplified Chinese labels for the Standard Mandarin video edition.
Original fictional English PDF pages are retained as source evidence.
Uses installed Noto Sans CJK SC, font collection index 2.
"""
from PIL import ImageFont
import render_demo as base
TRANSLATIONS={
'ILLUSTRATED DEMO  /  FICTIONAL FILES':'流程演示  /  虚构示例文件',
'Selectable text only. Human review required.':'仅比较可选取的文字，仍须人工复核。',
'A tiny change. A closer look.':'小小改动，仔细检查。',
'Start with two PDFs.':'从两份 PDF 开始。',
'Catch the weight change.':'找出净含量变化。',
'Keep the ingredient context.':'结合上下文检查配料。',
'Work through every difference.':'逐项检查所有差异。',
'Preview the checkout.':'预览模拟结账。',
'Take the review with you.':'下载检查报告。',
'APPROVED':'已确认原稿','PRINTER’S PROOF':'印刷校样','APPROVED ORIGINAL':'已确认原稿',
'180 g':'180 克','160 g':'160 克',
'Packaging proof text comparison.':'包装校样文字比较。',
'Your PDFs are processed in your browser.':'PDF 在你的浏览器中本地处理。',
'Approved original':'已确认原稿','Printer’s proof':'印刷校样','COMPARE':'比较','2 pages each':'每份 2 页',
'CHANGE 1 OF 3   ·   SOURCE PAGE 1':'差异 1 / 3  ·  原文第 1 页',
'Net weight':'净含量',
'Compare the changed line in its page context.':'结合所在页面的文字，查看发生变化的内容。',
'CHANGE 2 OF 3   ·   SOURCE PAGE 1':'差异 2 / 3  ·  原文第 1 页',
'Approved ingredients':'原稿配料','Proof ingredients':'校样配料',
'sunflower oil':'葵花籽油','canola oil':'菜籽油',
'A substitution':'配料被替换','to follow up.':'需要进一步核实。',
'3 / 3 reviewed':'已检查 3 / 3 项','2 / 3 reviewed':'已检查 2 / 3 项',
'2 for follow-up':'2 项待跟进','1 for follow-up':'1 项待跟进',
'P1 · Weight changed':'第 1 页 · 净含量变化','P1 · Ingredient changed':'第 1 页 · 配料变化',
'P2 · Printer reference added':'第 2 页 · 新增印刷参考编号',
'Reviewed':'已检查','Follow up':'待跟进','Not reviewed':'未检查',
'J / K  navigate     R  reviewed     F  follow-up':'J / K 切换差异    R 标记已检查    F 标记待跟进',
'Illustrative review choices. Reviewed does not mean approved.':'检查状态仅作演示。“已检查”不代表批准印刷。',
'SIMULATION ONLY':'仅为模拟','A$39':'A$39',
'Proposed one-off price':'拟定单次价格（澳元）',
'No card details. No money moves.':'不收集支付信息，不产生扣款。',
'Cancel returns to review; simulated success unlocks export.':'取消后返回检查；模拟成功后可导出报告。',
'PayPal is not connected.':'尚未接入 PayPal。',
'HTML REVIEW REPORT':'HTML 检查报告',
'Every detected text difference':'所有检测到的文字差异',
'Review decisions and follow-up flags':'检查记录及待跟进标记',
'Full extracted page context':'完整的页面提取文字',
'Building ProofDelta. Feedback welcome.':'ProofDelta 开发中，欢迎反馈。',
'Prototype · React frontend · Rust service tested locally':'原型 · React 前端 · Rust 服务已在本地测试'
}
for size in base.F:
 base.F[size]=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',size,index=2)
for size in base.B:
 base.B[size]=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc',size,index=2)
original_txt=base.txt
def translated_txt(d,xy,s,size=28,color=base.INK,bold=False):
 if s not in TRANSLATIONS and s!='ProofDelta' and not s.replace(' ','').replace('/','').isdigit():
  raise ValueError('Untranslated label: '+s)
 if s == 'COMPARE': xy=(570,376)
 if s == '2 pages each': xy=(550,420)
 return original_txt(d,xy,TRANSLATIONS.get(s,s),size,color,bold)
base.txt=translated_txt
FPS=base.FPS;PAPER=base.PAPER;SCENES=base.SCENES;frame=base.frame
