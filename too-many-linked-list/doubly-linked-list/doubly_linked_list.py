class Node:
    def __init__(self, value, prev=None, next=None):
        self.value = value
        self.prev = prev
        self.next = next


# 双方向にすることで、挿入・削除そのものの操作は O(1) で済むが、
# 対象のノードを見つけるのに O(n) かかる...
class DoublyLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    # O(1)
    def push_front(self, value):
        self.size += 1
        new_node = Node(value)
        if self.head is None:
            self.head = new_node
            self.tail = new_node
            return

        new_node.next = self.head
        self.head.prev = new_node
        self.head = new_node

    # O(1)
    def push_back(self, value):
        self.size += 1
        new_node = Node(value)
        if self.tail is None:
            self.head = new_node
            self.tail = new_node
            return

        new_node.prev = self.tail
        self.tail.next = new_node
        self.tail = new_node

    # O(1)
    def pop_front(self):
        self.size -= 1
        pop_value = self.head.value
        self.head = self.head.next
        self.head.prev = None
        return pop_value

    # O(1)
    def pop_back(self):
        self.size -= 1
        pop_value = self.tail.value
        self.tail = self.tail.prev
        self.tail.next = None
        return pop_value

    # O(n)
    def insert(self, index, value):
        # 最後に挿入するとき
        if index == self.size:
            self.push_back(value)
            return

        target_node = self.search_node(index)
        # 挿入場所が見つからないとき
        if target_node is None:
            return None

        if target_node is self.head:
            self.push_front(value)
        else:
            self.size += 1
            new_node = Node(value, target_node.prev, target_node)
            target_node.prev.next = new_node
            target_node.prev = new_node

    # O(n)
    def delete(self, index):
        target_node = self.search_node(index)
        if target_node is None:
            return None

        if target_node is self.tail:
            self.pop_back()
        elif target_node is self.head:
            self.pop_front()
        else:
            self.size -= 1
            target_node.prev.next = target_node.next
            target_node.next.prev = target_node.prev

    # O(n)
    def get(self, index):
        target_node = self.search_node(index)
        return target_node.value if target_node is not None else None

    # O(n)
    def search_node(self, index):
        curr_node = self.head
        cnt = 0
        while curr_node is not None:
            if index == cnt:
                return curr_node
            cnt += 1
            curr_node = curr_node.next

        return None

    # O(n)
    def reverse(self):
        curr_node = self.head
        new_head = None
        while curr_node is not None:
            new_head = Node(curr_node.value, next=new_head)
            if new_head.next is None:
                self.tail = new_head
            else:
                new_head.next.prev = new_head
            curr_node = curr_node.next

        self.head = new_head

    def show(self):
        curr_node = self.head
        show_str = ""
        while curr_node is not None:
            show_str += str(curr_node.value) + " <-> "
            curr_node = curr_node.next
        return show_str + "None"

    def clear(self):
        self.__init__()

    def __len__(self):
        return self.size


if __name__ == "__main__":
    linked_list = DoublyLinkedList()
    linked_list.push_front(1)
    linked_list.push_front(2)
    linked_list.push_back(0)
    assert linked_list.size == 3
    assert linked_list.show() == "2 <-> 1 <-> 0 <-> None"
    assert linked_list.head.value == 2
    assert linked_list.tail.value == 0

    linked_list.reverse()
    assert linked_list.show() == "0 <-> 1 <-> 2 <-> None"
    assert linked_list.head.value == 0
    assert linked_list.tail.value == 2
    linked_list.reverse()

    pop_value = linked_list.pop_front()
    assert pop_value == 2
    pop_value = linked_list.pop_back()
    assert pop_value == 0

    linked_list.push_back(0)
    linked_list.push_front(2)
    assert linked_list.get(0) == 2
    assert linked_list.get(1) == 1
    assert linked_list.get(2) == 0
    assert linked_list.get(3) is None

    linked_list.insert(1, 5)
    assert linked_list.show() == "2 <-> 5 <-> 1 <-> 0 <-> None"
    assert linked_list.insert(7, 3) is None
    linked_list.insert(4, 3)
    assert linked_list.show() == "2 <-> 5 <-> 1 <-> 0 <-> 3 <-> None"
    assert linked_list.size == 5

    linked_list.delete(2)
    assert linked_list.show() == "2 <-> 5 <-> 0 <-> 3 <-> None"
    assert linked_list.delete(5) is None
    assert linked_list.delete(6) is None

    linked_list.clear()
    assert linked_list.size == 0
