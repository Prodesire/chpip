import sys

import pytest

from chpip.core import PY2, ChpipManager

if PY2:
    import shutil
    import itertools
    import gc
    from weakref import ref
    import warnings
    from tempfile import mkdtemp, template


    class finalize(object):
        """Class for finalization of weakrefable objects

        finalize(obj, func, *args, **kwargs) returns a callable finalizer
        object which will be called when obj is garbage collected. The
        first time the finalizer is called it evaluates func(*arg, **kwargs)
        and returns the result. After this the finalizer is dead, and
        calling it just returns None.

        When the program exits any remaining finalizers for which the
        atexit attribute is true will be run in reverse order of creation.
        By default atexit is true.
        """

        # Finalizer objects don't have any state of their own.  They are
        # just used as keys to lookup _Info objects in the registry.  This
        # ensures that they cannot be part of a ref-cycle.

        __slots__ = ()
        _registry = {}
        _shutdown = False
        _index_iter = itertools.count()
        _dirty = False
        _registered_with_atexit = False

        class _Info(object):
            __slots__ = ("weakref", "func", "args", "kwargs", "atexit", "index")

        def __init__(*args, **kwargs):
            if len(args) >= 3:
                self, obj, func = args[:3]
                args = args[3:]
            elif not args:
                raise TypeError("descriptor '__init__' of 'finalize' object "
                                "needs an argument")
            else:
                if 'func' not in kwargs:
                    raise TypeError('finalize expected at least 2 positional '
                                    'arguments, got %d' % (len(args) - 1))
                func = kwargs.pop('func')
                if len(args) >= 2:
                    self, obj = args[:2]
                    args = args[2:]
                    import warnings
                    warnings.warn("Passing 'func' as keyword argument is deprecated",
                                  DeprecationWarning, stacklevel=2)
                else:
                    if 'obj' not in kwargs:
                        raise TypeError('finalize expected at least 2 positional '
                                        'arguments, got %d' % (len(args) - 1))
                    obj = kwargs.pop('obj')
                    self = args[0]
                    args = args[1:]
                    import warnings
                    warnings.warn("Passing 'obj' as keyword argument is deprecated",
                                  DeprecationWarning, stacklevel=2)
            args = tuple(args)

            if not self._registered_with_atexit:
                # We may register the exit function more than once because
                # of a thread race, but that is harmless
                import atexit
                atexit.register(self._exitfunc)
                finalize._registered_with_atexit = True
            info = self._Info()
            info.weakref = ref(obj, self)
            info.func = func
            info.args = args
            info.kwargs = kwargs or None
            info.atexit = True
            info.index = next(self._index_iter)
            self._registry[self] = info
            finalize._dirty = True

        __init__.__text_signature__ = '($self, obj, func, /, *args, **kwargs)'

        def __call__(self, _=None):
            """If alive then mark as dead and return func(*args, **kwargs);
            otherwise return None"""
            info = self._registry.pop(self, None)
            if info and not self._shutdown:
                return info.func(*info.args, **(info.kwargs or {}))

        def detach(self):
            """If alive then mark as dead and return (obj, func, args, kwargs);
            otherwise return None"""
            info = self._registry.get(self)
            obj = info and info.weakref()
            if obj is not None and self._registry.pop(self, None):
                return (obj, info.func, info.args, info.kwargs or {})

        def peek(self):
            """If alive then return (obj, func, args, kwargs);
            otherwise return None"""
            info = self._registry.get(self)
            obj = info and info.weakref()
            if obj is not None:
                return (obj, info.func, info.args, info.kwargs or {})

        @property
        def alive(self):
            """Whether finalizer is alive"""
            return self in self._registry

        @property
        def atexit(self):
            """Whether finalizer should be called at exit"""
            info = self._registry.get(self)
            return bool(info) and info.atexit

        @atexit.setter
        def atexit(self, value):
            info = self._registry.get(self)
            if info:
                info.atexit = bool(value)

        def __repr__(self):
            info = self._registry.get(self)
            obj = info and info.weakref()
            if obj is None:
                return '<%s object at %#x; dead>' % (type(self).__name__, id(self))
            else:
                return '<%s object at %#x; for %r at %#x>' % \
                       (type(self).__name__, id(self), type(obj).__name__, id(obj))

        @classmethod
        def _select_for_exit(cls):
            # Return live finalizers marked for exit, oldest first
            L = [(f, i) for (f, i) in cls._registry.items() if i.atexit]
            L.sort(key=lambda item: item[1].index)
            return [f for (f, i) in L]

        @classmethod
        def _exitfunc(cls):
            # At shutdown invoke finalizers for which atexit is true.
            # This is called once all other non-daemonic threads have been
            # joined.
            reenable_gc = False
            try:
                if cls._registry:
                    import gc
                    if gc.isenabled():
                        reenable_gc = True
                        gc.disable()
                    pending = None
                    while True:
                        if pending is None or finalize._dirty:
                            pending = cls._select_for_exit()
                            finalize._dirty = False
                        if not pending:
                            break
                        f = pending.pop()
                        try:
                            # gc is disabled, so (assuming no daemonic
                            # threads) the following is the only line in
                            # this function which might trigger creation
                            # of a new finalizer
                            f()
                        except Exception:
                            sys.excepthook(*sys.exc_info())
                        assert f not in cls._registry
            finally:
                # prevent any more finalizers from executing during shutdown
                finalize._shutdown = True
                if reenable_gc:
                    gc.enable()


    class TemporaryDirectory(object):
        """Create and return a temporary directory.  This has the same
        behavior as mkdtemp but can be used as a context manager.  For
        example:

            with TemporaryDirectory() as tmpdir:
                ...

        Upon exiting the context, the directory and everything contained
        in it are removed.
        """

        def __init__(self, suffix='', prefix=template, dir=None):
            self.name = mkdtemp(suffix, prefix, dir)
            self._finalizer = finalize(
                self, self._cleanup, self.name,
                warn_message="Implicitly cleaning up {!r}".format(self))

        @classmethod
        def _cleanup(cls, name, warn_message):
            shutil.rmtree(name)
            warnings.warn(warn_message, RuntimeWarning)

        def __repr__(self):
            return "<{} {!r}>".format(self.__class__.__name__, self.name)

        def __enter__(self):
            return self.name

        def __exit__(self, exc, value, tb):
            self.cleanup()

        def cleanup(self):
            if self._finalizer.detach():
                shutil.rmtree(self.name)
else:
    from tempfile import TemporaryDirectory


@pytest.fixture(scope='function')
def chpip_manager():
    with TemporaryDirectory() as tmp_dirname:
        chpip = ChpipManager(pip_dirname=tmp_dirname)
        yield chpip
