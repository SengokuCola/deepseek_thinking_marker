# DeepSeek 思考模式 Marker

DeepSeek 思考模式 Marker 是一个 MaiBot 插件，用于在 Maisaka planner 和 replyer 的模型请求中插入 DeepSeek V4 思考模式 marker。

当前版本：`0.1.1`

## 功能

- 在 planner 请求中注入思考模式 marker。
- 在 replyer 最终模型请求中注入思考模式 marker。
- 支持 `inner_os`、`no_inner_os`、`custom` 和关闭注入模式。
- 可检测已有 marker，避免重复注入。

## 配置

```toml
[plugin]
enabled = true
config_version = "0.1.0"

[marker]
mode = "inner_os"
custom_marker = ""
inject_planner = true
inject_replyer = true
avoid_duplicate = true
```

## 配置项说明

- `marker.mode`：注入模式。`inner_os` 为角色沉浸，`no_inner_os` 为纯分析，`custom` 使用自定义文本，`default`、`off`、`disabled` 或 `none` 表示不注入。
- `marker.custom_marker`：`mode = "custom"` 时注入的完整 marker 文本。
- `marker.inject_planner`：是否在 planner 请求中注入 marker。
- `marker.inject_replyer`：是否在 replyer 请求中注入 marker。
- `marker.avoid_duplicate`：检测到已有内置 marker 标题时不重复注入。

## 使用说明

安装并启用插件后，保持默认配置即可在 Maisaka planner 和 replyer 请求中注入角色沉浸 marker。如需切换为纯分析模式，将 `marker.mode` 改为 `no_inner_os`。

## 更新记录

### 0.1.1

#### 开发侧

- 移除 manifest v2 不支持的顶层字段，避免插件运行器严格校验失败。

## 许可证

GPL-v3.0-or-later
