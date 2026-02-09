use serde::{Deserialize, Serialize};
use uuid::Uuid;

/// コマンド（Todo 集約用）
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "command_type", rename_all = "snake_case")]
pub enum TodoCommand {
    CreateTodo { id: Uuid, title: String },
    ChangeTitle { id: Uuid, title: String },
    CompleteTodo { id: Uuid },
}

impl TodoCommand {
    pub fn aggregate_id(&self) -> Uuid {
        match self {
            TodoCommand::CreateTodo { id, .. }
            | TodoCommand::ChangeTitle { id, .. }
            | TodoCommand::CompleteTodo { id } => *id,
        }
    }
}
