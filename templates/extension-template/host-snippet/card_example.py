"""Connect a verified extension to the Alp settings panel."""
from __future__ import annotations

from collections.abc import Callable

from brb02.gui.extensions_ui import ExtensionCard, ExtensionsPanel, make_extension_subcard
from brb02.gui.widgets import Toggle


def attach_sample_extension_card(
    panel: ExtensionsPanel,
    *,
    installed: bool,
    running: bool,
    accent_color: str,
    on_toggle: Callable[[bool], None],
    on_get_extension: Callable[[], None],
    on_uninstall: Callable[[], None],
) -> ExtensionCard:
    """Use the host's verified installation and runtime state."""
    active = installed and running
    toggle = Toggle(active)
    toggle.setEnabled(installed)
    status = 'absent'
    if installed:
        toggle.toggled = on_toggle
        status = 'running' if active else 'ready'

    card = ExtensionCard(
        ext_id='vendor.example-extension',
        name='示例扩展',
        version='1.0.0',
        mode_label='独立安装',
        description='演示安装状态、运行开关与独立卸载如何接入 Alp。',
        status=status,
        toggle_widget=toggle,
        installed=installed,
        accent_color=accent_color,
        secondary_label='卸载' if installed else '获取扩展',
        on_secondary=on_uninstall if installed else on_get_extension,
        expanded=True,
        keywords='示例 扩展',
    )

    title = '设置' if installed else '安装说明'
    hint = ('这里可以加入扩展的设置控件。' if installed
            else '运行扩展安装包，然后从托盘退出并重新打开 Alp。')
    section, _, _ = make_extension_subcard(title, hint)
    card.drawer_layout.addWidget(section)
    panel.add_card(card)
    return card
