# pylint: disable=missing-module-docstring
# pylint: disable=no-name-in-module
from __future__ import generator_stop
from __future__ import annotations

from cynodegraph.core import graphics_guifeedback



# TODO: Make this dynamic somehow so that when using the package icons can
# be added and removed
# dictionary containing the guifeedback icons avaiable
ICON_TYPES = {
    'null': 0.0, # question
    'good': 24.0, # check
    'bad': 48.0, # error
}



class GUIFeedbackPopup:
    """A popup forthe system to convey info and warnings to the user.

    Args:
        graphics_scene_ref (GraphicsScene): Reference to the scene which the
            popup is to be for and drawn on.

    Todo:
        * FOCUS: Commenting this.
        * Make icon dictionary dynamic, perhaps with add and remove methods.
    """

    def __init__(self, graphics_scene_ref: 'GraphicsScene'):
        self.__graphics_scene: 'GraphicsScene' = graphics_scene_ref
        self.__graphics_guifeedback: 'GraphicsGUIFeedbackPopup' = (
            graphics_guifeedback.GraphicsGUIFeedbackPopup())
        self.__graphics_guifeedback.setZValue(1_000_000)
        self.__graphics_guifeedback.hide()
        self.__active = False

        # add guifeedback to scene
        self.__graphics_scene.addItem(self.__graphics_guifeedback)


    @property
    def position(self) -> 'QPointF':
        """QPointF: The position of the popup as a QPointF.
        """
        return self.__graphics_guifeedback.pos()

    def set_position(self, x_pos: int, y_pos: int):
        """Setter: Update the position to the child GraphicsGUIFeedbackPopup.

        Args:
            x_pos (int): The x position to update the popup to.
            y_pos (int): The y position to update the popup to.
        """
        self.__graphics_guifeedback.setPos(x_pos, y_pos)

    @property
    def text(self) -> str:
        """str: The popup's current info text to be displayed.

        Setter: Change the popup's current info text to be displayed.
        """
        return self.__graphics_guifeedback.text

    @text.setter
    def text(self, value: str):
        self.__graphics_guifeedback.text = value

    def is_visible(self) -> bool:
        """Returns if the popup is currently in a visible state.

        Returns:
            bool: Returns True if the popup is currently visible, else False.
        """
        return self.__graphics_guifeedback.isVisible()


    def hide(self):
        """Tells the child GraphicsGUIFeedbackPopup to hide itself.
        """
        self.__graphics_guifeedback.hide()

    def show(self):
        """Tells the child GraphicsGUIFeedbackPopup to show itself.
        """
        self.__graphics_guifeedback.show()

    # TODO: find out the type of object icon is
    def set(self, text: str, icon=None):
        """Set the info string to be displayed and the icon for the top
        left corner.

        Args:
            text (str): The popup's info text to be displayed.
            icon (???): The popup's icon to be displayed in the top left
                corner.
        """
        if not self.__active:
            self.text = text
            if icon is None:
                self.__graphics_guifeedback.icon_offset = ICON_TYPES['null']
            else:
                self.__graphics_guifeedback.icon_offset = icon
            self.__active = True
            self.__graphics_guifeedback.update()
            self.__graphics_guifeedback.show()

    def reset(self):
        """Reset the popup to a null state.

        Since the popup always exist instead of destroying it, do this.
        """
        if self.__active:
            self.__graphics_guifeedback.hide()
            self.text = "NULL"
            self.__graphics_guifeedback.icon_offset = ICON_TYPES['null']
            self.__active = False
