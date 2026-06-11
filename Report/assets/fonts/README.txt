CJK 字体（PDF 渲染用）
======================

本目录的 WenQuanYiZenHei-Regular.ttf 随 skill 分发，用于在 PDF 中显示中文。

为什么是这个字体：xhtml2pdf 基于 reportlab，reportlab **只能嵌入 TrueType（glyf
轮廓）字体**，不支持 PostScript/CFF 轮廓。Noto Sans CJK、Source Han Sans 这类
常见中文字体是 CFF 轮廓，reportlab 会直接报
"postscript outlines are not supported"。文泉驿正黑（WenQuanYi Zen Hei）是 glyf
轮廓、覆盖简体中文，可用。

为什么放这里：reportlab 自己解析 TTF，不走系统 fontconfig，所以渲染 PDF 不需要
apt-get、不需要在服务器上装字体。字体随 skill 走，在干净服务器上也能直接渲染中文。
"零系统依赖" 不等于 "零字体文件"。

许可：WenQuanYi Zen Hei，GPL v2 + 字体嵌入例外（font embedding exception），
可随附再分发。

换字体的硬性要求：**必须是 glyf 轮廓的 .ttf**（不能用 CFF/.otf）。
  1. 把新的 glyf TTF 放进本目录；
  2. 改 assets/report.css 的 @font-face：src: url("fonts/你的字体.ttf");
     （body 用别名 "CJK"，不用改。）
快速自检某字体是否可用：
    python -c "from reportlab.pdfbase.ttfonts import TTFont; TTFont('t','你的字体.ttf')"
  能加载且不抛 TTFError 即可。

注：reportlab 对粗体为合成（faux-bold）。要求高可另放 Bold 字重并加第二条 @font-face。
