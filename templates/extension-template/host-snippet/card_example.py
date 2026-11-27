"""Reference snippet showing how Alp Toolbox renders an extension card cleanly."""
from __future__ import annotations

from PySide6.QtWidgets import QLabel

from brb02.gui.extensions_ui import ExtensionCard, ExtensionsPanel, make_extension_subcard
from brb02.gui.widgets import Toggle


def attach_sample_extension_card(
    panel: ExtensionsPanel,
    *,
    installed: bool,
    enabled: bool,
    accent_color: str,
    on_toggle,
    on_open_plugins,
) -> ExtensionCard:
    """Attach a sample extension card following Alp Toolbox Settings -> Extensions rules."""
    toggle = Toggle(enabled if installed else False)
    toggle.setEnabled(installed)
    if installed:
        toggle.toggled = on_toggle

    card = ExtensionCard(
        ext_id='vendor.example-extension',
        name='示例扩展',
        version='1.0.0',
        mode_label='按需加载 · 需重启',
        description='演示如何基于 ExtensionCard 与 make_extension_subcard 接入工具箱设置页',
        status='running' if (installed and enabled) else ('ready' if installed else 'absent'),
        toggle_widget=toggle,
        installed=installed,
        icon_kind='overlay',
        accent_color=accent_color,
        secondary_label='卸载' if installed else '获取扩展',
        on_secondary=on_open_plugins,
        expanded=True,
        keywords='example utility template',
    )

    # IMPORTANT: Never nest a second GlassFrame inside card.drawer_layout;
    # always use make_extension_subcard() for sub-sections inside the drawer.
    sub_card, _title, sub_layout = make_extension_subcard(
        '基础配置',
        '各子区域使用边框子卡片承载，适配浅色/深色与液态玻璃主题。',
    )
    sub_layout.addWidget(QLabel('在此添加扩展开关、下拉选项或状态提示。'))
    card.drawer_layout.addWidget(sub_card)

    panel.add_card(card)
    return card
