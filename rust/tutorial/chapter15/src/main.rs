use std::cell::RefCell;
use std::ops::Deref;
use std::rc::{Rc, Weak};
use List::{Cons, Nil};

fn main() {
    let b = Box::new(5);
    println!("b = {}", b);

    let list = Cons(1, Box::new(Cons(2, Box::new(Cons(3, Box::new(Nil))))));

    let x = 5;
    let y = &x;
    assert_eq!(5, x);
    // 参照は比較できない
    // assert_eq!(5, y);
    assert_eq!(5, *y);

    let y_box = Box::new(x);
    assert_eq!(5, *y_box);

    let y_mybox = MyCBox::new(x);
    assert_eq!(5, *y_mybox);

    // let y_mybox = MyBox::new(x);
    // assert_eq!(5, *y_mybox);

    let m = MyCBox::new(String::from("Rust"));
    hello(&m);

    let m = MyBox::new(String::from("Rust"));
    // hello(&m);
    // hello(&(*m)[..]);

    let c = CustomSmartPointer {
        data: String::from("my stuff"),
    };
    let d = CustomSmartPointer {
        data: String::from("other stuff"),
    };
    println!("CustomSmartPointers created.");
    // invalid
    // c.drop();
    // valid
    drop(c);
    // mainの終端の前にCustomSmartPointerがドロップされた
    println!("CustomSmartPointer dropped before the end of main.");

    let a = Cons(5, Box::new(Cons(10, Box::new(Nil))));
    let b = Cons(3, Box::new(a));
    // エラー：すでに a は move されている
    // let c = Cons(4, Box::new(a));

    let a = Rc::new(CList::Cons(
        5,
        Rc::new(CList::Cons(10, Rc::new(CList::Nil))),
    ));
    let b = CList::Cons(3, Rc::clone(&a));
    let c = CList::Cons(4, Rc::clone(&a));

    println!("count after creating a = {}", Rc::strong_count(&a));
    let b = CList::Cons(3, Rc::clone(&a));
    println!("count after creating b = {}", Rc::strong_count(&a));
    {
        let c = CList::Cons(4, Rc::clone(&a));
        println!("count after creating c = {}", Rc::strong_count(&a));
    }
    println!("count after c goes out of scope = {}", Rc::strong_count(&a));

    let value = Rc::new(RefCell::new(5));
    let a = Rc::new(CCList::Cons(Rc::clone(&value), Rc::new(CCList::Nil)));
    let b = CCList::Cons(Rc::new(RefCell::new(6)), Rc::clone(&a));
    let c = CCList::Cons(Rc::new(RefCell::new(10)), Rc::clone(&a));
    // 表面上は読み取り専用 immutable なオブジェクトを mutable に扱える
    *value.borrow_mut() += 10;
    println!("a after = {:?}", a);
    println!("b after = {:?}", b);
    println!("c after = {:?}", c);

    // 循環参照の話
    let a = Rc::new(CCCList::Cons(5, RefCell::new(Rc::new(CCCList::Nil))));
    // aの最初の参照カウント = {}
    println!("a initial rc count = {}", Rc::strong_count(&a));
    // aの次の要素は = {:?}
    println!("a next item = {:?}", a.tail());

    let b = Rc::new(CCCList::Cons(10, RefCell::new(Rc::clone(&a))));
    // b作成後のaの参照カウント = {}
    println!("a rc count after b creation = {}", Rc::strong_count(&a));
    // bの最初の参照カウント = {}
    println!("b initial rc count = {}", Rc::strong_count(&b));
    // bの次の要素 = {:?}
    println!("b next item = {:?}", b.tail());

    if let Some(link) = a.tail() {
        *link.borrow_mut() = Rc::clone(&b);
    }

    // aを変更後のbの参照カウント = {}
    println!("b rc count after changing a = {}", Rc::strong_count(&b));
    // aを変更後のaの参照カウント = {}
    println!("a rc count after changing a = {}", Rc::strong_count(&a));
    // 循環参照が起きてスタックオーバーフロー
    // println!("a next item = {:?}", a.tail()); // aの次の要素 = {:?}

    // 木構造
    let leaf = Rc::new(Node {
        value: 3,
        children: RefCell::new(vec![]),
    });

    let branch = Rc::new(Node {
        value: 5,
        children: RefCell::new(vec![Rc::clone(&leaf)]),
    });

    let leaf = Rc::new(CNode {
        value: 3,
        parent: RefCell::new(Weak::new()),
        children: RefCell::new(vec![]),
    });
    // leafの親 = {:?}
    println!("leaf parent = {:?}", leaf.parent.borrow().upgrade());

    let branch = Rc::new(CNode {
        value: 5,
        parent: RefCell::new(Weak::new()),
        children: RefCell::new(vec![Rc::clone(&leaf)]),
    });
    *leaf.parent.borrow_mut() = Rc::downgrade(&branch);
    println!("leaf parent = {:?}", leaf.parent.borrow().upgrade());

    let leaf = Rc::new(CNode {
        value: 3,
        parent: RefCell::new(Weak::new()),
        children: RefCell::new(vec![]),
    });

    println!(
        // leafのstrong_count = {}, weak_count = {}
        "leaf strong = {}, weak = {}",
        Rc::strong_count(&leaf),
        Rc::weak_count(&leaf),
    );

    {
        let branch = Rc::new(CNode {
            value: 5,
            parent: RefCell::new(Weak::new()),
            children: RefCell::new(vec![Rc::clone(&leaf)]),
        });

        *leaf.parent.borrow_mut() = Rc::downgrade(&branch);

        println!(
            // branchのstrong_count = {}, weak_count = {}
            "branch strong = {}, weak = {}",
            Rc::strong_count(&branch),
            Rc::weak_count(&branch),
        );

        println!(
            "leaf strong = {}, weak = {}",
            Rc::strong_count(&leaf),
            Rc::weak_count(&leaf),
        );
    }

    println!("leaf parent = {:?}", leaf.parent.borrow().upgrade());
    println!(
        "leaf strong = {}, weak = {}",
        Rc::strong_count(&leaf),
        Rc::weak_count(&leaf),
    );
}

enum List {
    Cons(i32, Box<List>),
    Nil,
}

enum CList {
    Cons(i32, Rc<CList>),
    Nil,
}

#[derive(Debug)]
enum CCList {
    Cons(Rc<RefCell<i32>>, Rc<CCList>),
    Nil,
}

#[derive(Debug)]
enum CCCList {
    Cons(i32, RefCell<Rc<CCCList>>),
    Nil,
}

impl CCCList {
    fn tail(&self) -> Option<&RefCell<Rc<CCCList>>> {
        match *self {
            CCCList::Cons(_, ref item) => Some(item),
            CCCList::Nil => None,
        }
    }
}

struct MyBox<T>(T);

impl<T> MyBox<T> {
    fn new(x: T) -> MyBox<T> {
        MyBox(x)
    }
}

struct MyCBox<T>(T);

impl<T> MyCBox<T> {
    fn new(x: T) -> MyCBox<T> {
        MyCBox(x)
    }
}

// 参照外しをするならDerefを実装する
impl<T> Deref for MyCBox<T> {
    type Target = T;

    fn deref(&self) -> &T {
        &self.0
    }
}

fn hello(name: &str) {
    println!("Hello, {}!", name);
}

struct CustomSmartPointer {
    data: String,
}

impl Drop for CustomSmartPointer {
    // 値がメモリから完全に削除されるときに呼ばれるメソッド
    fn drop(&mut self) {
        // CustomSmartPointerをデータ`{}`とともにドロップするよ
        println!("Dropping CustomSmartPointer with data `{}`!", self.data);
    }
}

#[derive(Debug)]
struct Node {
    value: i32,
    children: RefCell<Vec<Rc<Node>>>,
}

#[derive(Debug)]
struct CNode {
    value: i32,
    // Rcだと循環参照が発生する
    parent: RefCell<Weak<CNode>>,
    children: RefCell<Vec<Rc<CNode>>>,
}
