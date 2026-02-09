use crate::domain::commands::TodoCommand;
use crate::domain::events::TodoEvent;
use serde::{Deserialize, Serialize};
use thiserror::Error;
use uuid::Uuid;

/// Todo 集約ルート
#[derive(Debug, Clone)]
pub struct Todo {
    pub id: Uuid,
    pub title: String,
    pub completed: bool,
}

/// Todo スナップショット（集約の状態を保存）
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TodoSnapshot {
    pub id: Uuid,
    pub title: String,
    pub completed: bool,
    pub version: i64, // イベントのシーケンス番号
}

#[derive(Error, Debug)]
pub enum TodoError {
    #[error("Todo already created")]
    AlreadyCreated,
    #[error("Todo not found")]
    NotFound,
    #[error("Cannot change title of completed todo")]
    CannotChangeTitleWhenCompleted,
    #[error("Todo already completed")]
    AlreadyCompleted,
}

impl Todo {
    /// 空の集約（新規作成前）
    pub fn new_empty(id: Uuid) -> Self {
        Self {
            id,
            title: String::new(),
            completed: false,
        }
    }

    /// スナップショットから集約を復元
    pub fn from_snapshot(snapshot: TodoSnapshot) -> Self {
        Self {
            id: snapshot.id,
            title: snapshot.title,
            completed: snapshot.completed,
        }
    }

    /// 現在の状態をスナップショットに変換
    pub fn to_snapshot(&self, version: i64) -> TodoSnapshot {
        TodoSnapshot {
            id: self.id,
            title: self.title.clone(),
            completed: self.completed,
            version,
        }
    }

    /// イベントを適用して状態を更新
    pub fn apply(&mut self, event: &TodoEvent) {
        match event {
            TodoEvent::TodoCreated { id, title } => {
                self.id = *id;
                self.title = title.clone();
                self.completed = false;
            }
            TodoEvent::TodoTitleChanged { title, .. } => {
                self.title = title.clone();
            }
            TodoEvent::TodoCompleted { .. } => {
                self.completed = true;
            }
        }
    }

    /// コマンドを実行し、生成されたイベントのリストを返す
    pub fn execute(&mut self, command: TodoCommand) -> Result<Vec<TodoEvent>, TodoError> {
        match command {
            TodoCommand::CreateTodo { id, title } => {
                if !self.title.is_empty() || self.id != id {
                    return Err(TodoError::AlreadyCreated);
                }
                Ok(vec![TodoEvent::TodoCreated { id, title }])
            }
            TodoCommand::ChangeTitle { id, title } => {
                if self.id != id {
                    return Err(TodoError::NotFound);
                }
                if self.completed {
                    return Err(TodoError::CannotChangeTitleWhenCompleted);
                }
                Ok(vec![TodoEvent::TodoTitleChanged { id, title }])
            }
            TodoCommand::CompleteTodo { id } => {
                if self.id != id {
                    return Err(TodoError::NotFound);
                }
                if self.completed {
                    return Err(TodoError::AlreadyCompleted);
                }
                Ok(vec![TodoEvent::TodoCompleted { id }])
            }
        }
    }
}

impl Default for Todo {
    fn default() -> Self {
        Self::new_empty(Uuid::nil())
    }
}
