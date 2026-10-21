class EditCommand:
    """A reversible set of translation cell changes.

    ``changes`` is a list of ``(file_idx, entry_idx, old_value, new_value)``
    tuples describing every cell touched by the command. ``focus`` optionally
    points at the cell that should regain focus once the command is undone or
    redone.
    """

    def __init__(self, changes, focus=None, label=""):
        self.changes = [
            (file_idx, entry_idx, old, new)
            for file_idx, entry_idx, old, new in changes
        ]
        self.focus = focus
        self.label = label

    @property
    def target(self):
        """Cell edited by this command, or None when it spans several cells."""
        if len(self.changes) != 1:
            return None
        return (self.changes[0][0], self.changes[0][1])

    def is_noop(self):
        return all(old == new for _, _, old, new in self.changes)

    def update_value(self, value):
        """Replace the new value of a single cell command."""
        file_idx, entry_idx, old, _ = self.changes[0]
        self.changes[0] = (file_idx, entry_idx, old, value)

    def files(self):
        return {file_idx for file_idx, _, _, _ in self.changes}

    def apply(self, data, use_new):
        """Write the old (undo) or new (redo) values into ``data``."""
        for file_idx, entry_idx, old, new in self.changes:
            value = new if use_new else old
            data[file_idx]["entries"][entry_idx]["translated"] = value


class UndoStack:
    """Bounded undo/redo history of :class:`EditCommand` objects."""

    def __init__(self, limit=200):
        self.limit = limit
        self._undo = []
        self._redo = []

    def clear(self):
        self._undo.clear()
        self._redo.clear()

    def push(self, command):
        """Record a new command, discarding any pending redo history."""
        if command is None or not command.changes:
            return
        self._redo.clear()
        self._undo.append(command)
        while len(self._undo) > self.limit:
            self._undo.pop(0)

    def drop_current(self):
        """Remove the newest undo command without touching the redo stack."""
        if not self._undo:
            return None
        return self._undo.pop()

    def undo(self):
        if not self._undo:
            return None
        command = self._undo.pop()
        self._redo.append(command)
        return command

    def redo(self):
        if not self._redo:
            return None
        command = self._redo.pop()
        self._undo.append(command)
        return command

    @property
    def current(self):
        return self._undo[-1] if self._undo else None

    @property
    def can_undo(self):
        return bool(self._undo)

    @property
    def can_redo(self):
        return bool(self._redo)
