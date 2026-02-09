use serde::{Deserialize, Serialize};
use uuid::Uuid;

/// ドメインイベント（Todo 集約用）
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(tag = "event_type", rename_all = "snake_case")]
pub enum TodoEvent {
    TodoCreated { id: Uuid, title: String },
    TodoTitleChanged { id: Uuid, title: String },
    TodoCompleted { id: Uuid },
}

impl TodoEvent {
    pub fn aggregate_id(&self) -> Uuid {
        match self {
            TodoEvent::TodoCreated { id, .. }
            | TodoEvent::TodoTitleChanged { id, .. }
            | TodoEvent::TodoCompleted { id } => *id,
        }
    }

    pub fn type_name(&self) -> &'static str {
        match self {
            TodoEvent::TodoCreated { .. } => "todo_created",
            TodoEvent::TodoTitleChanged { .. } => "todo_title_changed",
            TodoEvent::TodoCompleted { .. } => "todo_completed",
        }
    }
}
