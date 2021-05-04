pub struct Post {
  // 構造体は参照のフィールドが持てないからOptionが必要
  // 値を参照したいときは、take()でNoneが変えるようにする
  state: Option<Box<State>>,
  content: String,
}

impl Post {
  pub fn new() -> Post {
    Post {
      state: Some(Box::new(Draft {})),
      content: String::new(),
    }
  }

  pub fn add_text(&mut self, text: &str) {
    self.content.push_str(text);
  }

  pub fn content(&self) -> &str {
    self.state.as_ref().unwrap().content(&self)
  }

  pub fn request_review(&mut self) {
    if let Some(s) = self.state.take() {
      self.state = Some(s.request_review())
    }
  }

  pub fn approve(&mut self) {
    if let Some(s) = self.state.take() {
      self.state = Some(s.approve())
    }
  }

  pub fn reject(&mut self) {
    if let Some(s) = self.state.take() {
      self.state = Some(s.reject())
    }
  }
}

trait State {
  fn request_review(self: Box<Self>) -> Box<State>;
  fn approve(self: Box<Self>) -> Box<State>;
  fn reject(self: Box<Self>) -> Box<State>;
  fn content<'a>(&self, post: &'a Post) -> &'a str {
    ""
  }
}

struct Draft {}

impl State for Draft {
  fn request_review(self: Box<Self>) -> Box<State> {
    Box::new(PendingReview {})
  }
  fn approve(self: Box<Self>) -> Box<State> {
    self
  }
  fn reject(self: Box<Self>) -> Box<State> {
    self
  }
}

struct PendingReview {}

impl State for PendingReview {
  fn request_review(self: Box<Self>) -> Box<State> {
    self
  }
  fn approve(self: Box<Self>) -> Box<State> {
    Box::new(Published {})
  }

  fn reject(self: Box<Self>) -> Box<State> {
    Box::new(Draft {})
  }
}

struct Published {}

impl State for Published {
  fn request_review(self: Box<Self>) -> Box<State> {
    self
  }

  fn approve(self: Box<Self>) -> Box<State> {
    self
  }

  fn reject(self: Box<Self>) -> Box<State> {
    Box::new(Draft {})
  }

  fn content<'a>(&self, post: &'a Post) -> &'a str {
    &post.content
  }
}

pub struct NPost {
  content: String,
}

pub struct NDraftPost {
  content: String,
}

pub struct NPendingReviewPost {
  content: String,
}

impl NPost {
  pub fn new() -> NDraftPost {
    NDraftPost {
      content: String::new(),
    }
  }

  pub fn content(&self) -> &str {
    &self.content
  }
}

impl NDraftPost {
  pub fn add_text(&mut self, text: &str) {
    self.content.push_str(text);
  }
  pub fn request_review(self) -> NPendingReviewPost {
    NPendingReviewPost {
      content: self.content,
    }
  }
}

impl NPendingReviewPost {
  pub fn approve(self) -> NPost {
    NPost {
      content: self.content,
    }
  }
}
