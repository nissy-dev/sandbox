-- Add migration script here
create table newsletter_issues (
  newsletter_issue_id uuid not null,
  title text not null,
  text_content text not null,
  html_content text not null,
  published_at timestamptz not null,
  primary key(newsletter_issue_id)
);
