# pylint: disable=missing-module-docstring
# pylint: disable=no-name-in-module
from __future__ import generator_stop
from __future__ import annotations

from cynodegraph.core import graphics_edge
from cynodegraph.core import logparams
from cynodegraph.core import node_scene
from cynodegraph.core import node_socket



# edge line types
EDGE_TYPE_DIRECT: int = 1
EDGE_TYPE_BEZIER: int = 2



class Edge:
    """The edge component that connect Node's Sockets.

    Args:
        scene (Scene): Reference to Scene object that the Edge is drawn on(child of).
        start_socket (Socket): Reference to the edge's starting Socket.
        end_socket (Socket): Reference to the edge's ending Socket.
        edge_type (int): The const deciding the type of line the edge will be.
            Direct or Bezier.

    Attributes:
        scene (Scene): Reference to Scene object that the edge is drawn on(child of).
        start_socket (Socket): Reference to the edge's starting Socket.
        end_socket (Socket): Reference to the edge's ending Socket.
        edge_type (int): The const deciding the type of line the edge will be.
            Direct or Bezier.
    """

    # pylint: disable=too-many-instance-attributes
    # Reasoning: All the attributes are needed and used. Also the properties are
    # not attributes.
    def __init__(self, scene: node_scene.Scene,
            start_socket: node_socket.Socket=None,
            end_socket: node_socket.Socket=None,
            edge_type: int=EDGE_TYPE_DIRECT
        ):
        """Inits the components needed for the edge to connect to."""
        self.scene: node_scene.Scene = scene

        # These are the protected Socket class member variables
        self.__start_socket: node_socket.Socket = None
        self.__end_socket: node_socket.Socket = None
        self.__edge_type: int = None

        # These are the @property calls to set the protected variables
        self.start_socket: node_socket.Socket = start_socket
        self.end_socket: node_socket.Socket = end_socket
        self.edge_type: int = edge_type

        self.scene.add_edge(self)

    def __str__(self) -> str:
        """Returns the Edge's python id as hexidecimal."""
        return f"{{Edge: {hex(id(self))}}}"


    def _remove_from_sockets(self):
        """Calls the @property of the attached sockets and sets them None."""
        self.end_socket = None
        self.start_socket = None


    @property
    def start_socket(self) -> node_socket.Socket:
        """Socket: Reference to the starting socket.

        Setter: If there is already a Socket value held, then remove the
        Edge from it and then set the class's starting Socket to the new
        one. Then add the Edge to the new Socket.
        """
        return self.__start_socket

    @start_socket.setter
    def start_socket(self, value: node_socket.Socket):
        # if we were assigned to some socket before, delete us from the socket
        if self.__start_socket is not None:
            self.__start_socket.remove_edge(self)

        # assign new start socket
        self.__start_socket = value
        # addEdge to the Socket class
        if self.start_socket is not None:
            self.start_socket.add_edge(self)

    @property
    def end_socket(self) -> node_socket.Socket:
        """Socket: Reference to the ending socket.

        Setter: If there is already a Socket value held, then remove the Edge
        from it and then set the class's ending Socket to the new one. Then
        add the Edge to the new Socket
        """
        return self.__end_socket

    @end_socket.setter
    def end_socket(self, value: node_socket.Socket):
        # if we were assigned to some socket before, delete us from the socket
        if self.__end_socket is not None:
            self.__end_socket.remove_edge(self)

        # assign new end socket
        self.__end_socket = value
        # addEdge to the Socket class
        if self.end_socket is not None:
            self.end_socket.add_edge(self)

    @property
    def edge_type(self) -> int:
        """int: An integer value that represents which line type to use.

        Setter: Creates a new GraphicsEdge for the set line type. If the Edge
        had a GraphicsEdge already it is removed and released.
        """
        return self.__edge_type

    @edge_type.setter
    def edge_type(self, value: int):
        # if the type of edge is being changed remove the old GraphicsEdge
        if hasattr(self, 'graphics_edge') and self.graphics_edge is not None:
            self.scene.graphics_scene.removeItem(self.graphics_edge)

        # add the new GraphicsEdge for the edge
        self.__edge_type = value
        if self.edge_type == EDGE_TYPE_DIRECT:
            self.graphics_edge = graphics_edge.GraphicsEdge(self, graphics_edge.EDGE_TYPE_DIRECT)
        elif self.edge_type == EDGE_TYPE_BEZIER:
            self.graphics_edge = graphics_edge.GraphicsEdge(self, graphics_edge.EDGE_TYPE_BEZIER)
        else:
            self.graphics_edge = graphics_edge.GraphicsEdge(self, graphics_edge.EDGE_TYPE_BEZIER)

        self.scene.graphics_scene.addItem(self.graphics_edge)

        if self.start_socket is not None:
            self.update_positions()


    def do_select(self, new_state=True):
        """In order to highlight the selected line, set the GraphicsEdge
            selected or not.

        Args:
            new_state (bool): The select state of the GraphicsEdge. Default
                is True.
        """
        self.graphics_edge.do_select(new_state)

    def get_other_socket(self, known_socket) -> node_socket.Socket:
        """Returns the other Socket that is not the parameter.

        Args:
            known_socket (Socket): The Socket that is known.

        Returns:
            Socket: The Socket of the other Socket that is not the known
                one.
        """
        return self.start_socket if known_socket == self.end_socket else self.end_socket

    def remove(self):
        """Removes the edge for the application.

        Removes the edge from the application and then makes sure the
        sockets that it connected no longer reference it.
        """
        old_sockets = [self.start_socket, self.end_socket]

        logparams.logging.info(f"# Removing Edge {self}")
        logparams.logging.debug(" - remove edge from all sockets")
        self._remove_from_sockets()
        logparams.logging.debug(" - remove graphics_edge")
        self.scene.graphics_scene.removeItem(self.graphics_edge)
        self.graphics_edge = None
        logparams.logging.debug(" - remove edge from scene")
        try:
            self.scene.remove_edge(self)
        except ValueError:
            logparams.logging.exception("Exception occurred")
        logparams.logging.debug(" - everything is done.")

        try:
            # notify nodes from old sockets
            for socket in old_sockets:
                if socket and socket.node:
                    socket.node.on_edge_connection_changed(self)
                    if socket.is_input:
                        socket.node.on_input_changed(self)
        # pylint: disable=broad-except
        # Reasoning: would need a special exception
        except Exception:
            logparams.logging.exception("Exception occurred")

    def update_positions(self):
        """When the line needs to be redraw set the GraphicsEdge's new starting
        and end socket locations.
        """
        source_pos = self.start_socket.get_socket_position()
        source_pos[0] += self.start_socket.node.graphics_node.pos().x()
        source_pos[1] += self.start_socket.node.graphics_node.pos().y()
        self.graphics_edge.set_source(*source_pos)
        if self.end_socket is not None:
            end_pos = self.end_socket.get_socket_position()
            end_pos[0] += self.end_socket.node.graphics_node.pos().x()
            end_pos[1] += self.end_socket.node.graphics_node.pos().y()
            self.graphics_edge.set_destination(*end_pos)
        else:
            self.graphics_edge.set_destination(*source_pos)
        self.graphics_edge.update()
