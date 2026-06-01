"""DeepSeek V4 思考模式 marker 注入插件。"""

from typing import Any

from maibot_sdk import Field, HookHandler, MaiBotPlugin, PluginConfigBase
from maibot_sdk.types import ErrorPolicy, HookMode, HookOrder


INNER_OS_MARKER = (
    "【角色沉浸要求】在你的思考过程（<think>标签内）中，请遵守以下规则：\n"
    "1. 请以角色第一人称进行内心独白，用括号包裹内心活动，例如\"（心想：……）\"或\"(内心OS：……)\"\n"
    "2. 用第一人称描写角色的内心感受，例如\"我心想\"\"我觉得\"\"我暗自\"等\n"
    "3. 思考内容应沉浸在角色中，通过内心独白分析剧情和规划回复"
)
NO_INNER_OS_MARKER = (
    "【思维模式要求】在你的思考过程（<think>标签内）中，请遵守以下规则：\n"
    "1. 禁止使用圆括号包裹内心独白，例如\"（心想：……）\"或\"(内心OS：……)\"，所有分析内容直接陈述即可\n"
    "2. 禁止以角色第一人称描写内心活动，例如\"我心想\"\"我觉得\"\"我暗自\"等，请用分析性语言替代\n"
    "3. 思考内容应聚焦于剧情走向分析和回复内容规划，不要在思考中进行角色扮演式的内心戏表演"
)
BUILTIN_MARKERS = {
    "inner_os": INNER_OS_MARKER,
    "no_inner_os": NO_INNER_OS_MARKER,
}
MARKER_TITLES = ("【角色沉浸要求】", "【思维模式要求】")


class PluginSectionConfig(PluginConfigBase):
    """插件基础配置。"""

    __ui_label__ = "插件"
    __ui_icon__ = "sparkles"
    __ui_order__ = 0

    enabled: bool = Field(default=True, description="是否启用插件")
    config_version: str = Field(default="0.1.3", description="配置版本")


class MarkerConfig(PluginConfigBase):
    """Marker 注入配置。"""

    __ui_label__ = "Marker"
    __ui_icon__ = "message-square-plus"
    __ui_order__ = 1

    mode: str = Field(
        default="inner_os",
        description="注入模式：inner_os=角色沉浸，no_inner_os=纯分析，custom=自定义，default=不注入",
    )
    custom_marker: str = Field(default="", description="mode=custom 时注入的完整 marker 文本")
    inject_planner: bool = Field(default=True, description="是否在 planner 请求中注入 marker")
    inject_replyer: bool = Field(default=True, description="是否在 replyer 请求中注入 marker")


class DeepSeekThinkingMarkerConfig(PluginConfigBase):
    """DeepSeek 思考模式 marker 插件配置。"""

    plugin: PluginSectionConfig = Field(default_factory=PluginSectionConfig)
    marker: MarkerConfig = Field(default_factory=MarkerConfig)


class DeepSeekThinkingMarkerPlugin(MaiBotPlugin):
    """在 Maisaka 模型请求第一条 user message 位置插入思考模式 marker。"""

    config_model = DeepSeekThinkingMarkerConfig

    async def on_load(self) -> None:
        """处理插件加载。"""

        self.ctx.logger.info("DeepSeek 思考模式 Marker 插件已加载，当前模式: %s", self.config.marker.mode)

    async def on_unload(self) -> None:
        """处理插件卸载。"""

    async def on_config_update(self, scope: str, config_data: dict[str, object], version: str) -> None:
        """处理配置热重载。"""

        del scope
        del config_data
        del version
        self.ctx.logger.info("DeepSeek 思考模式 Marker 配置已更新，当前模式: %s", self.config.marker.mode)

    def _resolve_marker(self) -> str:
        mode = str(self.config.marker.mode or "").strip().lower()
        if mode in {"", "default", "off", "disabled", "none"}:
            return ""
        if mode == "custom":
            return str(self.config.marker.custom_marker or "").strip()
        return BUILTIN_MARKERS.get(mode, "").strip()

    @staticmethod
    def _extract_message_text(message: dict[str, Any]) -> str:
        content = message.get("content")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            text_parts: list[str] = []
            for item in content:
                if isinstance(item, str):
                    text_parts.append(item)
                    continue
                if isinstance(item, dict) and isinstance(item.get("text"), str):
                    text_parts.append(item["text"])
            return "".join(text_parts)
        return ""

    def _has_existing_marker(self, messages: list[dict[str, Any]]) -> bool:
        for message in messages:
            if str(message.get("role") or "").strip().lower() != "user":
                continue
            text = self._extract_message_text(message)
            if any(title in text for title in MARKER_TITLES):
                return True
            custom_marker = str(self.config.marker.custom_marker or "").strip()
            if custom_marker and custom_marker in text:
                return True
        return False

    def _inject_marker_message(self, messages: Any) -> Any:
        if not self.config.plugin.enabled:
            return messages

        marker = self._resolve_marker()
        if not marker or not isinstance(messages, list):
            return messages

        normalized_messages = [dict(message) for message in messages if isinstance(message, dict)]
        if len(normalized_messages) != len(messages) or self._has_existing_marker(normalized_messages):
            return messages

        first_role = str(normalized_messages[0].get("role") if normalized_messages else "").strip().lower()
        insert_index = 1 if first_role == "system" else 0
        marker_message = {
            "role": "user",
            "content": marker,
        }
        return [
            *normalized_messages[:insert_index],
            marker_message,
            *normalized_messages[insert_index:],
        ]

    def _build_modified_kwargs(self, kwargs: dict[str, Any], *, enabled: bool) -> dict[str, Any]:
        modified_kwargs = dict(kwargs)
        if enabled:
            modified_kwargs["messages"] = self._inject_marker_message(modified_kwargs.get("messages"))
        return modified_kwargs

    @HookHandler(
        "maisaka.planner.before_request",
        name="deepseek_marker_planner",
        description="在 planner 请求第一条 user message 位置注入 DeepSeek 思考模式 marker。",
        mode=HookMode.BLOCKING,
        order=HookOrder.EARLY,
        timeout_ms=90000,
        error_policy=ErrorPolicy.SKIP,
    )
    async def inject_planner_marker(self, **kwargs: Any) -> dict[str, Any]:
        """改写 planner 请求 messages。"""

        return {
            "action": "continue",
            "modified_kwargs": self._build_modified_kwargs(kwargs, enabled=self.config.marker.inject_planner),
        }

    @HookHandler(
        "maisaka.replyer.before_model_request",
        name="deepseek_marker_replyer",
        description="在 replyer 请求第一条 user message 位置注入 DeepSeek 思考模式 marker。",
        mode=HookMode.BLOCKING,
        order=HookOrder.EARLY,
        timeout_ms=90000,
        error_policy=ErrorPolicy.SKIP,
    )
    async def inject_replyer_marker(self, **kwargs: Any) -> dict[str, Any]:
        """改写 replyer 最终请求 messages。"""

        return {
            "action": "continue",
            "modified_kwargs": self._build_modified_kwargs(kwargs, enabled=self.config.marker.inject_replyer),
        }


def create_plugin() -> DeepSeekThinkingMarkerPlugin:
    """创建插件实例。"""

    return DeepSeekThinkingMarkerPlugin()
