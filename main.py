from src.backend.PluginManager.ActionBase import ActionBase
from src.backend.PluginManager.PluginBase import PluginBase
from src.backend.PluginManager.ActionHolder import ActionHolder
from src.backend.DeckManagement.InputIdentifier import Input
from src.backend.PluginManager.ActionInputSupport import ActionInputSupport

# Import gtk modules
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw

import sys
import os
from loguru import logger as log
from evdev import ecodes, AbsInfo
from evdev import UInput

# Import action classes
from .actions.Joystick.Joystick import Joystick
from .actions.Joystick.JoystickButtons import JoystickButtons
from .actions.Joystick.joy import VirtualJoystick

# Add plugin to sys.paths
sys.path.append(os.path.dirname(__file__))


class ControllerPlugin(PluginBase):
    def __init__(self):
        self.PLUGIN_NAME = "Controller"
        self.GITHUB_REPO = "https://github.com/StreamController/ControllerPlugin"
        super().__init__()
        self.init_vars()

        # Joystick action
        self.joystick_holder = ActionHolder(
            plugin_base=self,
            action_base=Joystick,
            action_id_suffix="Joystick",
            action_name=self.lm.get("actions.joystick.name", "Joystick"),
            action_support={
                Input.Key: ActionInputSupport.SUPPORTED,
                Input.Dial: ActionInputSupport.SUPPORTED,
                Input.Touchscreen: ActionInputSupport.UNTESTED
            }
        )
        self.add_action_holder(self.joystick_holder)

        # JoystickButtons action
        self.joystick_buttons_holder = ActionHolder(
            plugin_base=self,
            action_base=JoystickButtons,
            action_id_suffix="JoystickButtons",
            action_name=self.lm.get("actions.joystick-buttons.name", "Joystick Buttons"),
            action_support={
                Input.Key: ActionInputSupport.SUPPORTED,
                Input.Dial: ActionInputSupport.SUPPORTED,
                Input.Touchscreen: ActionInputSupport.UNTESTED
            }
        )
        self.add_action_holder(self.joystick_buttons_holder)

        # Register plugin
        self.register(
            plugin_name=self.lm.get("plugin.name", "Controller"),
            github_repo=self.GITHUB_REPO,
            plugin_version="1.0.0",
            app_version="1.0.0-alpha"
        )

    def init_vars(self):
        self.lm = self.locale_manager
        self.lm.set_to_os_default()
        self.lm.set_fallback_language("en_US")

        # Initialize virtual gamepad
        try:
            capabilities = {
                ecodes.EV_KEY: [ecodes.BTN_A, ecodes.BTN_B, ecodes.BTN_X, ecodes.BTN_Y, 
                           ecodes.BTN_TL, ecodes.BTN_TR, ecodes.BTN_TL2, ecodes.BTN_TR2, 
                           ecodes.BTN_SELECT, ecodes.BTN_START, ecodes.BTN_MODE,
                           ecodes.BTN_THUMBL, ecodes.BTN_THUMBR],
                ecodes.EV_ABS: [
                    # Alternative axes that don't affect mouse
                    (ecodes.ABS_RZ, AbsInfo(value=0, min=-32767, max=32767, fuzz=0, flat=0, resolution=0)),
                    (ecodes.ABS_THROTTLE, AbsInfo(value=0, min=-32767, max=32767, fuzz=0, flat=0, resolution=0)),
                    # Standard gamepad axes
                    (ecodes.ABS_RX, AbsInfo(value=0, min=-32767, max=32767, fuzz=0, flat=0, resolution=0)),
                    (ecodes.ABS_RY, AbsInfo(value=0, min=-32767, max=32767, fuzz=0, flat=0, resolution=0)),
                    (ecodes.ABS_HAT0X, AbsInfo(value=0, min=-1, max=1, fuzz=0, flat=0, resolution=0)),
                    (ecodes.ABS_HAT0Y, AbsInfo(value=0, min=-1, max=1, fuzz=0, flat=0, resolution=0)),
                    # Include original X/Y axes for completeness but not recommended
                    (ecodes.ABS_X, AbsInfo(value=0, min=-32767, max=32767, fuzz=0, flat=0, resolution=0)),
                    (ecodes.ABS_Y, AbsInfo(value=0, min=-32767, max=32767, fuzz=0, flat=0, resolution=0)),
                ]
            }
            self.gamepad_ui = UInput(capabilities, name="stream-controller-controller-plugin-virtual-gamepad", phys="virtual-gamepad")
            self.gamepad = VirtualJoystick("streamcontroller-joystick", self.gamepad_ui)
        except Exception as e:
            log.error(f"Failed to initialize virtual gamepad: {e}")
            self.gamepad_ui = None
            self.gamepad = None 