use rust_cqrs_es_todo::application::{get_todo, handle_command, list_all_todos, CommandHandlerError};
use rust_cqrs_es_todo::domain::{TodoCommand, TodoError};
use rust_cqrs_es_todo::infrastructure::{PostgresEventStore, run_migrations};
use std::env;
use std::sync::Arc;
use uuid::Uuid;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let database_url = env::var("DATABASE_URL").unwrap_or_else(|_| {
        "postgres://postgres:postgres@localhost:5432/cqrs_todo".to_string()
    });

    let pool = Arc::new(
        sqlx::postgres::PgPoolOptions::new()
            .max_connections(5)
            .connect(&database_url)
            .await?,
    );

    run_migrations(pool.as_ref()).await?;
    let store = PostgresEventStore::new(pool.clone());

    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        print_usage();
        return Ok(());
    }

    match args[1].as_str() {
        "create" => {
            let title = args.get(2).map(|s| s.as_str()).unwrap_or("(no title)");
            let id = Uuid::new_v4();
            let cmd = TodoCommand::CreateTodo {
                id,
                title: title.to_string(),
            };
            handle_command(&store, pool, cmd).await?;
            println!("Created todo: {}", id);
        }
        "complete" => {
            let id_str = args.get(2).ok_or("Usage: complete <id>")?;
            let id = Uuid::parse_str(id_str)?;
            let cmd = TodoCommand::CompleteTodo { id };
            match handle_command(&store, pool, cmd).await {
                Ok(()) => println!("Completed: {}", id),
                Err(CommandHandlerError::Domain(TodoError::NotFound)) => println!("Todo not found: {}", id),
                Err(CommandHandlerError::Domain(TodoError::AlreadyCompleted)) => println!("Todo already completed: {}", id),
                Err(e) => return Err(e.into()),
            }
        }
        "title" => {
            let id_str = args.get(2).ok_or("Usage: title <id> <new_title>")?;
            let title = args.get(3).map(|s| s.as_str()).unwrap_or("(no title)");
            let id = Uuid::parse_str(id_str)?;
            let cmd = TodoCommand::ChangeTitle {
                id,
                title: title.to_string(),
            };
            match handle_command(&store, pool, cmd).await {
                Ok(()) => println!("Updated title: {}", id),
                Err(CommandHandlerError::Domain(TodoError::NotFound)) => println!("Todo not found: {}", id),
                Err(CommandHandlerError::Domain(TodoError::CannotChangeTitleWhenCompleted)) => println!("Cannot change title of completed todo: {}", id),
                Err(e) => return Err(e.into()),
            }
        }
        "list" => {
            let todos = list_all_todos(pool).await?;
            if todos.is_empty() {
                println!("(no todos)");
            } else {
                for t in todos {
                    let done = if t.completed { "x" } else { " " };
                    println!("  [{}] {} - {} ({})", done, t.id, t.title, t.updated_at);
                }
            }
        }
        "get" => {
            let id_str = args.get(2).ok_or("Usage: get <id>")?;
            let id = Uuid::parse_str(id_str)?;
            match get_todo(pool, id).await? {
                Some(t) => {
                    let done = if t.completed { "completed" } else { "open" };
                    println!("{} | {} | {} | {}", t.id, t.title, done, t.updated_at);
                }
                None => println!("Todo not found: {}", id),
            }
        }
        _ => {
            print_usage();
        }
    }

    Ok(())
}

fn print_usage() {
    println!("Usage:");
    println!("  create [title]     Create a new todo");
    println!("  complete <id>      Mark todo as completed");
    println!("  title <id> <title> Change todo title");
    println!("  list                List all todos");
    println!("  get <id>            Get a todo by id");
}
