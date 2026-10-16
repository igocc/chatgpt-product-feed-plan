from pathlib import Path
import csv
import html
import json

ROOT = Path(__file__).resolve().parent
DATE = '2026-10-16'
SOURCES = [
 ('S1', 'OpenAI 商家申请与候补入口', 'https://chatgpt.com/merchants/', '申请表、候补、Shopify 既有集成；不是批准函。'),
 ('S2', 'OpenAI Product Feed 接入指南', 'https://developers.openai.com/commerce/guides/get-started', '获批合作伙伴、文件与 API 接入、更新建议。'),
 ('S3', '文件投递与快照处理', 'https://developers.openai.com/commerce/specs/file-upload/overview', 'SFTP、固定文件名、分片、保留与移除规则。'),
 ('S4', '文件格式商品字段规范', 'https://developers.openai.com/commerce/specs/file-upload/products', '九个基础字段、变体、金额、库存、市场与资格。'),
 ('S5', 'API 请求约定', 'https://developers.openai.com/commerce/specs/api/overview', '认证头、幂等键、请求追踪；生产接入参数须获批后确认。'),
 ('S6', 'Feed API', 'https://developers.openai.com/commerce/specs/api/feeds', '创建及读取 Feed 元数据。'),
 ('S7', 'Products API', 'https://developers.openai.com/commerce/specs/api/products', '嵌套商品与变体、金额最小单位、PATCH upsert。'),
 ('S8', 'OpenAI Feed 最佳实践', 'https://developers.openai.com/commerce/guides/best-practices', '事实描述、稳定标识、变体专属数据及追踪。'),
 ('S9', 'Shopify 向 ChatGPT 分发的条件', 'https://help.shopify.com/en/manual/online-sales-channels/agentic-storefronts/chatgpt', '原生渠道资格及商家政策要求。'),
 ('S10', 'Shopify Catalog 与商品发现', 'https://help.shopify.com/en/manual/online-sales-channels/agentic-storefronts/products', 'Catalog 分发与网站发现文件的区别。'),
 ('S11', 'Shopify Admin GraphQL 批量读取', 'https://shopify.dev/docs/apps/build/apis/graphql-admin/bulk-operations/queries', '服务端批量读取商品与变体。'),
 ('S12', 'Shopify HTTPS Webhook 接收', 'https://shopify.dev/docs/apps/build/webhooks/subscribe/https', '原始请求体 HMAC 验证与接收处理。'),
]

MATERIALS = [
 ('A01','企业与网站','公司名称、总部国家、商家官网','业务负责人','公开申请表','申请前','未提供','官网主体与申请主体可解释；勿填虚构信息'),
 ('A02','申请联系人','姓名、职务、LinkedIn、工作邮箱','业务负责人','公开申请表','申请前','未提供','公开网页仅列字段；真实信息放受控申请包'),
 ('A03','目录规模','主要商品类别、唯一 SKU 数量及统计日期','商品运营','公开申请表','申请前','待统计','区分产品数与可购买变体数，不以页面数代替'),
 ('A04','Feed 准备情况','是否已符合规范、样例是否完成','技术负责人','公开申请表','申请前','待准备','仅在实际完成后选择已就绪'),
 ('A05','申请补充说明','数据来源、更新能力、希望接入的范围','业务＋技术','建议补充','申请前','待编写','使用下载模板；不是官方必填的额外门槛'),
 ('B01','目标范围','商家主体、店铺域名、品牌与域名授权关系','业务负责人','内部实施','G0','待确认','同一商品重复供给、代理供给必须有权限依据'),
 ('B02','市场与语言','首批目的国、语言、币种、可配送范围','业务＋履约','内部实施','G0','待确认','建议首期美国／英语／USD；其他市场须平台确认'),
 ('B03','现有分发','Shopify Catalog、第三方 Feed 与直接接入现状','渠道运营','内部实施','G0','未核验','确认同一域名和商品的数据源优先级'),
 ('B04','商品权威源','Shopify／ERP／PIM 各字段来源与冲突裁决人','商品＋技术','内部实施','G0','待确认','价格和库存以实际可购买市场为准'),
 ('B05','商品样本','约 100 个可购买条目，覆盖多变体、促销、缺货','商品运营','平台建议样本','G1','待准备','仅通过获批渠道交付；样本不能全是理想数据'),
 ('B06','价格合同','常规价、促销价、币种、税费展示与生效时区','商品＋财务','内部实施','G1','待确认','Feed 与落地页实际可支付价格一致'),
 ('B07','库存合同','按市场的可售判断、预售、欠货及库存源','履约＋技术','内部实施','G1','待确认','库存数量不能直接等同可售状态'),
 ('B08','商品素材','标题、纯文本描述、品牌、主图与变体 URL','商品运营','字段规范','G1','待准备','真实公开可访问；不补造 GTIN、评价或材质'),
 ('B09','商家政策','配送、退换货、隐私、服务条款及联系入口','法务＋运营','内部实施／渠道要求','G1','待核验','区分原生 Shopify 条件与直接接入字段条件'),
 ('B10','权利与禁售审核','品牌授权、图片权利、禁售与限制品类清单','法务＋商品','平台政策＋内部实施','G1','待审核','有争议条目先隔离，不能默认允许推送'),
 ('C01','Shopify 访问','店铺标识、应用安装方式、所需读取 scope','技术负责人','内部实施','G1','待配置','凭证只进 Secret Manager，不进表格或 GitHub'),
 ('C02','生产运行环境','服务账号、数据库、对象存储、HTTPS 入口','平台工程','内部实施','G1','待配置','运行环境与公开文档站点完全分开'),
 ('C03','更新与责任','时效目标、告警接收人、发布批准人、替补','业务＋技术','内部实施','G1','待确认','建议目标不是 OpenAI SLA'),
 ('C04','平台准入证据','批准通知、获准商家／域名／Feed 范围','业务负责人','平台联调','G2','尚未核验','候补邮件、已填表或 Shopify 集成不是直连批准'),
 ('C05','文件投递配置','SFTP 地址、端口、目录、认证及主机指纹','技术＋OpenAI','平台联调','G2','等待平台提供','确认网络策略、轮换方式、文件数和上传行为'),
 ('C06','API 接入配置','生产 Base URL、权限、凭证、版本与限额','技术＋OpenAI','平台联调','G2','等待平台提供','不猜测通用 API 域名和普通模型密钥适用性'),
 ('C07','双通道约定','文件 item_id 与 API 产品／变体 ID 映射及覆盖顺序','技术＋OpenAI','平台联调','G2','待书面确认','未确认前只启用一种投递通道'),
 ('C08','接收与移除证据','接收结果查询方式、拒绝报告、紧急撤回渠道','技术＋OpenAI','平台联调','G2','待确认','不能用传输完成替代平台处理完成'),
 ('C09','预算与排班','人力、云资源额度、采购与值班责任','业务负责人','内部实施','G0','待确认','不含承诺审批时长或曝光量'),
]

TASKS = [
 ('T01','G0','业务负责人','确认直连必要性、目标市场、原生分发基线','范围表与数据源决定','无','1–2 人日'),
 ('T02','G0','业务＋技术','整理 A01–A05，生成受控申请包','已复核的申请材料','T01','1 人日'),
 ('T03','G0','业务负责人','通过官方入口提交并保存回执','申请时间与候补／批准原文','T02','0.5 人日；等待另计'),
 ('T04','G1','技术负责人','获取最小只读权限并冻结源字段合同','scope 清单、字段责任表','T01','1–2 人日'),
 ('T05','G1','后端工程','实现首次批量读取和完整性核对','商品／变体源快照','T04','2–3 人日'),
 ('T06','G1','后端工程','实现 ID、市场价格、库存和变体标准化','标准目录和稳定身份映射','T05','2–3 人日'),
 ('T07','G1','商品＋后端','实现规则校验与异常隔离','逐行错误清单与原因码','T06','2 人日'),
 ('T08','G1','后端工程','实现稳定文件名的 JSONL gzip 导出','约 100 条样本与本地全量快照','T07','1–2 人日'),
 ('T09','G1','后端工程','实现事件持久化、去重、乱序保护与重查','可重放事件、失败队列','T06','2–3 人日'),
 ('T10','G1','QA＋商品','核验样本、网页一致性和金额边界','G1 验收报告','T08,T09','2 人日'),
 ('T11','G2','业务＋OpenAI','取得直连批准及 C04–C08 接入合同','准入证据与书面参数','T03','外部等待，不估时'),
 ('T12','G2','后端工程','配置 SFTP 联调样本、幂等投递与回执','接收／拒绝及纠错证据','T10,T11','1–2 人日'),
 ('T13','G2','QA＋OpenAI','验证变体、价格更新与撤回场景','平台侧测试记录','T12','1–2 人日；平台等待另计'),
 ('T14','G2','后端工程','若获 API 权限，实现独立 API 编码器与身份桥','金额／结构测试、覆盖顺序验证','T11,T13','2–3 人日；条件项'),
 ('T15','G3','平台工程','配置告警、备份、Secret 轮换及暂停开关','运行手册与恢复演练','T13','1–2 人日'),
 ('T16','G3','QA＋业务','按已选范围完成全量核对与上线签字','G3 验收记录和上线范围','T15','1–2 人日'),
 ('T17','G3','运营＋技术','小批量放量，记录实际处理延迟与拒绝率','观察日志与问题清单','T16','3 个工作日观察；非持续人日'),
 ('T18','运行','渠道运营','核验真实商品结果、落地页与追踪','可见性观察与访问记录','T17','持续；不承诺展示'),
 ('T19','运行','技术负责人','每周核对规格和错误分类，按月演练恢复','规则变更记录和恢复报告','T17','持续'),
]

FIELDS = [
 ('item_id','必填','店铺＋市场＋变体不可变 ID','字符串；不依赖会变化的 SKU 文案或价格'),
 ('title','必填','商品标题＋实际变体信息','不堆关键词；与页面选中变体一致'),
 ('description','必填','事实性商品描述','纯文本；缺失时隔离，不让模型补造规格'),
 ('url','必填','已选中变体的公开商品 URL','可访问、稳定、与市场和币种一致'),
 ('brand','必填','商品实际品牌','不能把 vendor 未经核验地当品牌'),
 ('seller_name','必填','该报价的真实卖家名称','与申报主体、店铺页面关系明确'),
 ('image_url','必填','变体主图或适用的商品主图','直链公开可取；不能链接图片查看页'),
 ('availability','必填','市场可售状态映射','文件枚举 in_stock / out_of_stock / pre_order / backorder / unknown'),
 ('price','必填','常规价格＋约定币种','主单位字符串，例如 79.99 USD'),
 ('group_id','变体条件必填','同一商品父级稳定 ID','必须不同于每个 item_id'),
 ('listing_has_variations','变体条件必填','是否有真实选择维度','每个变体行设 true'),
 ('variant_dict','变体条件必填','selectedOptions，经统一命名','选项组合在组内唯一'),
 ('sale_price','可选','真实且正在生效的促销价','大于零、低于 price、同币种'),
 ('gtin / mpn','可选','经核验的商品标识','无值则省略；不造码，保留前导零'),
 ('is_eligible_search','可选，项目显式输出','条目搜索资格控制','false 用于取消资格；不等同瞬时下架'),
]

def table(headers, rows):
    return '<div class="table-wrap"><table><thead><tr>' + ''.join('<th scope="col">'+html.escape(h)+'</th>' for h in headers) + '</tr></thead><tbody>' + ''.join('<tr>'+''.join('<td>'+str(c)+'</td>' for c in row)+'</tr>' for row in rows) + '</tbody></table></div>'

def ref(*ids):
    return '<span class="refs">' + ' '.join(f'<a href="#source-{i}">[{i}]</a>' for i in ids) + '</span>'

def badge(kind, text):
    return f'<span class="tag {kind}">{text}</span>'

sections=[]
def section(id, number, title, intro, body):
    sections.append((id,number,title,f'<section id="{id}" aria-labelledby="h-{id}"><div class="section-kicker">{number}</div><h2 id="h-{id}">{title}</h2><p class="intro">{intro}</p>{body}</section>'))

section('decision','01','先决定接入路径与首期范围','目标是让 ChatGPT 获取准确的商品目录。自建系统负责数据与投递，OpenAI 负责准入、接收与产品展示。',f'''
<div class="callout"><strong>本交付是实施方案，尚未建设或投递真实 Feed。</strong> 未核验企业直连资格，也未读取生产店铺。空白资料应在受控环境补齐，不在公开网页输入。</div>
{table(['路径','适用情形','动作与边界'],[
('Shopify 原生分发','已在 Shopify 销售，主要诉求是商品被 ChatGPT 发现','先核验 Catalog 资格和渠道设置。原生集成不等于获准开通另一条独立直连。'+ref('S1','S9')),
('自建直接 Feed','多来源目录、独立数据治理或有明确的直连接入诉求','建设独立数据流水线，并向 OpenAI 申请。系统就绪不替代准入批准。'+ref('S2')),
('第三方分发','希望采购服务而非自行运维','要求供应商提供实际投递权限、回执和撤回能力证明，不以模板支持代替接入证据。')])}
<h3>建议的首期合同</h3><p>单一商家、单一数据源，面向美国市场、英语内容和 USD，先做商品发现与站外落地页。标准文件上传当前以美国为目标，其他国家和币种需要 OpenAI 确认。此处是建议范围，不能替代商家的业务确认。{ref('S4')}</p>
<p>首期不建设购物 Agent、支付、订单处理、广告 Feed 或全渠道分发。后续平台可复用内部目录，但每个平台的权限、格式与市场范围分别验收。文件规范里的 checkout 字段不能自动开启结账。</p>
<p class="note">G0 必须确认：直连的业务价值、目标店铺与域名、商品主数据来源、原生与直连的覆盖关系、上线负责人。若原生分发已经满足需求，可以停在数据审计与完善阶段。</p>''')

section('approval','02','审批、候补与「白名单」机制','官方公开的是合作伙伴准入；内部如何按商家、域名、账号或网络授权，并未完整公开。',f'''
<div class="status-grid"><div><span class="tag fact">已确认</span><h3>提交申请 ≠ 已获批</h3><p>直接 Feed 接入目前面向获批合作伙伴。官方商家页说明已申请者进入候补名单。{ref('S1','S2')}</p></div><div><span class="tag unknown">未公开</span><h3>不是已知的 IP 白名单</h3><p>不能断言按 IP 开通；最低 GMV、最低 SKU、评分权重和审批时限均未在所查官方材料中公布。</p></div></div>
<ol class="steps"><li><strong>申请前：资料与样例。</strong> 业务负责人复核申请表；技术负责人如实声明 Feed 准备状态。</li><li><strong>提交：保存回执。</strong> 从 <a href="https://chatgpt.com/merchants/" target="_blank" rel="noopener">OpenAI 官方商家入口</a> 提交，记录日期、申请主体、域名和联系人。候补状态保持 WAITLISTED。</li><li><strong>平台沟通：补齐接入合同。</strong> 仅以 OpenAI 明确批准的主体、域名、市场和方式作为实施依据；补充材料与样例按平台要求提供。</li><li><strong>联调：先提交小样。</strong> 使用分配的投递通道，保存可获得的接收、拒绝和纠错证据，确认如何识别处理完成。</li><li><strong>生产：受控放量。</strong> G2 平台验收通过后才能开放自动生产投递。任何展示或排名均不能由提交成功推导。</li></ol>
<p><strong>正式申请表收集：</strong>联系人姓名、职务、LinkedIn、工作邮箱，公司名称、总部国家、官网、主要类别、唯一 SKU 规模、接入意向、Feed 准备情况与补充说明。它们是资料项，不是公开的通过阈值。{ref('S1')}</p>
<h3>获批后必须向平台确认的 12 个问题</h3>
{table(['编号','要确认的事项'],[
('Q01','批准涵盖的主体、店铺、域名、品牌、国家与币种分别是什么？'),
('Q02','与已有 Shopify Catalog 或其他供应商 Feed 并存时，如何去重和选择权威数据源？'),
('Q03','允许 SFTP、API、托管 URL 中的哪些方式？本方案文件通道以文档规定的 SFTP 为基线。'),
('Q04','SFTP 主机、端口、目录、密钥、主机指纹及网络限制由谁提供和维护？'),
('Q05','API Base URL、认证范围、版本、速率、批次限制和测试环境是什么？'),
('Q06','文件 item_id 如何映射 API Product.id 与 Variant.id？双通道是否写同一个目录？'),
('Q07','全量文件与增量 API 并发时，哪个版本生效？如何避免旧快照回写旧价格？'),
('Q08','字段拒绝、文件拒绝及处理延迟在哪里查询？是否存在可调用的处理状态接口？'),
('Q09','更新和取消搜索资格何时生效？紧急撤回、误售与禁售品的人工升级渠道是什么？'),
('Q10','分片、压缩、上传完成判断以及首次全量切换有什么环境专属要求？'),
('Q11','市场、语言、域名验证、商品政策及可选字段是否存在额外接入条件？'),
('Q12','凭证轮换、事故联系、终止接入、数据删除及服务变更通知如何处理？')])}
<p class="note">平台未答复这些问题时，允许推进本地目录与模拟投递；不得猜 Base URL、冒用普通模型 API Key、伪造批准回执或宣称已进入正式目录。</p>''')

section('materials','03','资料诉求与责任分工','所有真实企业、联系人和配置均待收集。此表用于发起内部协作，不表示资料已经齐备。',f'''
<p><a class="text-action" href="downloads/materials-request.csv" download>下载完整资料诉求表 CSV ↗</a>　<a class="text-action" href="downloads/application-template.md" download>下载英文申请说明模板 ↗</a></p>
{table(['编号','资料组','需要提供什么','建议责任人','用途／要求来源','阻断阶段'],[(r[0],r[1],r[2],r[3],r[4],r[5]) for r in MATERIALS])}
<div class="callout subtle"><strong>资料提交方式：</strong>业务负责人收齐受控资料包；技术配置通过私有 Secret Manager 交接。公开 GitHub 仅存放空白模板、示例和技术方案。联系人、证件、真实成本、供应商凭证及原始批准邮件均不发布。</div>
<h3>交接包目录建议</h3><pre><code>private-onboarding/（私有，不放本仓库）
  01-business/       主体、联系人、域名与申请说明
  02-catalog/        样例、字段字典、市场与价格库存合同
  03-policy/         政策链接、授权与品类审核记录
  04-platform/       批准证据、接入参数、问题答复
  05-acceptance/     接收结果、纠错、撤回与签字记录
  secrets-reference 密钥管理器引用；不保存密钥明文</code></pre>''')

section('contract','04','商品数据合同：先文件，后 API','采用独立内部目录模型，再分别编码文件和 API；两种外部结构不能直接互传。',f'''
<h3>文件发现 Feed 的基础映射</h3><p>下表概括首期字段；完整的长度、枚举、条件与可选字段以 S4 为准。数据输出单位是一条可购买商品或变体。{ref('S4')}</p>
{table(['输出字段','要求','业务来源','项目校验'],[(f'<code>{a}</code>',b,c,d) for a,b,c,d in FIELDS])}
<p><a class="text-action" href="downloads/field-mapping.csv" download>下载字段映射表 ↗</a></p>
<h3>文件与 API 的关键差异</h3>
{table(['项目','文件发现 Feed','Products API'],[
('结构与身份','平面条目；item_id 标识变体，group_id 分组','Product.id ＋ variants[].id 嵌套结构；关联规则须联调确认'),
('金额','price 为主单位字符串，例如 79.99 USD；sale_price 为生效中的促销价','price.amount 为货币最小单位整数；79.99 USD 对应 7999，而非 79.99'),
('库存','文件使用 pre_order；其他状态按 S4 枚举','API 文档示例使用 preorder 等状态；不得机械照搬字符串'),
('缺省／删除','完整快照有保留窗口，遗漏不是即时删除','PATCH 为 upsert；未包含的产品保持不变，不能当成 DELETE'),
('搜索资格','可用 is_eligible_search=false 取消资格，待下次处理','公开的 API 产品结构未列出同名控制字段；撤回方式必须平台确认')])}
<p class="note">文件与 API 的字段差异依据 S4、S7。内部统一使用 Decimal 金额、ISO 币种、不可变身份和自定义内部库存枚举；编码时按各自合同转换。不得把内部 price=7999 直接写入文件成为 7999 USD。{ref('S4','S7')}</p>
<h3>身份与市场规则</h3><p>建议内部键包含 merchant_id、source_shop、market、source_product_id、source_variant_id。导出 item_id 使用稳定映射，SKU 仅作为业务属性。不同店铺和市场不得互相覆盖；父商品不是可购买变体。GTIN 没有可靠来源就省略。价格、库存、图片与 URL 必须对应同一市场和变体。</p>
<p>促销规则：有有效且高于现价的常规价时，文件写常规价和较低的 sale_price；否则只写真实现价。compareAtPrice 是否可作为常规价必须由业务验证，不能默认视为真实折扣。API 的现售价格与参考价分别映射。</p>
<h3>仅用于结构演示的文件样例</h3><p>虚构商品与 example.com 地址不能直接投产；该样例不是已通过平台验收的记录。</p><pre><code>{html.escape(json.dumps({'item_id':'demo-us-variant-001','title':'Example ceramic mug, blue, 350 mL','description':'Demonstration record only. Replace with verified product facts.','url':'https://example.com/products/mug?variant=001','brand':'Example Brand','seller_name':'Example Seller','image_url':'https://example.com/images/mug-blue.jpg','availability':'in_stock','price':'18.00 USD','is_eligible_search':True},ensure_ascii=False,indent=2))}</code></pre>''')

section('architecture','05','系统架构与交付模块','建议采用单一后端、持久任务队列和两个独立投递适配器。公开 HTML 只承载文档。',f'''
<div class="pipeline" role="img" aria-label="数据源经过采集、标准目录、校验和快照，送入获批投递通道，再核对 OpenAI 处理结果"><div>Shopify / ERP<small>只读数据源</small></div><b aria-hidden="true">→</b><div>采集与标准目录<small>身份、市场、版本</small></div><b aria-hidden="true">→</b><div>校验与隔离<small>错误单独处理</small></div><b aria-hidden="true">→</b><div>快照 / 增量任务<small>持久化、可重放</small></div><b aria-hidden="true">→</b><div>获批投递通道<small>SFTP / 条件 API</small></div><b aria-hidden="true">→</b><div>结果与对账<small>接收、处理、展示分离</small></div></div>
{table(['模块','建议实现','交付标准'],[
('源采集器','Shopify Admin GraphQL 批量首读；小目录可分页；Webhook 触发后重新读取权威状态','完整数据集、源更新时间、分页／批量结束证据；不能把部分下载当全量。'+ref('S11')),
('内部目录','PostgreSQL；不可变 ID、市场维度、源版本、Decimal 金额、资格与隔离原因','导出可追溯到源记录和规则版本'),
('校验器','Python ＋ Pydantic／JSON Schema；业务一致性校验另列','错误含 ID、字段、原因、修复责任人；未知字段不能静默上传'),
('快照生成器','JSONL＋gzip 起步；稳定文件名、确定性分片、私有对象存储归档','逐行检查、计数核对、内容 hash、规范版本与 manifest'),
('任务与事件','PostgreSQL 持久任务／outbox，worker 和调度器分别运行','事件去重、重试、死信、并发锁、断点和快照水位'),
('SFTP 适配器','校验主机指纹；按平台要求覆盖稳定文件／分片集合','真实平台投递证据；首次生产写入默认关闭'),
('API 适配器','获批后实现；独立序列化器、身份桥、幂等键和速率控制','与文件金额、身份、版本覆盖关系验收后启用'),
('管理与监控','FastAPI 提供私有状态／重试／暂停入口；审计日志与指标','有负责人、有停机开关；不把管理接口暴露到 Pages')])}
<p>建议运行方式：Docker 化 API、worker、scheduler 与托管 PostgreSQL，搭配私有对象存储和 Secret Manager。开发与联调使用相同镜像，生产独立凭证；具体版本在开工时锁定并记录。首期不需要 Kubernetes、向量数据库、LLM 自动写商品事实或浏览器模拟投递。</p>
<h3>最小数据表与工件</h3><p><code>catalog_items</code> 记录标准目录；<code>source_events</code> 记录源事件；<code>export_runs</code> 记录水位与计数；<code>delivery_jobs</code> 记录待投递和重试；<code>delivery_receipts</code> 记录平台实际结果；<code>eligibility_actions</code> 记录撤回动作。manifest 至少含 export_id、market、source_watermark、schema_hash、条目数、分片及 hash。内部 manifest 不随意放进 SFTP 根目录。</p>''')

section('delivery','06','同步、投递与撤回流程','先证明目录正确，再证明平台接受；双通道和多市场必须分别解锁。',f'''
<h3>首次全量</h3><ol class="steps"><li>只读采集全部源记录，确认分页或批量任务完整结束。</li><li>冻结市场、规则版本与源水位；标准化后输出候选、合格、隔离、撤回条目计数。</li><li>生成样例并人工核验。未获批时只做本地与模拟环境验证。</li><li>获批后投递约 100 条样本。样本规模为官方建议，不是最低 SKU 准入门槛。{ref('S3')}</li><li>平台反馈清楚后再上首次全量；保留本地可追溯归档与实际回执。</li></ol>
<h3>日常更新</h3><p>文件通道至少每日完整快照；稳定文件名原位更新，分片集合保持稳定。官方建议单分片不超过约 50 万条、目标小于约 500 MB，项目应按实际压缩体积和平台约定再调小；编码为 UTF-8。JSONL gzip 是本方案首选支持格式。{ref('S3')}</p>
<p>事件到达后先验证原始 body 的 HMAC，再持久化并入队；按源事件标识去重。Webhook 可能重复或乱序：重读权威源并比较版本，不用旧事件覆盖新数据。每日全量对账修复漏事件。{ref('S12')}</p>
<p>API 若已获批，可作为日内增量更新。全量开始时记录水位，暂缓有覆盖风险的并发写入，待快照处理边界明确后重放较新变更；平台未提供可判断处理完成的机制时，先保持单通道，不能宣称已解决写入顺序。{ref('S2','S7')}</p>
<h3>撤回与过期：不能只把商品从导出结果删掉</h3><div class="callout"><strong>官方文件规则：</strong>遗漏商品可能保留至多 14 天。取消搜索资格应在可处理的快照中显式输出 <code>is_eligible_search=false</code>；需要紧急撤回时走平台确认的升级渠道。该标志不承诺即时生效。{ref('S3')}</div>
<p>项目保留最近有效的合规记录和 tombstone，让已下架商品在撤回快照中保留稳定 item_id 与必要字段。验证失败的老商品也必须进入明确处置队列：能生成合法取消资格记录则发送，否则触发人工升级；不能静默漏掉并继续展示旧价。缺货用真实 out_of_stock，禁售或停卖用资格撤回，二者不混同。</p>
<p>SFTP 根目录代表目录集合。不要把备份、临时格式或内部 manifest 放入根目录；上传分片避免长暂停，按平台确认的可接受方式完成替换。文件上传完成不代表 OpenAI 已处理完成。{ref('S3')}</p>''')

section('gates','07','四个验收门：明确什么才算完成','开发验收、准入批准、平台处理和真实展示分别留证。',table(['门禁','进入条件','必须交付的证据','不通过时'],[
('G0 范围与申请就绪','B01–B04、C09 已确认；有负责人与预算','申请资料和范围表；明确原生／直连关系；真实申请回执（若已提交）','缺乏直连价值就先审计原生分发；缺资料不得声称申请已完成'),
('G1 本地技术就绪','源读取获授权；字段合同冻结','合格样例、全量对账、稳定 ID／币种／变体测试、模拟投递、失败重放、无凭证泄漏','修复问题后重验；可与外部候补并行，不发真实生产数据'),
('G2 平台联调通过','明确批准；C04–C08 配齐','平台接收及拒绝记录、纠错复验、价格库存更新与撤回结果；双通道如启用须专项验收','保持生产自动投递关闭；标记 PLATFORM_PENDING'),
('G3 可运行上线','G2 通过；业务批准上线范围','全量核对、告警、暂停／恢复演练、值班和回滚记录、小批量观察','缩小放量或暂停；恢复后重放较新版本，不能回推过时价格')
])+'''<h3>必须分开记录的状态</h3><p><code>LOCAL_VALIDATED</code> 本地校验 → <code>TRANSPORT_DELIVERED</code> 文件或请求已送达 → <code>PLATFORM_ACCEPTED</code> 平台接受 → <code>PLATFORM_PROCESSED</code> 有证据确认已处理 → <code>DISPLAY_OBSERVED</code> 实际观察到商品结果。不存在相应平台证据时保持 unknown，不自动升级状态。</p><p>API 返回 accepted=true 只证明该响应所描述的接收结果；HTTP 200、SFTP 上传成功、完整商家资格都不能保证具体查询的展示与排名。</p>''')

section('schedule','08','实施任务、依赖与资源','以下人日和时效均是项目估算或建议，不是平台承诺。外部审批等待不计入可承诺工期。',f'''
<p><a class="text-action" href="downloads/implementation-tasks.csv" download>下载可分工任务表 ↗</a></p>
{table(['任务','阶段','负责人角色','动作与产物','依赖','估算'],[(a,b,c,d+'<br><small>'+e+'</small>',f,g) for a,b,c,d,e,f,g in TASKS])}
<p>建议配置：1 名后端工程师主责，商品运营与 QA 分阶段参与，平台工程和业务负责人提供支持。按上表估算，工程与准备工作约 4–6 个日历周，前提是资料、人员和数据权限按时到位；API 条件项、数据修复和平台等待可能增加时间。正式排期以评审后任务估算为准。</p>
<p>预算按「工时 × 内部单价 ＋ 数据库／存储／计算／流量 ＋ 运维值班」核算。未评估目录规模与云厂商前不编造月费；每次全量记录压缩体积、耗时与云资源消耗，再决定升级容量。</p>''')

section('tests','09','验收测试：以真实业务故障为样本','下列是必须覆盖的测试场景，尚未执行。每项交付输入、期望、实际和证据链接。',table(['场景','期望结果','证据'],[
('商品／变体身份与重复事件','改标题、价格或 SKU 文案不换身份；同一事件重放不重复创建','跨两轮导出 diff、去重与事件重放记录'),
('多店铺／市场冲突','相同源数字 ID、不同市场价格不会覆盖','冲突样本与唯一键测试'),
('金额与促销','79.99 USD 与 API 7999 一致；无浮点偏差；促销开始／结束会刷新','Decimal 转换、有效时间和页面核对'),
('变体与页面','不同选项链接到对应变体、图片、价格和库存','实际 PDP 抽样记录'),
('源数据部分失败','批量未结束、分页失败或计数骤降时阻断全量发布','注入失败与 manifest 完整性证据'),
('坏数据与老记录','缺字段被隔离；已有记录有撤回／升级处置，不静默遗漏','隔离清单、撤回任务与平台复验'),
('撤回与缺货','缺货与取消搜索资格分别处理；验证平台实际处理结果','测试条目、时间线、官方反馈'),
('快照与 API 竞争','旧快照不覆盖新价格；不能确认时不启用双通道','水位与重放时间线'),
('网络、限额与凭证失效','重试不乱序；认证失败停投告警；不会无限循环','模拟超时、429、5xx、401/403 与恢复记录'),
('隐私与权限','没有订单／客户拉取；密钥不进入网页、日志和导出包','权限清单、敏感信息检查和日志抽样'),
('生产全量对账','源候选条目可归类为合格／隔离／明确排除；平台结果不靠推测','按市场计数、hash、错误清单与平台反馈')
])+'''<p class="note">项目建议门槛：发布记录必填字段合格率 100%，重复身份为 0，发现凭证泄漏为 0。它们是本项目的发布要求，不是 OpenAI 审批阈值。平台缺少可查询处理结果时，必须记录证据限制并取得业务例外批准，不填写虚假的处理成功率。</p>''')

section('operations','10','上线运行、监控与事故处理','把「有任务在跑」转换成「数据是否正确、是否被接收、出了问题谁处理」。',f'''
{table(['指标','建议目标／动作','责任'],[
('目录完整性','每轮记录源数、合格数、隔离数、撤回数；相对基线下降超过 20% 暂停全量并复核（可按业务调节）','商品运营＋后端'),
('文件新鲜度','至少每日快照；距上次成功投递超过 26 小时告警。平台处理新鲜度另计，不用投递时间代替','后端值班'),
('价格库存事件','内部事件到待投递建议 p95 ≤ 15 分钟；平台处理延迟以实测和平台约定为准','后端＋履约'),
('异常队列','每条错误有归属；关键商品错误当日升级；认证错误立即停投','商品／技术对应负责人'),
('投递重试','建议指数退避＋抖动，最多 5 次后死信；平台 Retry-After 和限额优先','后端'),
('恢复与归档','建议私有保留 30 天导出与回执；定期恢复演练；不把旧库存快照直接当生产回滚','平台工程'),
('规范维护','每周检查来源变更；生成规则有版本和差异；上线前重新核对官方规范','技术负责人')])}
<h3>故障 Runbook</h3><ol class="steps"><li><strong>传输失败：</strong>保留 export_id、错误时间和已脱敏错误；检查凭证有效性、网络和平台状态。业务数据不变时重试同一幂等任务。</li><li><strong>平台拒绝：</strong>暂停该批次自动放量，依据实际拒绝原因修复字段，只重新投递受影响记录或修复后的完整文件。</li><li><strong>价格或身份错误：</strong>立即暂停后续任务；以权威源重建正确记录；采用平台确认的更正／撤回流程，记录影响范围。</li><li><strong>密钥泄漏：</strong>撤销并轮换凭证，检查泄漏位置与访问日志；恢复前清理工件并重新测试。不要只删除网页可见内容。</li><li><strong>平台批准撤销或长期未获批：</strong>关闭生产投递，保留本地目录校验能力；按平台终止要求处理数据，继续可用的 Shopify 原生路径。</li></ol>
<p class="note">本节所有数值除官方每日快照建议外，均是待团队评审的内部目标；不是 OpenAI 的 SLA 或接入资格条件。</p>''')

section('boundaries','11','明确限制、待确认项与停做条件','把不能靠开发解决的问题放在实施前面，避免把技术完成误写成业务获准。',table(['问题','当前结论','实施处理'],[
('直连资格','本方案未核验申请或批准状态','收齐 C04；未批准保持模拟模式'),
('所谓白名单','存在合作伙伴准入，授权实现未公开','不假定 IP、普通 Key 或域名备案可以自动解锁'),
('审批门槛／时间','所查材料未公布最低 GMV／SKU、评分或 SLA','不以商业规模承诺通过；工期不包含审批'),
('直连与 Shopify 数据覆盖','本商家并行接入的优先级未知','取得书面答复前不做重复生产供给'),
('多市场','标准文件以美国为目标；其他范围须单独确认','首期限定已批准市场；不得只加国家字段就声称全球分发'),
('即时删除','遗漏不立即删除；文件保留机制有窗口','维护撤回记录与紧急升级渠道'),
('API 的资格撤回字段','公开 API schema 未列出文件同名字段','不虚构 API 撤回 payload 或 DELETE endpoint'),
('保证展示／排名','Feed 接入与展示是不同结果','不承诺搜索曝光、排名、流量或收入'),
('公开 HTML 的作用','文档站，不是生产服务或密钥容器','业务材料、真实商品数据与运行服务另行私有托管')
])+'''<p>停做条件：业务无法证明直连价值、没有合法数据访问权限、没有生产值班与事故负责人，或平台明确不接受目标商家／市场。此时停止生产建设投入或投递，保留可复用的数据准备成果。</p>''')

section('start','12','开工清单与下载包','清单只记录浏览器本机的勾选状态，不代表任何申请、开发或平台验收已经完成。',f'''
<div class="check-head"><strong id="progress-label">0 / 10 项已勾选</strong><button type="button" id="reset-checks" class="quiet">清空本机勾选</button></div><progress id="progress" max="10" value="0" aria-label="本机开工清单进度"></progress>
<div class="checks">{''.join(f'<label><input type="checkbox" data-check="{i}"><span>{t}</span></label>' for i,t in enumerate([
'指定业务负责人、技术负责人和上线批准人',
'确认美国市场、语言、币种和首批店铺范围',
'核验 Shopify 原生分发，说明另建直连的必要性',
'收齐申请表资料，并如实标记 Feed 准备状态',
'准备约 100 条真实样例及价格库存合同',
'取得源读取权限并记录最小 scope',
'完成 G1 本地技术验收与错误修复',
'取得 OpenAI 直接接入批准与通道参数',
'完成平台接收、纠错、更新与撤回验证',
'完成 G3 告警、恢复、值班与上线范围签字'
]))}</div>
<div class="download-list"><a href="downloads/materials-request.csv" download><strong>资料诉求表</strong><span>24 项资料、责任、状态与验收说明 · CSV</span></a><a href="downloads/implementation-tasks.csv" download><strong>实施任务表</strong><span>19 个任务、依赖、交付物和估算 · CSV</span></a><a href="downloads/field-mapping.csv" download><strong>字段映射表</strong><span>文件字段与业务来源 · CSV</span></a><a href="downloads/application-template.md" download><strong>申请与平台问题模板</strong><span>英文申请说明＋待确认接入合同 · Markdown</span></a><a href="index.html" download="chatgpt-product-feed-plan.html"><strong>离线 HTML</strong><span>保存本页；样式、脚本均内嵌</span></a></div>
<p>CSV 含中文列名和 UTF-8 BOM，便于表格软件打开。下载文件仅为模板；填写后保存到私有协作空间，不提交回此公开仓库。清单不接受自由文本，不上传勾选结果。</p>''')

section('sources','13','事实来源与版本维护','事实核对日期：2026-10-16。平台规范可能变更；生产联调必须重新核对并保存使用版本。',
 ''.join(f'<div class="source" id="source-{k}"><span>{k}</span><div><a href="{url}" target="_blank" rel="noopener">{title} ↗</a><p>{note}</p></div></div>' for k,title,url,note in SOURCES)
 + '<p class="note">文档标注规则：已确认事实来自以上官方页面；建议的架构、人日、指标、角色和步骤属于项目设计；明确待确认的参数不补猜。未填写企业资料不表示企业不符合资格，也不能反推其已经获批。</p>')

CSS='''
:root{--ink:#182e2b;--muted:#586b65;--paper:#f5f3eb;--white:#fffefa;--line:#d7ded5;--accent:#17634e;--soft:#e5efe6;--amber:#775419;--amberbg:#f5edda}*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:28px}body{margin:0;color:var(--ink);background:var(--paper);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;font-size:16px;line-height:1.85}a{color:var(--accent);text-underline-offset:4px}a:hover{text-decoration-thickness:2px}button{font:inherit;cursor:pointer}a:focus-visible,button:focus-visible,input:focus-visible{outline:3px solid #bd8019;outline-offset:4px}.skip{position:absolute;left:15px;top:-70px;background:white;padding:10px;z-index:5}.skip:focus{top:10px}.layout{max-width:1600px;margin:auto;display:grid;grid-template-columns:245px minmax(0,1fr);gap:66px;padding:36px 60px 100px}.sidebar{position:sticky;top:28px;align-self:start;max-height:calc(100vh - 56px);overflow:auto;font-size:13px}.wordmark{font-size:12px;letter-spacing:2px;font-weight:750;padding:8px 0 22px;border-bottom:1px solid var(--line)}.sidebar p{font-size:12px;color:var(--muted)}nav{padding-top:16px}nav a{display:flex;gap:13px;padding:8px 0;text-decoration:none;color:var(--muted)}nav a span{font-size:11px;min-width:20px;color:var(--accent);font-variant-numeric:tabular-nums}nav a:hover,nav a[aria-current=true]{color:var(--ink);font-weight:650}.sidebar .meta{margin-top:24px;padding-top:15px;border-top:1px solid var(--line)}main{min-width:0;max-width:1110px}.eyebrow{font-size:12px;letter-spacing:2.3px;color:var(--accent);font-weight:700}.hero{padding:31px 0 50px;border-bottom:2px solid var(--ink)}h1{font-size:clamp(34px,4.5vw,66px);font-weight:650;letter-spacing:-2px;line-height:1.17;margin:23px 0}h1 span{display:block;font-family:Georgia,"Times New Roman",serif;font-weight:400;letter-spacing:-1.5px;color:var(--accent);margin-top:9px}.hero .lede{max-width:740px;font-size:19px;color:var(--muted);margin:24px 0}.hero-meta{display:flex;gap:12px;flex-wrap:wrap;margin-top:23px;font-size:12px}.tag{display:inline-block;font-size:11px;line-height:1.65;padding:4px 9px;border-radius:3px;font-weight:600;background:#e7eae2;color:var(--muted)}.fact{background:var(--soft);color:#245b3b}.unknown{background:var(--amberbg);color:var(--amber)}.proposal{background:#e8ecef;color:#3f5868}.hero-actions{display:flex;gap:14px;flex-wrap:wrap;margin-top:28px}.button{display:inline-block;text-decoration:none;padding:10px 17px;font-size:13px;border:1px solid var(--accent);background:var(--accent);color:white}.button.secondary{background:transparent;color:var(--accent)}section{padding:49px 0 36px;border-bottom:1px solid var(--line);scroll-margin-top:24px}.section-kicker{font-family:Georgia,serif;font-size:20px;color:var(--accent);margin-bottom:3px}h2{font-size:29px;letter-spacing:-.6px;line-height:1.4;margin:0 0 16px;font-weight:650}h3{font-size:19px;line-height:1.6;margin:28px 0 10px}.intro{font-size:17px;color:var(--muted);margin:0 0 24px}p{margin:12px 0}small{font-size:12px;color:var(--muted)}.table-wrap{max-width:100%;overflow:auto;margin:22px 0;border:1px solid var(--line);background:var(--white)}table{width:100%;border-collapse:collapse;font-size:13px;line-height:1.75;min-width:690px}th,td{text-align:left;vertical-align:top;padding:13px 15px;border-bottom:1px solid var(--line)}th{background:#e9ede4;font-weight:650;color:#355147}tr:last-child td{border-bottom:0}td:first-child{font-weight:600}tbody tr:hover{background:#f1f5ed}.callout{background:var(--soft);border-left:3px solid var(--accent);padding:19px 23px;margin:22px 0;font-size:14px}.callout strong{display:block}.callout.subtle{background:#eeefe6}.note{color:var(--muted);font-size:13px;border-left:2px solid var(--line);padding-left:16px;margin:20px 0}.refs{font-size:11px;white-space:nowrap;margin-left:5px}.refs a{text-decoration:none}.status-grid{display:grid;grid-template-columns:1fr 1fr;gap:30px;margin:20px 0}.status-grid>div{border-top:1px solid var(--line);padding-top:16px}.status-grid h3{margin:12px 0 4px}.status-grid p{font-size:14px}.steps{padding-left:26px}.steps li{padding-left:7px;margin:14px 0;font-size:14px}.pipeline{display:flex;align-items:stretch;gap:9px;overflow:auto;padding:22px 0}.pipeline>div{flex:1;min-width:125px;border:1px solid #b4c6b7;padding:15px 13px;font-size:13px;background:var(--white);font-weight:650}.pipeline small{display:block;font-weight:400;margin-top:8px;font-size:11px}.pipeline b{align-self:center;color:var(--accent);font-weight:400}code{font-family:"SFMono-Regular",Consolas,monospace;font-size:.88em;overflow-wrap:anywhere}pre{background:#1d3430;color:#e6eee5;padding:22px;overflow:auto;font-size:13px;line-height:1.8;border-radius:3px}pre code{font-size:inherit;white-space:pre;overflow-wrap:normal}.text-action{font-size:13px}.check-head{display:flex;align-items:center;justify-content:space-between;gap:10px;font-size:14px}.quiet{font-size:12px;border:1px solid var(--line);color:var(--muted);padding:7px 11px;background:var(--white)}progress{width:100%;height:7px;appearance:none;accent-color:var(--accent);border:0;background:var(--line);margin:15px 0}progress::-webkit-progress-bar{background:var(--line)}progress::-webkit-progress-value{background:var(--accent)}.checks{display:grid;grid-template-columns:1fr 1fr;gap:0 26px}.checks label{display:flex;gap:12px;align-items:flex-start;border-bottom:1px solid var(--line);padding:14px 0;font-size:14px;cursor:pointer}.checks input{width:19px;height:19px;margin:4px 0 0;flex:0 0 auto;accent-color:var(--accent)}.checks label:has(input:checked) span{color:var(--muted)}.download-list{display:grid;grid-template-columns:1fr 1fr;gap:0 24px;margin:24px 0}.download-list a{border-top:1px solid var(--line);padding:18px 0;text-decoration:none}.download-list strong{font-size:15px;display:block}.download-list span{font-size:12px;color:var(--muted)}.source{display:flex;gap:18px;border-top:1px solid var(--line);padding:17px 0;font-size:14px;scroll-margin-top:30px}.source>span{font-family:Consolas,monospace;min-width:30px;font-size:12px;color:var(--accent)}.source p{margin:5px 0 0;font-size:12px;color:var(--muted)}footer{padding-top:28px;color:var(--muted);font-size:12px}.mobile-title{display:none}.back-top{display:block;margin-top:18px}.sr-only{position:absolute;width:1px;height:1px;padding:0;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}
@media(max-width:1100px){.layout{grid-template-columns:195px minmax(0,1fr);gap:32px;padding:25px 28px 70px}h1{font-size:49px}h2{font-size:26px}}@media(max-width:760px){.layout{display:block;padding:0 20px 55px}.sidebar{position:static;max-height:none;overflow:visible;padding:17px 0;border-bottom:1px solid var(--line)}.wordmark{border:0;padding:0}.sidebar>p,.sidebar .meta{display:none}nav{display:flex;gap:16px;overflow:auto;padding:7px 0 3px}nav a{white-space:nowrap;padding:5px 0;font-size:12px}nav a span{min-width:auto}main{max-width:100%}.hero{padding:31px 0}h1{font-size:39px;letter-spacing:-1.2px}.hero .lede{font-size:16px}.eyebrow{font-size:10px}section{padding:34px 0 25px}h2{font-size:24px}.intro{font-size:15px}.status-grid,.checks,.download-list{grid-template-columns:1fr;gap:8px}body{font-size:15px}.table-wrap{margin-left:0;margin-right:0}table{min-width:650px}th,td{padding:11px 12px}.hero-actions{gap:9px}.button{font-size:12px;padding:9px 13px}.callout{padding:16px 17px}pre{font-size:11px;padding:16px}.pipeline>div{min-width:120px}.source a{overflow-wrap:anywhere}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}@media print{body{background:white;color:#111;font-size:10pt}.layout{display:block;padding:0;max-width:none}.sidebar,.hero-actions,.check-head button,.back-top{display:none}main{max-width:none}h1{font-size:32pt}.hero{padding:0 0 18px}section{padding:22px 0;break-before:auto}h2,h3{break-after:avoid}h2{font-size:19pt}.table-wrap{overflow:visible}table{min-width:0;font-size:8pt}th,td{padding:7px}tr{break-inside:avoid}pre{white-space:pre-wrap;color:#111;background:#f2f2f2}pre code{white-space:pre-wrap}.pipeline{flex-wrap:wrap;overflow:visible}.source,.callout{break-inside:avoid}a{color:#174e3c}footer{font-size:8pt}}
'''

JS='''
(()=>{
const key='chatgpt-feed-plan-checks-v1';
const checks=[...document.querySelectorAll('[data-check]')];
let saved=[];try{saved=JSON.parse(localStorage.getItem(key)||'[]');if(!Array.isArray(saved))saved=[];}catch{}
checks.forEach(el=>el.checked=saved.includes(el.dataset.check));
function update(){const selected=checks.filter(el=>el.checked).map(el=>el.dataset.check);document.getElementById('progress').value=selected.length;document.getElementById('progress-label').textContent=`${selected.length} / ${checks.length} 项已勾选`;try{localStorage.setItem(key,JSON.stringify(selected))}catch{}}
checks.forEach(el=>el.addEventListener('change',update));
document.getElementById('reset-checks').addEventListener('click',()=>{checks.forEach(el=>el.checked=false);update()});update();
document.getElementById('print').addEventListener('click',()=>window.print());
if('IntersectionObserver' in window){const links=[...document.querySelectorAll('nav a')];const observer=new IntersectionObserver(entries=>{for(const e of entries){if(e.isIntersecting){links.forEach(a=>a.removeAttribute('aria-current'));const link=links.find(a=>a.hash==='#'+e.target.id);if(link)link.setAttribute('aria-current','true');}}},{rootMargin:'-5% 0px -65% 0px',threshold:0});document.querySelectorAll('main section').forEach(el=>observer.observe(el));}
})();
'''

nav=''.join(f'<a href="#{id}"><span>{n}</span>{title.split('：')[0]}</a>' for id,n,title,_ in sections)
doc=f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="description" content="自建商品 Feed 并直接接入 ChatGPT 的执行方案：申请资料、准入机制、字段合同、系统架构、实施任务与验收。"><meta name="robots" content="noindex,nofollow"><meta name="color-scheme" content="light"><title>ChatGPT 商品 Feed｜自建接入实施方案</title><style>{CSS}</style></head>
<body><a class="skip" href="#main">跳到正文</a><div class="layout"><aside class="sidebar" aria-label="方案目录"><div class="wordmark">COMMERCE / FIELD NOTES</div><p>商品目录分发 · 实施文档</p><nav aria-label="章节导航">{nav}</nav><div class="meta">版本 1.0 · {DATE}<br>公开方案／空白模板<br><a class="back-top" href="#top">返回顶部 ↑</a></div></aside>
<main id="main"><header class="hero" id="top"><div class="eyebrow">IMPLEMENTATION PLAN / PRODUCT FEEDS</div><h1>把商品目录<br>可靠地交付给 ChatGPT<span>Build the feed.<br>Prove the delivery.</span></h1><p class="lede">从申请资料到生产运行，明确谁提供什么、先做哪一步、怎样证明完成。把平台准入、技术交付与真实展示分别验收。</p><div class="hero-meta"><span class="tag fact">官方事实已核对</span><span class="tag proposal">架构与排期为建议</span><span class="tag unknown">直连资格尚未核验</span><span class="tag">2026-10-16 · v1.0</span></div><div class="hero-actions"><a class="button" href="#materials">查看资料诉求</a><a class="button secondary" href="#schedule">进入实施任务</a><button type="button" id="print" class="quiet">打印 / 存为 PDF</button></div></header>
<noscript><p class="callout">正文与下载无需 JavaScript；清单进度和打印按钮需要脚本。可使用浏览器的打印功能。</p></noscript>{''.join(s[3] for s in sections)}<footer>独立实施方案 · 公开内容不含真实商家申请资料或生产凭证。<br>完成方案发布不代表完成 Feed 开发、取得准入批准或实现商品展示。</footer></main></div><script>{JS}</script></body></html>'''
(ROOT/'index.html').write_text(doc,encoding='utf-8')

def write_csv(name, headers, rows):
    with (ROOT/'downloads'/name).open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.writer(f, lineterminator='\n');writer.writerow(headers);writer.writerows(rows)
write_csv('materials-request.csv',['编号','资料组','资料诉求','建议责任人','用途或来源','阻断阶段','当前状态','验收说明'],MATERIALS)
write_csv('implementation-tasks.csv',['任务','阶段','负责人角色','实施动作','交付物','前置依赖','建议估算','实际负责人','状态','证据链接'],[r+('','未开始','') for r in TASKS])
write_csv('field-mapping.csv',['输出字段','要求','业务来源','校验说明','真实源字段','责任人','状态'],[r+('','','待映射') for r in FIELDS])

APPLICATION='''# ChatGPT 商品 Feed 直接接入申请资料模板

版本：2026-10-16。空白模板；不是已提交申请或批准证据。
填妥的文件仅保存于受控私有空间，不提交到公开 GitHub。

## 1. 官方申请表资料

- First name / Last name: [待填]
- Work title: [待填]
- LinkedIn: [待填]
- Work email: [待填]
- Company: [待填]
- Headquarter country: [待填]
- Merchant website: [待填]
- Primary product categories: [待填]
- Unique SKU count / counted at: [待填；说明产品与变体口径]
- Product feed readiness: [未开始 / 样例完成 / 全量校验完成；仅选实际状态]

申请入口：https://chatgpt.com/merchants/
申请后保存平台回执；候补不等于批准。

## 2. English supplementary statement

We are [company], the [merchant / authorized representative] of [merchant domain].
Our catalog contains approximately [count] purchasable items or variants, counted as of [date], in [categories].
Our initial requested scope is [country, language and currency].
The catalog source of truth is [Shopify / ERP / PIM and ownership].
Our current feed readiness is [truthful status]. A representative sample [is / is not yet] available.
We plan to maintain accurate product URLs, variant images, prices, availability and seller details,
with [proposed cadence, to be confirmed] and named operational contacts.
We [do / do not] already distribute through Shopify Catalog or another feed provider.
We seek confirmation on whether a direct feed is appropriate, and how duplicate sources would be reconciled.
Please confirm the approved scope, delivery channel, production connection details, credentials,
schema version, rate and batch limits, processing feedback and urgent product withdrawal procedure.
Business contact: [private contact reference]
Technical contact: [private contact reference]

## 3. 平台接入合同核对

以下是本项目联调问题，不是官方申请表新增必填条件。

- [ ] 批准的主体／域名／品牌／国家／币种
- [ ] 与 Shopify Catalog 和其他 Feed 的优先级、去重与覆盖规则
- [ ] 接受的投递方式：SFTP / API / 其他（以实际答复为准）
- [ ] SFTP 主机、端口、目录、认证、主机指纹、轮换及网络策略
- [ ] API Base URL、权限、版本、限额、批次大小和测试环境
- [ ] 文件 item_id 与 API Product.id / Variant.id 的映射
- [ ] 快照和 API 的覆盖顺序、处理边界及重放方式
- [ ] 接收／拒绝／处理结果的查询方式和可获得证据
- [ ] 搜索资格撤回和紧急下架渠道、预期时效
- [ ] 文件分片、上传完成判断与生产切换要求
- [ ] 市场、域名验证、政策及条件字段限制
- [ ] 事故、终止、删除与服务变更通知方式

## 4. 内部留档

- Application submitted at: [待填]
- Application status: NOT_SUBMITTED / WAITLISTED / APPROVED / NEEDS_INFO / DECLINED
- Evidence reference: [私有批准或回执位置，不复制敏感原文到公开文档]
- Approved scope: [待填]
- Production delivery switch: OFF
- G1 local validation: [未开始 / 进行中 / 通过；证据]
- G2 platform validation: [待批准 / 进行中 / 通过；证据]
- G3 operations readiness: [未开始 / 进行中 / 通过；证据]

## 5. 不可误填的结论

最低 GMV、最低 SKU、评分标准和审批 SLA：所查官方材料未公开。
普通模型 API Key 是否具有 Feed 权限：不得假定；以平台分配权限为准。
SKU 数量是申请资料，不代表达到某个数字就必然获批。
符合格式、传输成功、平台接受、平台处理和展示是不同状态。
'''
(ROOT/'downloads'/'application-template.md').write_text(APPLICATION,encoding='utf-8')
(ROOT/'sources.json').write_text(json.dumps({'verified_at':DATE,'sources':[{'id':i,'title':t,'url':u,'scope':n} for i,t,u,n in SOURCES]},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(ROOT/'.nojekyll').touch()
(ROOT/'robots.txt').write_text('User-agent: *\nAllow: /\n',encoding='utf-8')
print(f'Built {len(sections)} sections, {len(MATERIALS)} material requests, {len(TASKS)} tasks, {len(FIELDS)} field mappings.')
