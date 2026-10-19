# ChatGPT 商品 Feed 自建接入实施方案与官方规范汇总

> 本文档基于 OpenAI / ChatGPT 官方 Commerce 与商家接入文档（https://chatgpt.com/merchants/ 及 https://developers.openai.com/commerce/）整理，实事求是汇总从**资质申请**到 **Feed 格式与技术准备**的完整要求。

- 在线文档站点：https://igocc.github.io/chatgpt-product-feed-plan/
- 官方规范基线日期：2026-10-16
- 事实依据来源：OpenAI Commerce Specs & Guides / Shopify Help

---

## 一、 商家资质与官方申请准备

### 1. 申请入口与准入机制
* **官方申请入口**：`https://chatgpt.com/merchants/`
* **当前准入模式**：目前商品 Feed 直连面向**已获批的合作伙伴（Approved Partners）**开放。普通商家通过该入口提交后进入**候补名单（Waitlist）**由人工审核，并非自动开通。
* **API Key 权限隔离**：用于大模型调用的普通 OpenAI Model API Key **不具备**商品 Feed 提交权限；接入权限需待审批通过后单独核发。
* **Shopify 原生分发区别**：若商品已在 Shopify 销售且面向美国市场，Shopify Catalog 已具备原生集成通道；自建直连 Feed 适用于有多源目录、独立数据清洗或定制更新频率诉求的场景。

### 2. 官方申请表需准备的 10 项核心材料
提交官方申请表时，需提前备齐以下真实企业与业务信息：
1. **申请联系人姓名**：First Name 与 Last Name。
2. **联系人职务**：Work Title。
3. **职业履历链接**：LinkedIn Profile URL。
4. **工作邮箱**：企业域名工作邮箱（Work Email）。
5. **公司主体名称**：合法注册的公司英文名称（Company Name）。
6. **总部所在国家**：Headquarter Country。
7. **商家官方网站**：公开可访问的独立站官网（Merchant Website）。
8. **主营商品类目**：Primary Product Categories。
9. **目录规模**：唯一可售 SKU 数量（Unique SKU Count）及统计基准日期（需明确区分母商品数与独立变体数）。
10. **Feed 准备就绪状态**：如实勾选当前状态（未开始 / 样例就绪 / 全量校验完成）。

### 3. 官方未公开的事项（实事求是，不作臆测）
* **无公开门槛**：OpenAI 官方从未公布最低 GMV、最低 SKU 门槛或量化打分规则。
* **无承诺时效**：官方未承诺申请审核周期（SLA），提交申请不代表必然获批。
* **无公开 IP 白名单规则**：直连鉴权由平台统一核准后下发参数，非简单的服务器公网 IP 加白。

---

## 二、 技术投递通道准备

官方提供两种接入通道，推荐模式为：**每日全量文件快照（File Upload） + 日内 API 增量更新（API Upsert）**。

### 1. 文件投递通道规范（首选 / 基础通道）
* **传输协议**：通过 **SFTP** 推送至 OpenAI 根目录。
* **支持格式**：
  * **首选**：`parquet`（推荐 `zstd` 压缩）；
  * **兼容支持**：`jsonl.gz`、`csv.gz`、`tsv.gz`。
* **文本编码**：严格使用 **UTF-8**。
* **文件名稳定性（强制要求）**：必须使用**固定文件名**（例如 `products.jsonl.gz`），每次更新直接覆盖原文件。严禁每次生成带时间戳或随机后缀的文件名。
* **多文件分片建议（Sharding）**：
  * 单分片商品上限建议 ≤ 50 万条；
  * 单分片体积建议保持在 500MB 以下；
  * 分片文件名集合需保持稳定（如 `shard-001.jsonl.gz`, `shard-002.jsonl.gz`），更新时原位覆盖。
* **目录级处理机制**：SFTP 根目录代表当前全量目录；上传完成后系统自动检测并处理，无需投递完成标记文件（Completion Marker）。

### 2. 留存、撤回与更新生命周期规则
* **14 天容错留存机制**：从快照文件中遗漏的商品**不会被即时删除**，OpenAI 最多保留 14 天的最近处理记录，以防止网络中断或分片上传延迟导致误下架。
* **主动取消搜索资格**：若商品下架、售罄或不再允许被 ChatGPT 检索，必须在快照中显式标记字段 `is_eligible_search=false`。
* **物理清除**：在连续 14 天的全量快照中完全排除该商品，历史保留记录将自然过期。

### 3. API 增量通道规范（条件通道）
* **端点与权限**：必须获批后获取专用 Base URL 与专用认证凭据。
* **数据格式**：支持嵌套商品与变体结构（Products API），支持 PATCH 操作进行增量 upsert。
* **金额单位关键差异**：
  * 文件 Feed 中金额为主单位字符串（例如 `"79.99 USD"`）；
  * API 中金额字段 `price.amount` 为**货币最小单位整数**（例如 79.99 USD 需填入 `7999`，禁止传浮点数或带小数点的字符串）。

---

## 三、 商品 Feed 数据格式与字段规范

Feed 中的每一行必须且仅代表**一件独立可购买的商品或具体变体（Purchasable Item or Variant）**。

### 1. 基础必填字段（9 项）
任何有效的商品发现 Feed 必须完整包含以下 9 个基础字段：

| 字段名称 | 数据类型 | 格式要求与说明 | 规范示例 |
| :--- | :--- | :--- | :--- |
| `item_id` | String | 变体级全局唯一且稳定的不可变 ID，不得随标题/价格变更而改变。 | `"TRAIL-BLK-10"` |
| `title` | String | 商品真实名称（包含该行变体的特征属性），建议 ≤ 150 字符，不堆砌关键词。 | `"Trail running shoes — black, size 10"` |
| `description` | String | 客观真实的事实性纯文本描述，建议 ≤ 5,000 字符，不支持 HTML 标签。 | `"Waterproof trail shoes with a rubber outsole."` |
| `url` | String (URL) | 该商品/变体的公开落地页绝对 HTTPS 地址（需默认选中该具体变体）。 | `"https://example.com/products/trail?color=black&size=10"` |
| `brand` | String | 页面展示的真实品牌名称。 | `"Northline"` |
| `seller_name` | String | 提供此报价的真实卖家名称。 | `"Northline Outdoor"` |
| `image_url` | String (URL) | 对应此变体的主图公开直链（JPEG/PNG 格式，公网可直接访问）。 | `"https://example.com/images/trail-black.jpg"` |
| `availability` | String | 当前实时库存状态，仅允许 5 个枚举值：<br>`in_stock` / `out_of_stock` / `pre_order` / `backorder` / `unknown` | `"in_stock"` |
| `price` | String (Money) | 正规常规售价，格式为 `金额 ISO币种`，保留 2 位小数。 | `"79.99 USD"` |

### 2. 多规格变体商品组合规范（条件必填）
对于包含颜色、尺码等多变体的商品，除上述 9 个基础字段外，每行必须提供以下变体控制字段：

| 变体字段 | 数据类型 | 填写要求 | 规范示例 |
| :--- | :--- | :--- | :--- |
| `group_id` | String | 同一商品所有变体共享的父级稳定 ID（**必须与任一变体的 `item_id` 不同**）。 | `"TRAIL"` |
| `listing_has_variations` | Boolean | 只要属于多变体行，固定为 `true`。 | `true` |
| `variant_dict` | Object (Map) | 具体选择维度的键值对（统一维度命名，同一组内组合唯一）。 | `{"color": "Black", "size": "10"}` |
| `offer_id` | String | 稳定的报价标识（可选，用于区分同一落地页的不同卖家报价，**严禁把价格编入 offer_id**）。 | `"northline-TRAIL-BLK-10"` |

### 3. 常用可选字段与业务属性

| 业务分类 | 字段名 | 类型 | 说明与规范要求 |
| :--- | :--- | :--- | :--- |
| **检索控制** | `is_eligible_search` | Boolean | `true`（默认）允许检索；`false` 禁止在 ChatGPT 检索中呈现。 |
| **促销价格** | `sale_price` | String | 当前生效促销价（需满足：大于 0、低于 regular price、同币种），如 `"59.99 USD"`。 |
| **标准条码** | `gtin` | String | 8/12/13/14 位标准条码（UPC/EAN），需保留前导零且校验位有效。 |
| **厂商料号** | `mpn` | String | 制造商零件编号，需与 `brand` 配合提供。 |
| **成色状态** | `condition` | String | 枚举：`new` / `refurbished` / `used`。 |
| **物流运费** | `shipping_price` | String | 运费金额字符串，如 `"5.00 USD"`（0.00 代表包邮，留空代表未提供）。 |
| **退换货保障** | `accepts_returns` | Boolean | 是否支持退换货（`true` / `false`）。 |
| **退换时限** | `return_deadline_in_days` | Integer | 退换货有效天数整数（如 `30`）。 |
| **政策链接** | `return_policy` | String (URL) | 退换货政策详情页的 HTTPS 链接。 |
| **商品评价** | `review_count` | Integer | 真实的商品评价总数（非店铺评价，如 `254`）。 |
| **评分** | `star_rating` | String (Decimal)| 0~5 分制的平均评分，保留两位小数（如 `"4.50"`）。 |

---

## 四、 官方合规与商品禁售政策（Prohibited Products Policy）

OpenAI 明确规定，向 ChatGPT 提交的商品必须符合法律法规并适合大众群体。**禁止提交以下品类**：
1. **成人与色情内容**；
2. **年龄受限商品**：酒精类饮料、烟草/尼古丁、博彩相关制品；
3. **危险有害物品与武器**：爆炸物、枪支弹药及相关攻击性配件；
4. **处方药与医疗监管品**：处方药、未经许可的医疗设备；
5. **违规金融产品**：未经牌照的金融、借贷或虚拟币理财衍生品；
6. **假冒伪劣与欺诈性商品**：侵犯知识产权或虚假宣传商品。

*违规处理：OpenAI 明确表示若发现违规商品，将直接采取移除商品或永久封禁商家 ChatGPT 展现资格的惩治措施。*

---

## 五、 本地交付与工具说明

* `build.py`：本地静态方案构建脚本（执行 `python3 build.py` 重新生成 `index.html`）。
* `downloads/`：
  * `application-template.md`：英文官方申请表填报与答复模板；
  * `field-mapping.csv`：15 项核心字段映射与业务归属表；
  * `materials-request.csv`：24 项接入资料准备清单；
  * `implementation-tasks.csv`：19 项工程落地与阶段验收任务表。
* `sources.json`：12 份官方事实依据映射索引。
