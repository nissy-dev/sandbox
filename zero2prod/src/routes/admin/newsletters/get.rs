use std::fmt::Write;

use actix_web::{http::header::ContentType, HttpResponse};
use actix_web_flash_messages::IncomingFlashMessages;
use uuid::Uuid;

pub async fn publish_newsletters_form(
    flash_messages: IncomingFlashMessages,
) -> Result<HttpResponse, actix_web::Error> {
    let mut msg_html = String::new();
    for m in flash_messages.iter() {
        writeln!(msg_html, "<p><i>{}</i></p>", m.content()).unwrap();
    }

    let idempotency_key = Uuid::new_v4();

    Ok(HttpResponse::Ok()
        .content_type(ContentType::html())
        .body(format!(
            r#"<!DOCTYPE html>
<html lang="en">
<head>
  <meta http-equiv="content-type" content="text/html; charset=utf-8">
  <title>Publish newsletters</title>
</head>
<body>
  {msg_html}
  <form action="/admin/newsletter" method="post">
    <label>Text content
      <input type="text" placeholder="Enter text content" name="text_content">
    </label>
    <br>
    <label>Html content
      <input type="text" placeholder="Enter html content" name="html_content">
    </label>
    <br>
    <input hidden type="text" name="idempotency_key" value="{idempotency_key}">
    <button type="submit">Publish newsletters</button>
  </form>
</body>
</html>"#
        )))
}
