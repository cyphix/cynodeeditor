# pylint: disable=missing-module-docstring
# pylint: disable=no-name-in-module
from __future__ import generator_stop
from __future__ import annotations

from typing import List

from PyQt5.QtCore import QPointF

from cynodegraph.core import graphics_node
from cynodegraph.core import logparams
from cynodegraph.core import node
from cynodegraph.core import node_content_widget
from cynodegraph.core import node_edge
from cynodegraph.core import node_scene
from cynodegraph.core import node_socket



class Node:
    """The node component used in the node graph.

    Args:
        scene (Scene): Reference to Scene object that the Node is drawn
            on(child of).
        title (str): The display title of the Node.
        inputs (List[int]): A List of integer values representing the types
            of input Sockets to create.
        outputs (List[int]): A List of integer values representing the types
            of output Sockets to create.

    Attributes:
        scene (Scene): Reference to Scene object that the Node is drawn
            on(child of).
        title (str): The display title of the Node.
        content (NodeContentWidget): The content of the Node.
        graphics_node (GraphicsNode): The child GraphicsNode used to display
            the Node.
        inputs (List[Socket]): A List of the Node's input Sockets.
        outputs (List[Socket]): A List of the Node's output Sockets.
        socket_spacing_x (int): The spacing from the Node's edge for input
            Sockets.
        socket_spacing_y (int): The spacing from the Node's other Sockets.
        socket_spacing_x_offset (int): The spacing from the Node's edge for
            output Socets.
        input_socket_position (int): A value representing the area the input
            Sockets are on the Node. [LEFT_TOP, LEFT_CENTER, LEFT_BOTTOM,
            RIGHT_TOP, RIGHT_CENTER, RIGHT_BOTTOM]
        output_socket_position (int): A value representing the area the
            output Sockets are on the Node. [LEFT_TOP, LEFT_CENTER,
            LEFT_BOTTOM, RIGHT_TOP, RIGHT_CENTER, RIGHT_BOTTOM]
        input_multi_edged (bool): Flag for if the input Sockets are
            multi-edge.
        output_multi_edged (bool): Flag for if the output Sockets are
            multi-edge.
    """

    # pylint: disable=too-many-instance-attributes
    # Reasoning: All the attributes are needed and used.
    # pylint: disable=too-many-public-methods
    # Reasoning: All the methods are needed and used.
    def __init__(
        self, scene: node_scene.Scene, title: str="Undefined Node",
        inputs: List[int]=None, outputs: List[int]=None
    ):
        self.scene: node_scene.Scene = scene
        self.title: str = title
        # TODO: Check if this can safely be removed
        #self.node_type = None

        self.content: node_content_widget.NodeContentWidget = (
            node_content_widget.NodeContentWidget(self))
        self.graphics_node: graphics_node.GraphicsNode = graphics_node.GraphicsNode(self)
        self.scene.add_node(self)
        self.scene.graphics_scene.addItem(self.graphics_node)

        self.inputs: List[node_socket.Socket] = []
        self.outputs: List[node_socket.Socket] = []

        # socket relative to node edges and other sockets
        self.socket_spacing_x: int = 15 # spacing from the node edge
        self.socket_spacing_y: int = 22 # spacing from other sockets
        self.socket_spacing_x_offset: int = 15 # offset for output nodes

        # settings
        self.input_socket_position: int = node_socket.LEFT_BOTTOM
        self.output_socket_position: int = node_socket.RIGHT_TOP
        self.input_multi_edged: bool = False
        self.output_multi_edged: bool = True

        # create components
        self.__create_sockets(inputs, outputs)

        # dirty and evaluation
        self._is_dirty: bool = False
        self._is_invalid: bool = False



    def __create_sockets(self, inputs: List[int], outputs: List[int], reset: bool=True):
        """Creates and adds the Sockets for the Node.

        Args:
            input (List[int]): The input Socket's representing integer
                values.
            output (List[int]): The output Socket's representing integer
                values.
            reset (bool): Flag for if the Sockets should be recreated.
        """
        if reset:
            # clear old sockets
            if hasattr(self, 'inputs') and hasattr(self, 'outputs'):
                # remove grSockets from scene
                for socket in self.inputs + self.outputs:
                    self.scene.graphics_scene.removeItem(socket.graphics_socket)
                self.inputs = []
                self.outputs = []

        # create new sockets
        counter = 0
        for item in inputs:
            socket = node_socket.Socket(
                node_ref = self,
                scene = self.scene,
                index = counter,
                position = self.input_socket_position,
                socket_type = item,
                multi_edges = self.input_multi_edged,
                side_node_count = len(inputs),
                is_input = True
            )
            counter += 1
            self.inputs.append(socket)

        counter = 0
        for item in outputs:
            socket = node_socket.Socket(
                node_ref = self,
                scene = self.scene,
                index = counter,
                position = self.output_socket_position,
                socket_type = item,
                multi_edges = self.output_multi_edged,
                side_node_count = len(outputs),
                is_input = False
            )
            counter += 1
            self.outputs.append(socket)



    @property
    def pos(self) -> QPointF:
        """QPointF: Returns the Node's graphical position.
        """
        return self.graphics_node.pos()

    def set_pos(self, x_pos: int, y_pos: int):
        """Setter: Sets the Node's graphical position.

        Args:
            x_pos (int): The new x position.
            y_pos (int): The new y position.
        """
        self.graphics_node.setPos(x_pos, y_pos)


    def on_edge_connection_changed(self, new_edge: node_edge.Edge):
        """Logs when an Edge connection to a Socket is changed.

        Args:
            new_edge (Edge): Changed Edge.

        Todo:
            * May be able to remove this.(Used for Undo function. Not used)
        """
        logparams.logging.info(f"Edge connection changed: {new_edge}")

    def on_input_changed(self, new_edge: node_edge.Edge):
        """Inputs changed.

        Todo:
            * May be able to remove this.(Used for Undo function. Not used)
        """
        logparams.logging.info(f"Input changed: {new_edge}")
        self.mark_dirty()
        self.mark_descendants_dirty()

    def do_select(self, new_state: bool=True):
        """Let the child GraphicsNode know the Node has been selected.

        Args:
            new_state (bool): Flag for if the Node was selected.
        """
        self.graphics_node.do_select(new_state)

    def get_socket_position(
        self, index: int, position: int, num_out_of: int=1,
        socket_point_width: float=4.0
    ) -> List[int, int]:
        """Calculates where to position a Socket on the Node based on params.

        Args:
            index (int): The index of a Socket at a given position on the
                Node.
            position (int): A value representing the area the
                Socket is on the Node. [LEFT_TOP, LEFT_CENTER,
                LEFT_BOTTOM, RIGHT_TOP, RIGHT_CENTER, RIGHT_BOTTOM]
            num_out_of (int): The number of Sockets at a given position on
                the Node.
            socket_point_width (float): The size of the Socket graphically.

        Returns:
            List[int, int]: Returns a two sized List with the x and y
                positions of the Socket graphically.

        Todo:
            * Make the return a Tuple instead of a List.
        """
        # calculate x position
        if (position in (node_socket.LEFT_TOP, node_socket.LEFT_CENTER,
            node_socket.LEFT_BOTTOM)
        ):
            x_pos = self.socket_spacing_x
        else:
            # find the node width and then move inward the offset from the right of the socket
            x_pos = self.graphics_node.width - self.socket_spacing_x - socket_point_width

        # calculate y position
        if position in (node_socket.LEFT_BOTTOM, node_socket.RIGHT_BOTTOM):
            # start from bottom
            y_pos = (
                self.graphics_node.height -
                self.graphics_node.edge_roundness -
                self.graphics_node.title_vertical_padding - index *
                self.socket_spacing_y
            )
        elif position in (node_socket.LEFT_CENTER, node_socket.RIGHT_CENTER):
            num_sockets = num_out_of
            node_height = self.graphics_node.height
            top_offset = (
                self.graphics_node.title_height + 2 *
                self.graphics_node.title_vertical_padding +
                self.graphics_node.edge_padding
            )
            available_height = node_height - top_offset

            # TODO: Check if this can safely be removed
            #total_height_of_all_sockets = num_sockets * self.socket_spacing_y

            # TODO: Check if can safely be removed
            #new_top = available_height - total_height_of_all_sockets

            # y = top_offset + index * self.socket_spacing_y + new_top / 2
            y_pos = top_offset + available_height/2.0 + (index-0.5)*self.socket_spacing_y
            if num_sockets > 1:
                y_pos -= self.socket_spacing_y * (num_sockets-1)/2

        elif position in (node_socket.LEFT_TOP, node_socket.RIGHT_TOP):
            # start from top
            y_pos = (
                self.graphics_node.title_height +
                self.graphics_node.title_vertical_padding +
                self.graphics_node.edge_roundness + index *
                self.socket_spacing_y
            )
        else:
            # TODO: this should never happen, put a exception log here.
            y_pos = 0

        return [x_pos, y_pos]

    def update_connected_edges(self):
        """Update the edge positions for each of the Node's Sockets.
        """
        for socket in self.inputs + self.outputs:
            for edge in socket.edges:
                edge.update_positions()

    def remove(self):
        """Remove a Node from the graph.
        """
        logparams.logging.info(f"> Removing Node: {self}")
        logparams.logging.debug(" - remove all edges from sockets")
        for socket in self.inputs + self.outputs:
            # if socket.hasEdge():
            for edge in socket.edges:
                logparams.logging.debug(f"    - removing from socket: {socket}\tedge: {edge}")
                edge.remove()
        logparams.logging.debug(" - remove grNode")
        self.scene.graphics_scene.removeItem(self.graphics_node)
        self.graphics_node = None
        logparams.logging.debug(" - remove node from the scene")
        self.scene.remove_node(self)
        logparams.logging.debug(" - everything was done.")


    # TODO: Make these a @property
    # node evaluation stuff
    def is_dirty(self) -> bool:
        """.

        Todo:
            * May be able to remove this.(Used for Undo function. Not used)
        """
        return self._is_dirty

    def mark_dirty(self, new_value: bool=True):
        """.

        Todo:
            * May be able to remove this.(Used for Undo function. Not used)
        """
        self._is_dirty = new_value
        if self._is_dirty:
            self.on_marked_dirty()

    # TODO: Check if this can safely be removed
    def on_marked_dirty(self):
        """.

        Todo:
            * May be able to remove this.(Used for Undo function. Not used)
        """
        pass

    def mark_children_dirty(self, new_value: bool=True):
        """.

        Todo:
            * May be able to remove this.(Used for Undo function. Not used)
        """
        for other_node in self.get_children_nodes():
            other_node.mark_dirty(new_value)

    def mark_descendants_dirty(self, new_value: bool=True):
        """.

        Todo:
            * May be able to remove this.(Used for Undo function. Not used)
        """
        for other_node in self.get_children_nodes():
            other_node.mark_dirty(new_value)
            other_node.mark_children_dirty(new_value)

    # TODO: Make these a @property
    def is_invalid(self) -> bool:
        """.

        Todo:
            * May be able to remove this.(Used for Undo function. Not used)
        """
        return self._is_invalid

    def mark_invalid(self, new_value: bool=True):
        """.

        Todo:
            * May be able to remove this.(Used for Undo function. Not used)
        """
        self._is_invalid = new_value
        if self._is_invalid:
            self.on_marked_invalid()

    # TODO: Check if this can safely be removed
    def on_marked_invalid(self):
        """.

        Todo:
            * May be able to remove this.(Used for Undo function. Not used)
        """
        pass

    def mark_children_invalid(self, new_value: bool=True):
        """.

        Todo:
            * May be able to remove this.(Used for Undo function. Not used)
        """
        for other_node in self.get_children_nodes():
            other_node.mark_invalid(new_value)

    def mark_descendants_invalid(self, new_value: bool=True):
        """.

        Todo:
            * May be able to remove this.(Used for Undo function. Not used)
        """
        for other_node in self.get_children_nodes():
            other_node.mark_invalid(new_value)
            other_node.mark_children_invalid(new_value)

    # TODO: Check if this needs a return
    def eval(self):
        """.

        Todo:
            * May be able to remove this.(Used for Undo function. Not used)
        """
        self.mark_dirty(False)
        self.mark_invalid(False)
        return 0

    def eval_children(self):
        """.

        Todo:
            * May be able to remove this.(Used for Undo function. Not used)
        """
        for node_obj in self.get_children_nodes():
            node_obj.eval()

    # traversing nodes functions
    def get_children_nodes(self) -> node.Node:
        """.

        Todo:
            * May be able to remove this.(Used for Undo function. Not used)
        """
        if self.outputs == []:
            return []

        other_nodes = []
        for index_x in range(len(self.outputs)):
            for edge in self.outputs[index_x].edges:
                other_node = edge.get_other_socket(self.outputs[index_x]).node
                other_nodes.append(other_node)
        return other_nodes

    def get_input(self, index: int=0) -> node.Node:
        """.

        Todo:
            * May be able to remove this.(Used for Undo function. Not used)
        """
        try:
            edge = self.inputs[index].edges[0]
            socket = edge.get_other_socket(self.inputs[index])
            return socket.node
        except IndexError:
            logparams.logging.exception(f"EXC: Trying to get input, but none is attached to {self}")
            return None
        except Exception:
            logparams.logging.exception("Exception occurred")
            return None

    def get_inputs(self, index: int=0) -> List[node.Node]:
        """.

        Todo:
            * May be able to remove this.(Used for Undo function. Not used)
        """
        ins = []
        for edge in self.inputs[index].edges:
            other_socket = edge.get_other_socket(self.inputs[index])
            ins.append(other_socket.node)
        return ins

    def get_outputs(self, index: int=0) -> List[node.Node]:
        """.

        Todo:
            * May be able to remove this.(Used for Undo function. Not used)
        """
        outs = []
        for edge in self.outputs[index].edges:
            other_socket = edge.get_other_socket(self.outputs[index])
            outs.append(other_socket.node)
        return outs
