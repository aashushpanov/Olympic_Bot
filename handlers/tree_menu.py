from aiogram.utils.callback_data import CallbackData

move = CallbackData('action', 'node')


class TreeMenuNode:
    def __init__(self, text: str, callback=None, parent=None):
        self._id = None
        self._childs = []
        self._parent = parent
        self.text = text
        self._callback = callback or move.new(action='down', node=self)

    @property
    def callback(self):
        return self._callback

    @property
    def id(self):
        return self._id if self._id else 0

    def set_child(self, child):
        child._id = len(self._childs)
        self._childs.append(child)
        child._parent = self

    def __next__(self, child_id):
        return self._childs[child_id]

    def prev(self):
        return self._parent

    @property
    def childs(self):
        result = set()
        for child in self._childs:
            result.add([child.id, child.text, child.callback])
        return result


class CancelNode:
    def __init__(self, parent):
        self.text = "Назад"
        self._callback = move.new(action='up', node=parent)

    @property
    def callback(self):
        return self._callback
