from abc import ABC, abstractmethod
import asyncio
from typing import Callable, List, Optional
import inspect
from injector import inject

class BehaviorTreeNode(ABC):
    @abstractmethod
    async def run(self) -> bool:
        raise NotImplementedError

class NodeState:
    def __init__(self, node : BehaviorTreeNode, status):
        self.nodes = node
        self.status = status
        
class StateManager:
    def __init__(self) -> None:
        self.states = []
        self.actions = []

    def add(self, node: BehaviorTreeNode, status: bool) -> None:
        state = NodeState(node, status)
        self.states.append(state)
    
    def get_last_state(self):
        if self.states:
            return self.states[-1]
        return None
    
    def get_last_action(self):
        if self.actions:
            return self.actions[-1]
        return None

    def clear(self) -> None:
        self.node.clear()
        self.actions.clear()

class CompositeNode(BehaviorTreeNode):
    def __init__(self, children: List[BehaviorTreeNode]) -> None:
        self.children = children

class SelectorNode(CompositeNode):
    async def run(self) -> bool:
        for child in self.children:
            if await child.run():
                return True
        return False

class SequenceNode(CompositeNode):
    async def run(self) -> bool:
        for child in self.children:
            if not await child.run():
                return False
        return True

class ConditionNode(BehaviorTreeNode):
    def __init__(self, condition: Callable[[], bool]) -> None:
        self.condition = condition

    async def run(self) -> bool:
        if asyncio.iscoroutinefunction(self.condition):
            return await self.condition()
        else:
            return self.condition()

class ActionNode(BehaviorTreeNode):
    def __init__(self, action: Callable[[], bool]) -> None:
        self.action = action

    async def run(self) -> bool:
        return await self.action()

class BehaviorTree:
    def __init__(self) -> None:
        self.state_manager = StateManager()
        self.root: Optional[BehaviorTreeNode] = None
        self.nodes: List[BehaviorTreeNode] = []

    def add_action(self, action: Callable[[], bool]) -> ActionNode:
        node = ActionNode(action)
        self.nodes.append(node)
        return node

    def add_condition(self, condition: Callable[[], bool]) -> ConditionNode:
        node = ConditionNode(condition)
        self.nodes.append(node)
        return node

    def add_sequence(self, nodes: List[BehaviorTreeNode]) -> SequenceNode:
        sequence_node = SequenceNode(nodes)
        self.nodes.append(sequence_node)
        return sequence_node

    def add_selector(self, nodes: List[BehaviorTreeNode]) -> SelectorNode:
        selector_node = SelectorNode(nodes)
        self.nodes.append(selector_node)
        return selector_node

    def update(self, root: BehaviorTreeNode) -> None:
        self.root = root

    async def run(self) -> None:
        if self.root is None:
            raise ValueError("Корневой узел дерева поведения не установлен.")
        success = await self.root.run()
        if not success:
            print("Ошибка выполнения дерева поведения.")