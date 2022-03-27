from aiogram.utils.callback_data import CallbackData

move = CallbackData('id', 'action', 'node')


class MenuNode:
    def __init__(self, text: str = None, callback=None, parent=None, id=None):
        self._id = id or 'admin'
        self._childs = []
        self._parent = parent
        self._text = text
        self._callback = callback

    @property
    def callback(self):
        return self._callback

    @property
    def parent(self):
        return self._parent

    @property
    def id(self):
        return self._id if self._id else 0

    @property
    def text(self):
        return self._text

    @property
    def childs_data(self):
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
            child._callback = move.new(action='d', node=child.id)
        self._childs.append(child)
        child._parent = self

    def set_childs(self, childs):
        for child in childs:
            self.set_child(child)

    def __next__(self, child_id):
        return self._childs[child_id]

    def prev(self):
        return self._parent


class NodeGenerator(MenuNode):
    def __init__(self, text, func, reg_nodes=[], parent=None, callback=None):
        self._id = 'gen'
        self._callback = callback
        self._text = text
        self._childs = func
        self._reg_nodes = reg_nodes
        self._parent = parent

    def __iter__(self):
        return self

    def __next__(self, *kwargs):
        for child in self._reg_nodes:
            yield child.id, child.text, child.callback
        for child in self._childs(kwargs):
            yield child.id, child.text, child.callback

    def append(self, node):
        self._reg_nodes.append(node)