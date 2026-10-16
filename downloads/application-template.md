# ChatGPT 商品 Feed 直接接入申请资料模板

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
