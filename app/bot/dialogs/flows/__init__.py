from .broadcast.dialogs import broadcast_dialog
from .settings.dialogs import settings_dialog
from .start.dialogs import start_dialog

__all__ = ["dialogs"]

dialogs = [
    settings_dialog,
    start_dialog,
    broadcast_dialog,
]