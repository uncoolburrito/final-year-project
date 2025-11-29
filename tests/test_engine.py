import pytest
from src.engine.core import ExpansionEngine
from src.engine.store import Store
from src.common.models import Snippet, TriggerType

class MockStore(Store):
    def __init__(self):
        self.snippets = []
        self.profiles = []
        self.settings = None

    def load(self): pass
    def save(self): pass

def test_expansion_basic():
    store = MockStore()
    store.snippets.append(Snippet(abbreviation="btw", expansion="by the way", trigger=TriggerType.SPACE))
    
    engine = ExpansionEngine(store)
    
    # Type 'b', 't', 'w'
    assert engine.process_key("b") is None
    assert engine.process_key("t") is None
    assert engine.process_key("w") is None
    
    # Type space (trigger)
    result = engine.process_key(" ")
    assert result is not None
    
    backspaces, text, cursor = result
    assert backspaces == 4 # b, t, w, space
    assert text == "by the way"
    assert cursor == 0

def test_expansion_instant():
    store = MockStore()
    store.snippets.append(Snippet(abbreviation="omg", expansion="oh my god", trigger=TriggerType.NONE))
    
    engine = ExpansionEngine(store)
    
    assert engine.process_key("o") is None
    assert engine.process_key("m") is None
    result = engine.process_key("g")
    
    assert result is not None
    backspaces, text, cursor = result
    assert backspaces == 3
    assert text == "oh my god"

def test_cursor_placeholder():
    store = MockStore()
    store.snippets.append(Snippet(abbreviation="func", expansion="def func():\n    {{cursor}}", trigger=TriggerType.NONE))
    
    engine = ExpansionEngine(store)
    
    # Simulate typing 'func'
    engine.process_key("f")
    engine.process_key("u")
    engine.process_key("n")
    result = engine.process_key("c")
    
    assert result is not None
    _, text, cursor = result
    assert "{{cursor}}" not in text
    assert cursor == 0 # It's at the end
