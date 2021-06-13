class Node:
    def __init__(self, value, next):
        self.value = value
        self.next = next


class SinglyLinkedList:
    def __init__(self):
        self.head = None

    def push_front(self, value):
        self.head = Node(value, self.head)

    def push_back(self, value):
        if self.head is None:
            self.head = Node(value, self.head)
            return

        curr_node = self.head
        while curr_node.next is not None:
            curr_node = curr_node.next
        curr_node.next = Node(value, curr_node.next)

    def pop(self):
        pop_value = self.head.value
        self.head = self.head.next
        return pop_value

    def insert(self, index, value):
        if index == 0:
            self.head = Node(value, self.head)
            return value

        curr_node = self.head
        cnt = 0
        while curr_node is not None:
            if cnt == index - 1:
                curr_node.next = Node(value, curr_node.next)
                return value

            cnt += 1
            curr_node = curr_node.next

        return None

    def delete(self, index):
        if self.head is None:
            return None

        curr_node = self.head
        cnt = 0
        while curr_node.next is not None:
            if cnt == index - 1:
                curr_node.next = curr_node.next.next
                return curr_node.value

            cnt += 1
            curr_node = curr_node.next

        return None

    def delete_by_value(self, value):
        curr_node = self.head
        while curr_node.next is not None:
            if curr_node.next.value == value:
                curr_node.next = curr_node.next.next
                return value

            curr_node = curr_node.next

        return None

    def search_node(self, index):
        curr_node = self.head
        cnt = 0
        while curr_node is not None:
            if index == cnt:
                return curr_node
            cnt += 1
            curr_node = curr_node.next

        return None

    def get(self, index):
        curr_node = self.head
        cnt = 0
        while curr_node is not None:
            if index == cnt:
                return curr_node.value
            cnt += 1
            curr_node = curr_node.next

        return None

    def reverse(self):
        curr_node = self.head
        new_head = None
        while curr_node is not None:
            new_head = Node(curr_node.value, new_head)
            curr_node = curr_node.next

        self.head = new_head

    def show(self):
        curr_node = self.head
        show_str = ""
        while curr_node is not None:
            show_str += str(curr_node.value) + " -> "
            curr_node = curr_node.next
        return show_str + "None"

    def size(self):
        return self.__len__()

    def clear(self):
        self.__init__()

    def __len__(self):
        curr_node = self.head
        cnt = 0
        while curr_node is not None:
            cnt += 1
            curr_node = curr_node.next
        return cnt


if __name__ == "__main__":
    linked_list = SinglyLinkedList()
    linked_list.push_front(1)
    linked_list.push_front(2)
    linked_list.push_back(0)
    assert linked_list.size() == 3
    assert linked_list.show() == "2 -> 1 -> 0 -> None"

    linked_list.reverse()
    assert linked_list.show() == "0 -> 1 -> 2 -> None"
    linked_list.reverse()

    pop_value = linked_list.pop()
    assert pop_value == 2
    pop_value = linked_list.pop()
    assert pop_value == 1

    linked_list.push_front(1)
    linked_list.push_front(2)
    assert linked_list.get(0) == 2
    assert linked_list.get(1) == 1
    assert linked_list.get(2) == 0
    assert linked_list.get(3) is None

    linked_list.insert(1, 5)
    assert linked_list.show() == "2 -> 5 -> 1 -> 0 -> None"
    assert linked_list.insert(7, 3) is None
    linked_list.insert(4, 3)
    assert linked_list.show() == "2 -> 5 -> 1 -> 0 -> 3 -> None"

    linked_list.delete(2)
    assert linked_list.show() == "2 -> 5 -> 0 -> 3 -> None"
    assert linked_list.delete(5) is None
    assert linked_list.delete(6) is None

    linked_list.delete_by_value(5)
    assert linked_list.show() == "2 -> 0 -> 3 -> None"
    assert linked_list.delete_by_value(10) is None

    linked_list.clear()
    assert linked_list.size() == 0
