---
title: 网页数据来源的分类
date: 2026-06-12T00:00:00+08:00
draft: false
categories:
  - 数据来源判断
tags:
  - Python
  - 爬虫
  - 数据来源判断
  - Chrome DevTools
  - JSON
summary: 本文整理网页数据来源的常见分类，帮助爬虫初学者判断数据到底来自 HTML、接口、脚本、文件还是实时连接。
---

## 这篇文章解决什么问题

做爬虫之前，第一步不是写代码，而是判断数据从哪里来。

同样是在浏览器页面里看到一段数据，它可能来自不同位置：

1. HTML 页面源码
2. JSON 接口
3. JavaScript 脚本里的内嵌数据
4. 浏览器运行 JavaScript 后二次请求的数据
5. WebSocket 或 SSE 实时推送
6. CSV、Excel、PDF、图片等文件
7. GraphQL 接口
8. 需要登录后才能访问的用户数据

如果数据来源判断错了，后面的代码通常会走偏。

常见问题包括：

- 浏览器能看到数据，但 `requests` 拿不到；
- 页面源码里搜索不到目标字段；
- 明明请求成功了，却没有想要的数据；
- 分页参数找错，导致只能采集第一页；
- 把 JS 渲染问题误判成反爬；
- 直接上 Selenium，但其实一个 JSON 接口就能解决。

本文的目标是建立一个基础分类框架：先判断网页数据属于哪一类，再决定使用什么工具和采集方式。

## 它是什么

网页数据来源，指的是浏览器最终显示的数据，最初是从哪里取得的。

浏览器页面不是一个单一文件。一个网页通常由多种资源组成：

- HTML：页面骨架
- CSS：样式
- JavaScript：交互逻辑
- 图片、字体、视频等静态资源
- JSON 接口：结构化数据
- WebSocket：实时消息
- PDF、CSV、Excel 等文件资源

爬虫要关心的不是“页面看起来是什么样”，而是“目标字段最早出现在哪里”。

例如，一个商品标题出现在页面上，可能有三种情况：

1. 标题直接写在 HTML 里；
2. 标题来自某个 JSON 接口，浏览器拿到后再渲染；
3. 标题藏在某个 `<script>` 标签中的 JSON 数据里。

这三种情况对应的采集方法不同。

## 它解决什么问题

网页数据来源分类主要解决三个问题。

第一，减少无效代码。

很多初学者一看到网页，就直接写：

```python
import requests
from bs4 import BeautifulSoup

url = "https://example.com"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")
print(soup.text)
```

如果目标数据本来不在 HTML 里，这段代码无论怎么改选择器，都拿不到数据。

第二，选择合适工具。

不同数据来源对应不同工具：

| 数据来源 | 常用工具 |
| --- | --- |
| HTML 直出 | requests + BeautifulSoup/lxml |
| JSON 接口 | requests + json/pandas |
| JS 渲染 | Chrome DevTools 判断接口，必要时 Playwright/Selenium |
| 内嵌 JSON | requests + 正则/BeautifulSoup/json |
| WebSocket | DevTools 观察 WS，必要时 websocket-client |
| CSV/Excel | requests + pandas |
| PDF | requests + pdfplumber/pymupdf |
| GraphQL | requests 发送 POST 请求 |

第三，控制采集边界。

不是所有浏览器能看到的数据都适合采集。遇到登录后数据、个人信息、付费内容、验证码、接口权限校验时，要优先检查网站规则、服务条款、版权和隐私边界。学习阶段建议使用公开网页、练习站点、官方 API 或自己搭建的测试站点。

## 在爬虫中为什么重要

数据来源判断是爬虫流程的入口判断。

它决定后面四件事：

1. 请求什么地址；
2. 带什么参数；
3. 用什么解析方式；
4. 是否存在权限、合规或反爬风险。

如果把数据来源判断错，后续问题会被错误归因。

例如：

- HTML 里没有数据，不一定是网站反爬，可能只是数据来自接口；
- `response.text` 为空，不一定是编码问题，可能请求地址不是数据接口；
- 只能拿到第一页，不一定是循环写错，可能分页参数找错；
- 浏览器显示实时变化，不一定需要刷新页面，可能是 WebSocket 推送。

所以，正确流程应该是：

```text
先判断数据来源 → 再分析请求 → 再写最小代码 → 再扩展分页、保存和清洗
```

不要一开始就写完整爬虫。

## 常见网页数据来源分类

### 1. HTML 直出数据

HTML 直出，指目标数据直接存在于服务器返回的 HTML 文档中。

简单理解：你右键查看网页源代码，或者用 `requests.get(url).text` 获取页面内容，里面就能搜索到目标字段。

典型特征：

- Network 面板里目标页面类型通常是 `Doc`；
- Response 中能直接看到标题、价格、日期等字段；
- 禁用 JavaScript 后，页面主要数据仍然存在；
- `requests` 请求页面后可以直接解析。

适合工具：

- `requests`
- `BeautifulSoup`
- `lxml`

最小示例：

```python
import requests
from bs4 import BeautifulSoup

url = "https://example.com"
response = requests.get(url, timeout=10)
response.encoding = response.apparent_encoding

soup = BeautifulSoup(response.text, "html.parser")
title = soup.find("title").get_text(strip=True)
print(title)
```

这段代码做了三件事：

1. 请求 HTML 页面；
2. 用 BeautifulSoup 解析页面结构；
3. 提取 `<title>` 标签文本。

判断重点：目标字段必须在 HTML 响应里真实存在。

### 2. JSON 接口数据

JSON 接口可以理解为网站给前端页面提供数据的地址。

在网页中，前端通过 XHR 或 Fetch 请求接口，接口返回 JSON 格式的数据，浏览器再把这些数据渲染到页面上。

典型特征：

- Network 面板中请求类型常见为 `Fetch/XHR`；
- Response 或 Preview 里是 `{}` 或 `[]` 结构；
- 数据字段有明显的 key，例如 `title`、`price`、`items`、`list`；
- 页面 HTML 源码里搜索不到字段，但接口响应里能看到。

适合工具：

- `requests`
- `response.json()`
- `pandas.json_normalize`

最小示例：

```python
import requests

url = "https://example.com/api/items"
response = requests.get(url, timeout=10)
data = response.json()

print(data)
```

这段代码做了三件事：

1. 请求 JSON 接口；
2. 把响应内容解析为 Python 对象；
3. 打印接口返回的数据。

判断重点：不要只看页面 URL，要找到真正返回数据的接口 URL。

### 3. 内嵌 JSON 数据

内嵌 JSON，指数据没有通过单独接口返回，而是直接藏在 HTML 的 `<script>` 标签中。

常见形式包括：

```html
<script>
window.__INITIAL_STATE__ = {"items":[{"title":"示例标题"}]}
</script>
```

或者：

```html
<script id="__NEXT_DATA__" type="application/json">
{"props":{"pageProps":{"items":[]}}}
</script>
```

典型特征：

- 页面源码中能搜索到目标字段；
- 字段不在普通 HTML 标签里，而在 `<script>` 中；
- 数据通常是 JSON 或接近 JSON 的 JavaScript 对象；
- 常见于前端框架页面，例如 Next.js、Nuxt、React、Vue SSR 页面。

适合工具：

- `requests`
- `BeautifulSoup`
- `json`
- 必要时使用正则提取脚本内容

最小示例：

```python
import json
from bs4 import BeautifulSoup

html = '''
<html>
<script id="data" type="application/json">
{"title": "示例标题", "count": 3}
</script>
</html>
'''

soup = BeautifulSoup(html, "html.parser")
script_text = soup.find("script", id="data").get_text(strip=True)
data = json.loads(script_text)

print(data["title"])
```

这段代码做了三件事：

1. 找到指定 `<script>` 标签；
2. 读取其中的 JSON 字符串；
3. 转成 Python 字典后取字段。

判断重点：不要把所有 `<script>` 都当成无用代码，很多页面会把首屏数据放在脚本里。

### 4. JavaScript 渲染数据

JavaScript 渲染，指服务器返回的 HTML 只是空壳，真实数据需要浏览器执行 JavaScript 后才显示。

典型特征：

- `requests.get(url).text` 里没有目标数据；
- 查看页面源代码也没有目标字段；
- DevTools 的 Elements 面板能看到数据，但 Source 或 Response 中看不到；
- Network 面板的 Fetch/XHR 里可能能找到数据接口。

这里要注意：JS 渲染不是一种最终数据来源，它只是页面显示方式。真正的数据往往仍然来自 JSON 接口、内嵌数据或 WebSocket。

合理判断顺序：

1. 先看 HTML Response；
2. 再看 Fetch/XHR；
3. 再搜索全部 Network 响应；
4. 仍然找不到时，再考虑浏览器自动化工具。

适合工具：

- 首选：Chrome DevTools 找接口，再用 `requests` 请求接口；
- 次选：Playwright 或 Selenium 渲染页面后提取。

不建议一开始就上 Selenium。浏览器自动化成本更高，速度更慢，也更容易受页面变化影响。

### 5. 分页接口数据

分页接口不是单独的数据格式，而是一类常见请求模式。

列表页通常不会一次返回全部数据，而是通过参数控制页数或偏移量。

常见分页参数：

| 参数形式 | 含义示例 |
| --- | --- |
| `page=1` | 第 1 页 |
| `pageNo=1` | 第 1 页 |
| `offset=0` | 从第 0 条开始 |
| `limit=20` | 每页 20 条 |
| `cursor=xxx` | 游标分页 |
| `last_id=xxx` | 从某个 ID 之后继续加载 |

典型特征：

- 点击下一页或滚动加载时，Network 出现新的 Fetch/XHR 请求；
- URL 或 Payload 中某个参数发生变化；
- Response 中返回列表数组和是否还有下一页的信息；
- 有些接口返回 `has_next`、`total`、`next_cursor` 等字段。

最小示例：

```python
import requests

url = "https://example.com/api/items"

for page in range(1, 4):
    params = {"page": page}
    response = requests.get(url, params=params, timeout=10)
    data = response.json()
    print(page, data)
```

这段代码做了三件事：

1. 构造分页参数；
2. 循环请求不同页码；
3. 打印每页返回结果。

判断重点：分页不是猜参数，而是观察浏览器请求中哪个参数在变化。

### 6. GraphQL 接口数据

GraphQL 是一种接口查询方式。它通常不是通过多个 REST URL 获取不同资源，而是向同一个接口发送查询语句，让后端返回指定字段。

典型特征：

- 请求方法通常是 `POST`；
- 请求 URL 可能类似 `/graphql`；
- Payload 中出现 `query`、`variables`、`operationName`；
- Response 里通常包含 `data` 字段。

适合工具：

- Chrome DevTools 分析 Payload；
- `requests.post()` 发送 JSON 请求。

最小示例：

```python
import requests

url = "https://example.com/graphql"
payload = {
    "query": "query { items { title } }",
    "variables": {}
}

response = requests.post(url, json=payload, timeout=10)
print(response.json())
```

这段代码做了三件事：

1. 向 GraphQL 地址发送 POST 请求；
2. 在请求体中提交查询语句；
3. 读取 JSON 响应。

判断重点：GraphQL 重点不只在 URL，还在请求体中的 `query` 和 `variables`。

### 7. WebSocket 或 SSE 实时数据

WebSocket 和 SSE 常用于实时数据推送。

常见场景包括：

- 股票行情；
- 在线聊天；
- 实时通知；
- 体育比分；
- 直播弹幕；
- 交易盘口。

典型特征：

- Network 面板中出现 `WS` 类型；
- WebSocket 连接建立后，不断出现 Frames 消息；
- 页面数据不刷新也会变化；
- 普通 `requests.get()` 通常拿不到持续推送内容。

SSE 常见特征：

- 请求头或响应头中可能出现 `text/event-stream`；
- 连接长时间不断开；
- 服务端持续推送事件文本。

判断重点：实时数据不等于普通分页接口。先确认是否有学习和合规必要，不要对真实平台做高频连接或模拟交易类请求。

### 8. 文件型数据：CSV、Excel、PDF、图片

有些网页不是直接展示结构化 HTML 或 JSON，而是提供文件下载。

常见文件类型：

- CSV
- Excel
- PDF
- Word
- 图片
- 压缩包

典型特征：

- 点击按钮后下载文件；
- Network 中请求返回的 `Content-Type` 不是 `text/html` 或 `application/json`；
- Response 可能显示乱码或二进制内容；
- Headers 中可能有 `Content-Disposition: attachment`。

适合工具：

| 文件类型 | 常用处理工具 |
| --- | --- |
| CSV | pandas.read_csv |
| Excel | pandas.read_excel / openpyxl |
| PDF | pdfplumber / pymupdf |
| 图片 | requests 保存，必要时人工判断或 OCR |
| ZIP | zipfile |

最小示例：

```python
import requests

url = "https://example.com/data.csv"
response = requests.get(url, timeout=10)

with open("data.csv", "wb") as f:
    f.write(response.content)

print("保存完成")
```

这段代码做了三件事：

1. 请求文件地址；
2. 使用二进制方式保存内容；
3. 把文件写入本地。

判断重点：文件下载要使用 `response.content`，不要直接用 `response.text` 保存二进制文件。

### 9. 登录后数据和权限数据

登录后数据指只有特定账号登录后才能看到的数据。

典型特征：

- 无痕窗口无法直接访问；
- 请求中需要 Cookie、Token 或 Authorization；
- 不同账号看到的数据不同；
- 数据可能涉及个人隐私、订单、后台管理或内部信息。

这类数据要谨慎处理。

学习时可以研究 Cookie、Session、登录状态的原理，但不应采集他人账号数据，不应绕过权限，不应绕过付费，不应批量采集个人信息。

判断重点：能看到不等于能采集，能请求不等于可以合法使用。

## 如何判断它是否存在

可以用 Chrome DevTools 按下面流程判断。

### 第 1 步：打开 Network 面板

打开网页后按 `F12`，进入 Chrome DevTools，选择 Network 面板。

建议勾选：

- Preserve log：保留跳转前后的请求记录；
- Disable cache：禁用缓存，避免看到旧请求。

然后刷新页面。

### 第 2 步：先看 Doc 请求

找到页面主文档请求，通常类型是 `Doc`。

检查它的 Response：

- 如果目标字段在 Response 中，优先判断为 HTML 直出或内嵌 JSON；
- 如果字段在普通标签里，是 HTML 直出；
- 如果字段在 `<script>` 里，可能是内嵌 JSON；
- 如果完全找不到，继续看 Fetch/XHR。

### 第 3 步：筛选 Fetch/XHR

点击 Network 面板中的 Fetch/XHR。

逐个查看：

- Preview：是否有结构化字段；
- Response：是否能搜索到目标文本；
- Headers：请求 URL、请求方法、Content-Type；
- Payload：POST 请求参数、分页参数、查询条件。

如果在某个接口 Response 中找到目标字段，这个接口就是重点分析对象。

### 第 4 步：操作页面触发请求

不要只刷新页面。还要主动操作：

- 点击下一页；
- 修改搜索条件；
- 滚动到底部；
- 点击详情；
- 切换筛选项。

观察 Network 中新增了哪些请求。

如果每次操作都会出现新的接口请求，说明数据很可能来自动态接口。

### 第 5 步：搜索目标字段

在 Network 面板中，可以使用搜索功能查找目标文本。

判断逻辑：

```text
字段在 Doc Response 中 → HTML 直出或内嵌 JSON
字段在 Fetch/XHR Response 中 → JSON 接口
字段只在 Elements 中出现 → 可能是 JS 渲染后生成，需要继续找接口
字段在 WS Frames 中出现 → WebSocket 推送
字段在下载文件中出现 → 文件型数据
```

### 第 6 步：禁用 JavaScript 交叉验证

可以临时禁用 JavaScript 后刷新页面。

如果禁用 JavaScript 后数据仍然显示，说明数据大概率不是纯前端渲染。

如果禁用 JavaScript 后数据消失，说明页面显示依赖 JS，但仍要继续判断数据是来自接口、内嵌 JSON，还是实时连接。

## 最小判断示例

假设你要采集一个列表页的标题。

判断流程可以这样写成记录：

```text
目标字段：文章标题
页面 URL：https://example.com/articles

检查结果：
1. Doc Response 中没有搜索到标题
2. Fetch/XHR 中发现 /api/articles?page=1
3. Preview 中存在 list 数组
4. list 每一项包含 title、date、url 字段
5. 点击下一页后 page 从 1 变成 2

结论：
数据来源是 JSON 分页接口，不是 HTML 直出。
```

对应的最小代码：

```python
import requests

url = "https://example.com/api/articles"
params = {"page": 1}

response = requests.get(url, params=params, timeout=10)
data = response.json()

for item in data["list"]:
    print(item["title"])
```

这段代码做了三件事：

1. 请求文章列表接口；
2. 解析 JSON 数据；
3. 遍历列表并打印标题。

真正写爬虫前，应先确保接口地址、参数、字段路径都经过 DevTools 验证。

## 常见误区

### 误区 1：把 Elements 当成原始数据来源

Elements 面板显示的是浏览器最终渲染后的 DOM，不等于服务器原始响应。

`requests` 看到的是服务器返回内容，不会自动执行浏览器里的 JavaScript。

所以，Elements 中有数据，不代表 `requests.get(url).text` 中也有数据。

### 误区 2：页面 URL 就是数据 URL

很多现代网站的页面 URL 只是入口。

真实数据可能来自另一个接口，例如：

```text
页面 URL：https://example.com/articles
接口 URL：https://example.com/api/articles?page=1
```

写爬虫时要请求数据接口，而不是盲目请求页面 URL。

### 误区 3：一遇到拿不到数据就说是反爬

拿不到数据有很多原因：

1. 数据本来不在 HTML；
2. 请求参数不完整；
3. 请求方法错了；
4. 分页参数找错；
5. 需要登录权限；
6. 返回的是文件或压缩内容。

反爬只是其中一种可能，不要过早归因。

### 误区 4：过早使用 Selenium

Selenium 和 Playwright 能控制浏览器，但它们不是第一选择。

更稳的流程是：

```text
先找接口 → requests 复现 → 再考虑浏览器自动化
```

只有在接口难以复现、页面依赖复杂交互、或学习目标就是浏览器自动化时，才考虑 Selenium 或 Playwright。

### 误区 5：忽略合规边界

技术上能请求，不代表现实中应该采集。

尤其是以下情况要谨慎：

- 个人信息；
- 登录后数据；
- 付费内容；
- 后台管理数据；
- 大规模高频采集；
- 绕过验证码或权限限制；
- 明确禁止自动化访问的网站。

学习阶段优先使用公开练习站点、官方 API、开放数据集或自己搭建的测试页面。

## 小结

- 网页数据来源判断是爬虫的第一步，先判断数据在哪里，再决定怎么写代码。
- 常见数据来源包括 HTML 直出、JSON 接口、内嵌 JSON、JS 渲染、分页接口、GraphQL、WebSocket、文件型数据和登录后数据。
- Chrome DevTools 的 Network 面板是判断数据来源的核心工具，重点看 Doc、Fetch/XHR、Preview、Response、Headers 和 Payload。
- Elements 面板显示的是渲染结果，不等于服务器原始响应，不能只靠 Elements 写爬虫。
- 遇到真实网站时，要检查服务条款、robots.txt、版权和隐私边界，不要采集越权、付费或个人敏感数据。
