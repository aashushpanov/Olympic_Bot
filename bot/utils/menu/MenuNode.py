from aiogram.utils.callback_data import CallbackData

move = CallbackData('move', 'action', 'node', 'data', 'width')


class BaseNode:
    def __init__(self, id: str, parent, callback):
        self._id = id
        self._childs = []
        self._parent = parent
        self._callback = callback

    @property
    def id(self):
        return self._id if self._id else 0

    @property
    def parent(self):
        return self._parent

    @property
    def callback(self):
        return self._callback


class MenuNode(BaseNode):
    def __init__(self, text: str = None, callback=None, parent=None, id=None, row_width=1):
        super().__init__(id=id or 'admin', parent=parent, callback=callback)
        self._text = text
        self._row_width = row_width

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text):
        self._text = text

    async def childs_data(self, **kwargs):
        for child in self._childs:
            yield child.id, child.text, child.callback

    def child(self, child_id: str = None, text: str = None):
        if child_id is not None:
            for child in self._childs:
                if child.id == child_id:
                    return child
        elif text:
            for child in self._childs:
                if child.text == text:
                    return child
        raise KeyError

    def childs(self):
        result = {}
        for child in self._childs:
            result.update({child.id: child})
        return result

    def all_childs(self, result=None):
        if result is None:
            result = {}
        result.update(self.childs())
        for child in self._childs:
            result = child.all_childs(result)
        return result

    def set_child(self, child):
        child._id = self._id + '_' + str(len(self._childs))
        if child.callback is None:
            child._callback = move.new(action='d', node=child.id, data='', width=1)
        self._childs.append(child)
        child._parent = self

    def set_childs(self, childs):
        for child in childs:
            self.set_child(child)

    def prev(self):
        return self._parent

    def clean_childs(self):
        if self._childs:
            for child in self._childs:
                child.clean_childs()
                self._childs.clear()
        else:
            self._parent = None


class NodeGenerator(MenuNode):
    def __init__(self, text, func, id=None, reg_nodes=None, parent=None, callback=None):
        super().__init__(id=id if id else 'gen', parent=parent, callback=callback)
        if reg_nodes is None:
            reg_nodes = []
        self._text = text
        self._func = func
        self._reg_nodes = reg_nodes
        self._sub_childs = []
        self._blind_node = None

    @property
    def func(self):
        return self._func

    async def childs_data(self, **kwargs):
        for child in self._reg_nodes:
            yield child.id, child.text, child.callback
        async for child in self.func(self, **kwargs):
            yield child.id, child.text, child.callback

    def append(self, node):
        self._reg_nodes.append(node)

    def add_blind_node(self, node_id, type='simple', func=None, row_width=1, text=None):
        node_id = self.id + '_' + node_id
        if type == 'simple':
            self._blind_node = BlindNode(node_id, self, row_width=row_width)
        if type == 'generator':
            if text is None:
                text = 'Меню'
            self._blind_node = NodeGenerator(text=text, func=func, id=node_id)
        self._blind_node._parent = self

    def set_sub_child(self, sub_child):
        sub_child._id = self.blind_node.id + '_' + str(len(self.blind_node._childs))
        self._blind_node._childs.append(sub_child)
        sub_child._parent = self.blind_node

    def set_sub_childs(self, sub_childs):
        for sub_child in sub_childs:
            self.set_sub_child(sub_child)

    @property
    def blind_node(self):
        return self._blind_node

    def childs(self):
        result = {}
        for child in self._childs:
            result.update({child.id: child})
        result.update({self.blind_node.id: self.blind_node})
        result.update(self.blind_node.childs())
        return result


class BlindNode(MenuNode):
    def __init__(self, node_id, parent, row_width=1):
        super().__init__(id=node_id, parent=parent, callback=None, row_width=row_width)

    def childs(self):
        result = {}
        for child in self._childs:
            result.update({child.id: child})
        return result
