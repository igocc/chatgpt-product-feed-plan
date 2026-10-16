# ChatGPT 商品 Feed 自建接入实施方案

独立 HTML 技术方案，覆盖商家申请、合作伙伴准入、商品数据、系统架构、投递、撤回、实施任务、验收与运维。

- 站点：https://igocc.github.io/chatgpt-product-feed-plan/
- 事实核对日期：2026-10-16
- `index.html`：内嵌样式和脚本，正文可离线阅读。
- `downloads/`：公开空白模板，填写后应保存到私有协作空间。
- `sources.json`：官方来源与适用范围。
- `build.py`：仅生成静态文档，不连接 Shopify 或 OpenAI，也不提交 Feed。

重建：`python3 build.py`

本地预览：`python3 -m http.server 8876 --bind 127.0.0.1`

公开文件不包含真实企业联系人、商品明细、申请回执、凭证或生产配置。
浏览器清单只在本机保存勾选状态；不会上传或发起申请。

方案发布不代表 Feed 系统已建设、OpenAI 直连已批准或商品已在 ChatGPT 展示。
