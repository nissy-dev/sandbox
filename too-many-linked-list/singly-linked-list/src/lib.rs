struct Node {
    value: usize,
    next: Option<Box<Node>>,
}

pub struct SinglyLinkedList {
    // サイズは、事前に計算することで O(1) で求められる
    size: usize,
    // Boxはヒープ領域を利用するので、一定量のメモリまでしか確保されない
    // スタックだと無限にメモリを確保しようとしてしまう
    head: Option<Box<Node>>,
}

// 機能的にもはやスタックである
impl SinglyLinkedList {
    pub fn new() -> Self {
        Self {
            size: 0,
            head: None,
        }
    }

    // O(1)
    pub fn push_front(&mut self, value: usize) {
        self.size += 1;
        let new_node = Box::new(Node {
            value: value,
            next: self.head.take(),
        });
        self.head = Some(new_node)
    }

    // O(n)
    pub fn push_back(&mut self, value: usize) {
        self.size += 1;
        let mut curr_node = &mut self.head;
        while let Some(boxed_node) = curr_node {
            curr_node = &mut boxed_node.next;
        }
        *curr_node = Some(Box::new(Node {
            value: value,
            next: None,
        }));
    }

    // O(1)
    pub fn pop(&mut self) -> Option<usize> {
        self.size -= 1;
        match self.head.take() {
            None => None,
            Some(node) => {
                self.head = node.next;
                Some(node.value)
            }
        }
    }

    // O(n)
    pub fn insert(&mut self, index: usize, value: usize) -> Option<usize> {
        self.size += 1;

        // 最後に挿入するとき
        if index + 2 == self.size() {
            self.push_back(value);
            return Some(value);
        }

        let mut curr_node = &mut self.head;
        let mut cnt: usize = 0;
        loop {
            match curr_node {
                None => break,
                Some(_boxed_node) if cnt == index => {
                    *curr_node = Some(Box::new(Node {
                        value: value,
                        next: curr_node.take(),
                    }));
                    return Some(value);
                }
                Some(boxed_node) => {
                    curr_node = &mut boxed_node.next;
                }
            }
            cnt += 1
        }
        return None;
    }

    // O(n)
    pub fn delete(&mut self, index: usize) -> Option<usize> {
        self.size -= 1;
        let mut curr_node = &mut self.head;
        let mut cnt: usize = 0;
        loop {
            match curr_node {
                None => break,
                Some(boxed_node) if cnt == index => {
                    let removed_value = boxed_node.value;
                    *curr_node = boxed_node.next.take();
                    return Some(removed_value);
                }
                Some(boxed_node) => {
                    curr_node = &mut boxed_node.next;
                }
            }
            cnt += 1
        }
        return None;
    }

    // O(n)
    pub fn delete_by_value(&mut self, value: usize) -> Option<usize> {
        self.size -= 1;
        let mut curr_node = &mut self.head;
        loop {
            match curr_node {
                None => break,
                Some(boxed_node) if boxed_node.value == value => {
                    *curr_node = boxed_node.next.take();
                    return Some(value);
                }
                Some(boxed_node) => {
                    curr_node = &mut boxed_node.next;
                }
            }
        }

        return None;

        // これでなんで動かないのか、分からない...
        // let mut curr_node = &mut self.head;
        // while let Some(boxed_node) = curr_node {
        //     if boxed_node.value == value {
        //         *curr_node = boxed_node.next.take();
        //     } else {
        //         curr_node = &mut boxed_node.next;
        //     }
        // }
    }

    // O(n)
    pub fn get(&self, index: usize) -> Option<usize> {
        let mut curr_node = &self.head;
        let mut cnt: usize = 0;
        while let Some(boxed_node) = curr_node {
            if cnt == index {
                return Some(boxed_node.value);
            }
            cnt += 1;
            curr_node = &boxed_node.next;
        }
        return None;
    }

    // O(n)
    pub fn reverse(&mut self) {
        let mut curr_node = &mut self.head;
        let mut new_head: Option<Box<Node>> = None;
        while let Some(boxed_node) = curr_node {
            new_head = Some(Box::new(Node {
                value: boxed_node.value,
                next: new_head.take(),
            }));
            curr_node = &mut boxed_node.next;
        }
        self.head = new_head
    }

    pub fn size(&self) -> usize {
        self.size
    }

    pub fn show(&self) -> String {
        let mut curr_node = &self.head;
        let mut show_str = String::from("");
        while let Some(boxed_node) = curr_node {
            show_str += &(boxed_node.value.to_string() + " -> ");
            curr_node = &boxed_node.next;
        }
        return show_str + "None";
    }

    pub fn clear(&mut self) {
        self.size = 0;
        self.head = None;
    }
}

impl Drop for SinglyLinkedList {
    fn drop(&mut self) {
        let mut cur_link = self.head.take();
        while let Some(mut boxed_node) = cur_link {
            cur_link = boxed_node.next.take();
        }
    }
}

#[cfg(test)]
mod tests {
    use super::SinglyLinkedList;

    #[test]
    fn linked_list_test() {
        let mut list = SinglyLinkedList::new();

        list.push_front(1);
        list.push_front(2);
        list.push_back(0);
        assert_eq!(list.size(), 3);
        // 2が先頭、0が末端
        assert_eq!(list.show(), "2 -> 1 -> 0 -> None");

        // reverse
        list.reverse();
        assert_eq!(list.show(), "0 -> 1 -> 2 -> None");
        list.reverse();

        // pop
        assert_eq!(list.pop(), Some(2));
        assert_eq!(list.pop(), Some(1));

        // get
        list.push_front(1);
        list.push_front(2);
        assert_eq!(list.get(0), Some(2));
        assert_eq!(list.get(1), Some(1));
        assert_eq!(list.get(2), Some(0));
        assert_eq!(list.get(3), None);

        // insert
        list.insert(1, 5);
        assert_eq!(list.show(), "2 -> 5 -> 1 -> 0 -> None");
        assert_eq!(list.insert(7, 3), None);
        list.insert(4, 3);
        assert_eq!(list.show(), "2 -> 5 -> 1 -> 0 -> 3 -> None");

        // delete
        assert_eq!(list.delete(2), Some(1));
        assert_eq!(list.show(), "2 -> 5 -> 0 -> 3 -> None");
        assert_eq!(list.delete(5), None);
        assert_eq!(list.delete(6), None);

        // delete by value
        list.delete_by_value(5);
        assert_eq!(list.show(), "2 -> 0 -> 3 -> None");
        assert_eq!(list.delete_by_value(10), None);

        // clear
        list.clear();
        assert_eq!(list.size(), 0);
    }
}
