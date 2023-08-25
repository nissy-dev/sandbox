use actix_web::{body::to_bytes, HttpResponse};
use reqwest::StatusCode;
use sqlx::{
    postgres::{PgHasArrayType, PgTypeInfo},
    PgPool, Postgres, Transaction,
};
use uuid::Uuid;

use super::IdempotencyKey;

#[derive(Debug, sqlx::Type)]
#[sqlx(type_name = "header_pair")]
struct HeaderPairRecord {
    name: String,
    value: Vec<u8>,
}

impl PgHasArrayType for HeaderPairRecord {
    fn array_type_info() -> sqlx::postgres::PgTypeInfo {
        PgTypeInfo::with_name("_header_pair")
    }
}

pub async fn get_saved_response(
    user_id: Uuid,
    idempotency_key: &IdempotencyKey,
    pool: &PgPool,
) -> Result<Option<HttpResponse>, anyhow::Error> {
    // as で postgres から domain の型 (Vec<HeaderPairRecord>) にキャストする
    let saved_response = sqlx::query!(
        r#"
        select
            response_status_code as "response_status_code!",
            response_headers as "response_headers!: Vec<HeaderPairRecord>",
            response_body as "response_body!"
        from idempotency
        where user_id = $1 and idempotency_key = $2
        "#,
        user_id,
        idempotency_key.as_ref()
    )
    .fetch_optional(pool)
    .await?;
    if let Some(r) = saved_response {
        let status_code = StatusCode::from_u16(r.response_status_code.try_into()?)?;
        let mut response = HttpResponse::build(status_code);
        for HeaderPairRecord { name, value } in r.response_headers {
            response.append_header((name, value));
        }
        Ok(Some(response.body(r.response_body)))
    } else {
        Ok(None)
    }
}

pub async fn save_response(
    user_id: Uuid,
    idempotency_key: &IdempotencyKey,
    http_reponse: HttpResponse,
    mut transaction: Transaction<'static, Postgres>,
) -> Result<HttpResponse, anyhow::Error> {
    let (response_head, body) = http_reponse.into_parts();

    let body = to_bytes(body).await.map_err(|e| anyhow::anyhow!("{}", e))?;
    let status_code = response_head.status().as_u16() as i16;
    let headers = {
        let mut h = Vec::with_capacity(response_head.headers().len());
        for (name, value) in response_head.headers().iter() {
            let name = name.as_str().to_owned();
            let value = value.as_bytes().to_owned();
            h.push(HeaderPairRecord { name, value });
        }
        h
    };

    // postgres に挿入するデータはキャストできない
    // PgHasArrayType のトレイトを HeaderPairRecord に実装して、
    // 明示的に Vec<HeaderPairRecord> が Postgres の配列型に対応していることを伝える
    sqlx::query_unchecked!(
        r#"
        update idempotency
        set
            response_status_code = $3,
            response_headers = $4,
            response_body = $5
        where user_id = $1 and idempotency_key = $2
        "#,
        user_id,
        idempotency_key.as_ref(),
        status_code,
        headers,
        body.as_ref()
    )
    .execute(&mut transaction)
    .await?;
    transaction.commit().await?;

    let http_response = response_head.set_body(body).map_into_boxed_body();
    Ok(http_response)
}

pub enum NextAction {
    StartProcessing(Transaction<'static, Postgres>),
    ReturnSavedResponse(HttpResponse),
}

pub async fn try_processing(
    idempotency_key: &IdempotencyKey,
    user_id: Uuid,
    pool: &PgPool,
) -> Result<NextAction, anyhow::Error> {
    let mut transaction = pool.begin().await?;
    let n_inserted_rows = sqlx::query!(
        r#"
        insert into idempotency (
            user_id,
            idempotency_key,
            created_at
        )
        values ($1, $2, now())
        on conflict do nothing
        "#,
        user_id,
        idempotency_key.as_ref(),
    )
    .execute(&mut transaction)
    .await?
    .rows_affected();

    if n_inserted_rows > 0 {
        Ok(NextAction::StartProcessing(transaction))
    } else {
        let saved_response = get_saved_response(user_id, idempotency_key, pool)
            .await?
            .ok_or_else(|| anyhow::anyhow!("We expected a saved response, we didn't find it"))?;
        Ok(NextAction::ReturnSavedResponse(saved_response))
    }
}
