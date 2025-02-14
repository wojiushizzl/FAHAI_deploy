import flet as ft


def audio_played(page: ft.Page, audio_path: str = '/sounds/mes.wav'):
    """音频播放"""
    def audio_state_changed(e: ft.ControlEvent):
        """音频播放状态改变时触发的事件"""
        if e.data == 'completed':
            page.overlay.remove(e.control)

    audio = ft.Audio(src=audio_path, volume=1, autoplay=True, on_state_changed=audio_state_changed)
    page.overlay.append(audio)
    page.update()
