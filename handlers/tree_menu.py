from aiogram.utils.callback_data import CallbackData

move = CallbackData('id', 'action', 'node')


class MenuNode:
    def __init__(self, text: str = None, callback=None, parent=None):
        self._id = '0'
        self._childs = []
        self._parent = parent
        self.text = text
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


class CancelNode:
    def __init__(self, parent):
        self.text = "Назад"
        self._callback = move.new(action='u', node=parent)

    @property
    def callback(self):
        return self._callback
