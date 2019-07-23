# built-in libraries
# ...

# external libraries
# ...

# internal libraries
from ouroboros.conf import CLOUD, STONE
from ouroboros.core import (Type,
                            Event,
                            Item,
                            Mask, Mode,
                            Node, Edge, Face,
                            iterdata, iterctrl,
                            Task,
                            Image,
                            run)

# constants
# ...


def test_type(mocker):
    default = mocker.Mock()
    object_hook = mocker.Mock()
    obj = Type("py.test", "!py/test", bool, default, object_hook)
    assert obj.default is default
    assert obj.object_hook is object_hook
    assert STONE["py.test", bool] is obj


def test_event_empty():
    obj = Event()
    assert len(obj.cbs) == 0


def test_event(mocker):
    cb1 = mocker.Mock()
    cb2 = mocker.Mock()
    obj = Event([cb1, cb2])
    assert len(obj.cbs) == 2
    assert cb1 in obj.cbs
    assert cb2 in obj.cbs


def test_item(mocker):
    Event = mocker.patch("ouroboros.core.Event")
    data = mocker.Mock()
    key = mocker.Mock()
    ctrl = [key]
    obj = Item(data, ctrl)
    assert obj.data is data
    Event.assert_called_once_with()
    assert key in obj.ctrl
    assert obj.ctrl[key] is Event.return_value


def test_mask(mocker):
    gets = mocker.Mock()
    sets = mocker.Mock()
    obj = Mask(gets, sets)
    assert obj.gets is gets
    assert obj.sets is sets


def test_mode(mocker):
    Mask = mocker.patch("ouroboros.core.Mask")
    reqs = mocker.Mock()
    pros = mocker.Mock()
    ins = mocker.Mock()
    outs = mocker.Mock()
    obj = Mode(ins, outs, reqs, pros)
    assert Mask.call_count == 2
    assert obj.data is Mask.return_value
    assert obj.ctrl is Mask.return_value


def test_node(mocker):
    Mode = mocker.patch("ouroboros.core.Mode")
    evs = mocker.Mock()
    args = mocker.Mock()
    ins = mocker.Mock()
    reqs = mocker.Mock()
    outs = mocker.Mock()
    pros = mocker.Mock()
    obj = Node(evs, args, ins, reqs, outs, pros)
    assert Mode.call_count == 2
    assert obj.init is Mode.return_value
    assert obj.main is Mode.return_value


def test_edge_empty():
    obj = Edge()
    assert isinstance(obj.data, dict)
    assert len(obj.data) == 0
    assert isinstance(obj.ctrl, dict)
    assert len(obj.ctrl) == 0


def test_edge(mocker):
    data = mocker.Mock()
    ctrl = mocker.Mock()
    obj = Edge(data, ctrl)
    assert obj.data is data
    assert obj.ctrl is ctrl


def test_face(mocker):
    iterdata = mocker.patch("ouroboros.core.iterdata")
    iterctrl = mocker.patch("ouroboros.core.iterctrl")
    node = mocker.Mock()
    edge = mocker.Mock()
    item = mocker.Mock()
    obj = Face(node, edge, item)
    iterdata.assert_called_once_with(node, edge, item)
    iterctrl.assert_called_once_with(node, edge, item)
    assert obj.data is iterdata.return_value
    assert obj.ctrl is iterctrl.return_value


def test_iterdata_init(mocker):
    node = mocker.MagicMock()
    edge = mocker.MagicMock()
    item = mocker.MagicMock()
    
    pros = mocker.Mock()
    key = mocker.Mock()
    
    node.init.data.gets.__len__.return_value = 1
    node.init.data.gets.__iter__.return_value = [key]
    
    cor = iterdata(node, edge, item)
    reqs = cor.send(pros)
    list(reqs)
    
    edge.data.get.assert_called_once_with(key, key)
    item.data.get.assert_called_once_with(edge.data.get.return_value)
    node.init.data.gets.__iter__.assert_called_once_with()


def test_iterdata_main_gets(mocker):
    node = mocker.MagicMock()
    edge = mocker.MagicMock()
    item = mocker.MagicMock()
    
    pros = mocker.Mock()
    key = mocker.Mock()
    
    node.init.data.gets.__len__.return_value = 0
    node.main.data.gets.__len__.return_value = 1
    node.main.data.gets.__iter__.return_value = [key]
    node.main.data.sets.__len__.return_value = 0
    
    cor = iterdata(node, edge, item)
    list(cor.send(pros))
    
    edge.data.get.assert_called_once_with(key, key)
    item.data.get.assert_called_once_with(edge.data.get.return_value)
    node.main.data.gets.__iter__.assert_called_once_with()


def test_iterdata_main_sets(mocker):
    node = mocker.MagicMock()
    edge = mocker.MagicMock()
    item = mocker.MagicMock()

    pro = mocker.Mock()
    pros = [pro]
    key = mocker.Mock()
    
    node.init.data.gets.__len__.return_value = 0
    node.main.data.gets.__len__.return_value = 0
    node.main.data.sets.__len__.return_value = 1
    node.main.data.sets.__iter__.return_value = [key]
    
    cor = iterdata(node, edge, item)
    cor.send(pros)
    
    edge.data.get.assert_called_once_with(key, key)
    item.data.update.assert_called_once_with({edge.data.get.return_value: pro})


def test_iterctrl_init(mocker):
    node = mocker.MagicMock()
    edge = mocker.MagicMock()
    item = mocker.MagicMock()
    
    key = mocker.Mock()
    
    node.init.ctrl.gets.__len__.return_value = 1
    node.init.ctrl.gets.__iter__.return_value = [key]
    
    cor = iterctrl(node, edge, item)
    list(next(cor))
    
    edge.ctrl.get.assert_called_once_with(key, key)
    item.ctrl.get.assert_called_once_with(edge.ctrl.get.return_value)
    node.init.ctrl.gets.__iter__.assert_called_once_with()


def test_iterctrl_main_gets(mocker):
    node = mocker.MagicMock()
    edge = mocker.MagicMock()
    item = mocker.MagicMock()
    
    outs = mocker.Mock()
    key = mocker.Mock()
    
    node.init.ctrl.gets.__len__.return_value = 0
    node.main.ctrl.gets.__len__.return_value = 1
    node.main.ctrl.gets.__iter__.return_value = [key]
    node.main.ctrl.sets.__len__.return_value = 0
    
    cor = iterctrl(node, edge, item)
    next(cor)
    list(cor.send(outs))
    
    edge.ctrl.get.assert_called_once_with(key, key)
    item.ctrl.get.assert_called_once_with(edge.ctrl.get.return_value)
    node.init.ctrl.gets.__iter__.assert_called_once_with()


def test_iterctrl_main_sets(mocker):
    node = mocker.MagicMock()
    edge = mocker.MagicMock()
    item = mocker.MagicMock()

    out = mocker.Mock()
    outs = [out]
    key = mocker.Mock()
    
    node.init.ctrl.gets.__len__.return_value = 0
    node.main.ctrl.gets.__len__.return_value = 0
    node.main.ctrl.sets.__len__.return_value = 1
    node.main.ctrl.sets.__iter__.return_value = [key]
    
    cor = iterctrl(node, edge, item)
    next(cor)
    evs = list(cor.send(outs))
    
    edge.ctrl.get.assert_called_once_with(key, key)
    item.ctrl.get.assert_called_once_with(edge.ctrl.get.return_value)
    node.main.ctrl.sets.__iter__.assert_called_once_with()

    assert len(evs) == 1
    ev = evs[0]
    assert ev == (item.ctrl.get.return_value, out)

    
def test_task(mocker):
    p = mocker.Mock()
    gen = mocker.Mock()
    obj = Task(p, gen)
    assert obj.p is p
    assert obj.gen is gen


def test_task_call(mocker):
    p = mocker.Mock()
    gen = mocker.Mock()
    obj = Task(p, gen)


def test_image(mocker):
    tag = mocker.Mock()
    node = mocker.Mock()
    obj = Image(tag, test=node)
    assert obj.tag is tag
    assert "test" in obj.nodes
    assert obj.nodes["test"] is node
