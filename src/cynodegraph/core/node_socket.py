# pylint: disable=missing-module-docstring
# pylint: disable=no-name-in-module
from __future__ import generator_stop
from __future__ import annotations

from typing import Dict
from typing import List

from cynodegraph.core import graphics_socket
from cynodegraph.core import logparams
from cynodegraph.core import node
from cynodegraph.core import node_edge
from cynodegraph.core import node_scene



# anchor location of the socket on the node
LEFT_TOP = 1        #:
LEFT_CENTER =2      #:
LEFT_BOTTOM = 3     #:
RIGHT_TOP = 4       #:
RIGHT_CENTER = 5    #:
RIGHT_BOTTOM = 6    #:



class Socket:
    """The socket component that connects Node data using Edges.

    Args:
        node_ref (Node): The Socket's parent Node.
        scene (Scene): The parent Scene of the Node that this Socket belongs to.
        index (int): The index position on the Node's side.
        position (int): The side position of the Socket on the Node.
        socket_type (int): The value of the Socket type(ie. type of data).
        is_multi_edges (bool): Flag for if the Socket supports multiple edges.
        side_node_count (int): The number of Sockets on the position side.
        is_input (bool): Flag for if the Socket is an input Socket or output.

    Attributes:
        node (Node): The Socket's parent Node.
        scene (Scene): The parent Scene of the Node that this Socket belongs to.
        index (int): The index position on the Node's side.
        position (int): The side position of the Socket on the Node.
        socket_type (int): The value of the Socket type(ie. type of data).
        is_multi_edges (bool): Flag for if the Socket supports multiple edges.
        side_node_count (int): The number of Sockets on the position side.
        is_input (bool): Flag for if the Socket is an input Socket or output.
        is_output (bool): (Remove)Flag for if the Socket is an output Socket.
        edges (List[Edge]): A List of the references for the Socket's connected Edges.
    Todo:
        * FOCUS: Finishing documentation.
        * create property accesses(See note 1).
        * is_output is redundant. Fix and remove.
    """

    # pylint: disable=too-many-instance-attributes
    # Reasoning: All the attributes are needed and used.
    # pylint: disable=too-many-arguments
    # Reasoning: Useful and does no harm.
    def __init__(self, node_ref: node.Node, scene: node_scene.Scene,
        index: int=0, position: int=LEFT_TOP, socket_type: int=1,
        multi_edges: bool=True, side_node_count: int=1,
        is_input: bool=False
    ):
        """Inits the components needed for the socket."""
        # TODO: (Note 1) Make private and set accessors
        self.node: node.Node = node_ref
        self.scene: node_scene.Scene = scene
        self.index: int = index
        self.position: int = position
        self.socket_type: int = socket_type
        self.is_multi_edges: bool = multi_edges
        self.side_node_count: int = side_node_count
        self.is_input: bool = is_input
        self.is_output: bool = not self.is_input

        self.edges: List[node_edge.Edge] = []

        self.__graphics_socket: graphics_socket.GraphicsSocket = graphics_socket.GraphicsSocket(
            self, self.scene, self.socket_type
        )

        self.set_socket_position()

    def __str__(self) -> str:
        """Returns the Sockets's python id as hexidecimal and if it has one or more edges."""
        return (
            f"<Socket {'ME' if self.is_multi_edges else 'SE'} "
            f"{hex(id(self))[2:5]}..{hex(id(self))[-3:]}>"
        )



    def set_socket_position(self):
        """Set the position of the GraphicsSocket.

        Takes the parameters form the Node and the positioning of the
        Socket and sets the GraphicsSocket's position.
        """
        self.__graphics_socket.setPos(
            *self.node.get_socket_position(
                self.index, self.position, self.side_node_count
            )
        )

    def get_socket_position(self) -> List:
        """Returns the position of the Socket as a List of [x, y].

        Returns:
            List[int, int]: The position of the Socket as a List [x, y].
        """
        logparams.logging.debug(f"  GSP: {self.index} {self.position} node: {self.node}")
        position: List[int, int] = self.node.get_socket_position(
            self.index, self.position, self.side_node_count
        )
        logparams.logging.debug(f"  position({position})")

        return position

    def add_edge(self, edge):
        """Adds a connected Edge to the Sockets List of connected Edges.
        """
        self.edges.append(edge)
        logparams.logging.debug(f"Add Edge: Socket {id(self)} >> Edges: {len(self.edges)}")
        logparams.logging.debug(f"Socket Type: {self.socket_type}")
        logparams.logging.debug(f"Start Socket: {edge.start_socket}\tEnd Socket: {edge.end_socket}")

    def remove_edge(self, edge: List):
        """Removes an Edge from the Socket and it's List.

        Args:
            edge (Edge): A reference to the edge to remove.
        """
        if edge in self.edges:
            self.edges.remove(edge)
        else:
            print(
                f"!W: Socket::removeEdge want to remove edge {edge} from"
                f"self.edges but it's not in the list"
            )
        logparams.logging.debug(
            f"Remove Edge: Socket {id(self)} >> Edges: {len(self.edges)}"
        )

    def remove_all_edges(self):
        """Removes all Edges from the Socket and it's List.
        """
        while self.edges:
            edge = self.edges.pop(0)
            edge.remove()
        logparams.logging.debug(
            f"Remove All Edge: Socket {id(self)} >> Edges: {len(self.edges)}"
        )

    def determine_multi_edges(self, data: Dict) -> int:
        """Determines if the Socket is a multiedge or not.

        Args:
            data (Dict): Dictionary containing the Sockets data.

        Returns:
            bool: Not sure

        Todo:
            * Is used or effecient?
            * What is the return
        """
        if 'multi_edges' in data:
            return data['multi_edges']

        # else probably older version of file, make RIGHT socket multiedged by default
        return data['position'] in (RIGHT_BOTTOM, RIGHT_TOP)
