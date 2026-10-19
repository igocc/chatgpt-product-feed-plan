# ChatGPT 商品 Feed 官方接入指南与数据规范

> 依据 OpenAI 官方文档（入口：https://chatgpt.com/merchants/ | 规范：https://developers.openai.com/commerce/）整理，聚焦商家直接向 ChatGPT 申请与投递商品 Feed 的完整要求。

---

## 一、 官方申请与资质准备

### 1. 申请入口与机制
* **官方入口**：`https://chatgpt.com/merchants/`
* **准入方式**：采用**合作伙伴审核制（Approved Partners）**。商家在线提交申请后进入审核候补名单（Waitlist），由 OpenAI 人工评估。
* **权限说明**：普通 OpenAI 模型 API Key（用于调用大模型）**无**商品 Feed 提交权限；接入权限需在申请获批后由官方单独下发。
* **官方未公开项**：官网未公布最低 GMV、最低有效 SKU 数量门槛或审核时限（SLA）。

### 2. 申请表所需准备材料（10 项）
1. **联系人姓名**：First Name、Last Name
2. **联系人职务**：Work Title
3. **工作邮箱**：企业域名邮箱（Work Email）
4. **职业履历主页**：LinkedIn Profile URL
5. **公司名称**：合法注册的公司英文名称（Company Name）
6. **总部所在国家**：Headquarter Country
7. **商家官网**：公开可访问的官方网站（Merchant Website）
8. **主营类目**：Primary Product Categories
9. **目录规模**：唯一可购买 SKU 数量及统计日期（区分商品数与独立变体数）
10. **Feed 准备状态**：未开始 / 样例就绪 / 全量校验完成（按实际进度如实勾选）

---

## 二、 Feed 传输与投递规范

官方支持两种模式：**全量文件快照（SFTP，主通道）** 与 **增量更新（API，辅助通道）**。

### 1. SFTP 文件投递（核心通道）
* **传输方式**：通过 SFTP 推送至 OpenAI 分配的根目录。
* **文件格式**：首选 `parquet`（建议 `zstd` 压缩），支持 `jsonl.gz`、`csv.gz`、`tsv.gz`。
* **文本编码**：必须为 `UTF-8`。
* **文件命名**：**必须使用固定稳定文件名**（如 `products.jsonl.gz`），每次更新原位覆盖，不可使用带时间戳的动态文件名。
* **分片建议**：多文件分片时，单分片建议 ≤ 50 万条商品、体积 < 500MB，且分片文件名保持固定。
* **更新频率**：全量快照建议至少每日更新一次；文件上传停止后系统自动拉取，无需发送完成标记。

### 2. 生命周期与下架机制
* **14 天容错留存**：快照中遗漏的商品不会立即删除，系统最长保留 14 天，防止偶发漏传导致商品下架。
* **主动取消检索**：若商品下架、售罄或需立刻停止展示，在快照中显式传值 `"is_eligible_search": false`。
* **物理清除**：连续 14 天以上的全量快照中完全排除该商品，系统将自动过期清除。

### 3. API 增量通道
* **权限获取**：获批后获取专用 API Base URL 与认证凭证。
* **操作方式**：通过 Products API 发送 PATCH 请求做日内增量 Upsert。
* **金额格式差异**：
  * 文件 Feed 中为**主单位字符串**（如 `"79.99 USD"`）；
  * API 中必须传**货币最小单位整数**（如 79.99 USD 需传整数 `7999`）。

---

## 三、 Feed 数据格式与字段规范

数据粒度：**每行必须对应一件独立可售的商品或具体变体（Purchasable item or variant）**。

### 1. 基础必填字段（9 个）

| 字段名 | 类型 | 说明与规范要求 | 示例 |
| :--- | :--- | :--- | :--- |
| `item_id` | String | 变体级全局唯一且稳定的不可变 ID，不随标题或价格变动。 | `"TRAIL-BLK-10"` |
| `title` | String | 商品完整标题（含变体特征），纯文本，建议 ≤ 150 字符。 | `"Trail running shoes — black, size 10"` |
| `description` | String | 真实客观的产品描述，纯文本无 HTML，建议 ≤ 5,000 字符。 | `"Waterproof trail shoes with rubber outsole."` |
| `url` | String (URL) | 该具体变体的公开落地页绝对 HTTPS 链接（默认选中该变体）。 | `"https://example.com/p/trail?color=black&size=10"` |
| `brand` | String | 页面展示的真实品牌名。 | `"Northline"` |
| `seller_name` | String | 实际销售与履约的卖家名称。 | `"Northline Outdoor"` |
| `image_url` | String (URL) | 对应变体的主图直链（公网可直接访问的 JPEG 或 PNG）。 | `"https://example.com/img/trail-black.jpg"` |
| `availability` | String | 库存状态枚举，仅限：<br>`in_stock` / `out_of_stock` / `pre_order` / `backorder` / `unknown` | `"in_stock"` |
| `price` | String (Money)| 常规售价，格式为 `金额 货币代码`，保留 2 位小数。 | `"79.99 USD"` |

### 2. 多规格变体字段（多属性商品必填）
若商品包含颜色、尺码等多个属性，除上述 9 个字段外，还需包含：

| 字段名 | 类型 | 说明与规范要求 | 示例 |
| :--- | :--- | :--- | :--- |
| `group_id` | String | 同款母商品 ID（**必须与任意变体的 `item_id` 不同**）。 | `"TRAIL"` |
| `listing_has_variations` | Boolean | 只要属于多变体行，固定设为 `true`。 | `true` |
| `variant_dict` | Object | 具体规格键值对，组内组合必须唯一。 | `{"color": "Black", "size": "10"}` |
| `offer_id` | String | 报价标识（可选，用于区分不同卖家，**严禁把价格编入 ID**）。 | `"northline-TRAIL-BLK-10"` |

### 3. 常用可选字段

| 业务分类 | 字段名 | 类型 | 说明 |
| :--- | :--- | :--- | :--- |
| **检索控制** | `is_eligible_search` | Boolean | `true`（默认可检索）；`false`（取消搜索资格，用于下架）。 |
| **促销价格** | `sale_price` | String (Money)| 当前生效促销价（需大于 0、低于 regular price、同币种），如 `"59.99 USD"`。 |
| **标准条码** | `gtin` | String | 8/12/13/14 位标准商品条码（UPC/EAN），需校验位正确，保留前导零。 |
| **厂商零件号**| `mpn` | String | 制造商零件编号，需与 `brand` 配合。 |
| **成色** | `condition` | String | 枚举：`new` / `refurbished` / `used`。 |
| **运费** | `shipping_price` | String (Money)| 运费金额，如 `"5.00 USD"`（`"0.00 USD"` 表示免运费）。 |
| **退换保障** | `accepts_returns` | Boolean | 是否支持退换货（`true` / `false`）。 |
| **退换政策** | `return_policy` | String (URL) | 退换货政策详情页 HTTPS 链接。 |
| **评价与评分**| `review_count` / `star_rating` | Integer / Decimal | 真实评价数（如 `254`）与 0~5 分制均分（如 `"4.50"`）。 |

---

## 四、 官方禁售商品政策（Prohibited Products Policy）

提交给 ChatGPT 的商品必须合法合规且适合大众，**以下品类明确禁止接入**：
1. **成人与色情内容**；
2. **年龄限制商品**：酒精饮品、烟草/尼古丁产品、博彩相关；
3. **危险品与武器**：爆炸物、枪支武器及管制配件；
4. **处方药与医疗监管品**：处方药、未经合规认证的医疗器械；
5. **违规金融产品**：未经许可的金融借贷、加密货币衍生品；
6. **假冒伪劣与欺诈性商品**：侵权仿品、虚假陈述商品。

*违规处理：官方将采取直接下架相关商品或永久封禁商家 ChatGPT 展示资格的处理措施。*
