# 🛠️ Network Diagnostic Toolkit

一個用 Python 製作的跨平台網路診斷工具，能快速檢測區網裝置、網路連線狀況、社群封鎖、路由追蹤與網速測試，並自動將結果回報至指定的伺服器。

---

## 📦 功能說明

| 功能模組             | 說明 |
|----------------------|------|
| 區網裝置掃描         | 掃描區網中可達裝置 IP，透過 ping + ARP 表分析 |
| Port & 社群封鎖檢測 | 檢查常用 DNS/HTTP/社群網站連接狀況與封鎖情形 |
| 網速測試             | 使用 Speedtest API 或 CLI 進行上下傳與延遲測試 |
| Traceroute 路由追蹤  | 執行跨平台 `traceroute` 解析封包跳數與節點 |
| 統整回報             | 以 HTTPS POST 將診斷結果送至指定 API（自架伺服器） |

---

## 🖥️ 系統需求

- Python 3.7+
- 作業系統：Windows / Linux / macOS
- 套件依賴：

  ```bash
  pip install speedtest-cli requests
  
---
