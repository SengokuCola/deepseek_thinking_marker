# DeepSeek 思考模式 Marker

DeepSeek 思考模式 Marker 是一个 MaiBot 插件，用于在 Maisaka planner 和 replyer 的模型请求中插入 DeepSeek V4 思考模式 marker。

当前版本：`0.1.2`

## 功能

- 在 planner 请求中注入思考模式 marker。
- 在 replyer 最终模型请求中注入思考模式 marker。
- 支持 `inner_os`、`no_inner_os`、`custom` 和关闭注入模式。
- 可检测已有 marker，避免重复注入。

## 配置

```toml
[plugin]
enabled = true
config_version = "0.1.2"

[marker]
mode = "inner_os"
custom_marker = """
"""
inject_planner = true
inject_replyer = true
avoid_duplicate = true
```

## 配置项说明

- `marker.mode`：注入模式。`inner_os` 为角色沉浸，`no_inner_os` 为纯分析，`custom` 使用自定义文本，`default`、`off`、`disabled` 或 `none` 表示不注入。
- `marker.custom_marker`：`mode = "custom"` 时注入的完整 marker 文本，支持 TOML 多行字符串。
- `marker.inject_planner`：是否在 planner 请求中注入 marker。
- `marker.inject_replyer`：是否在 replyer 请求中注入 marker。
- `marker.avoid_duplicate`：检测到已有内置 marker 标题时不重复注入。

## 使用说明

安装并启用插件后，保持默认配置即可在 Maisaka planner 和 replyer 请求中注入角色沉浸 marker。如需切换为纯分析模式，将 `marker.mode` 改为 `no_inner_os`。

如需使用自定义 marker，将 `marker.mode` 改为 `custom`，并在 `marker.custom_marker` 中填写完整文本：

```toml
[marker]
mode = "custom"
custom_marker = """
【自定义思考要求】
1. 在 <think> 中先判断当前回复目标。
2. 保持分析简洁，不要暴露无关推理。
"""
inject_planner = true
inject_replyer = true
avoid_duplicate = true
```

`avoid_duplicate = true` 时，插件会检查请求中是否已经包含内置 marker 标题或完整自定义 marker，避免重复插入。

## 更新记录

### 0.1.1

#### 开发侧

- 移除 manifest v2 不支持的顶层字段，避免插件运行器严格校验失败。

### 0.1.2

#### 用户感知功能侧

- 配置文件示例支持通过 `mode = "custom"` 和多行 `custom_marker` 自定义注入内容。

#### 开发侧

- 自定义 marker 已存在时会随 `avoid_duplicate` 一起跳过重复注入。

## 许可证

GPL-v3.0-or-later
