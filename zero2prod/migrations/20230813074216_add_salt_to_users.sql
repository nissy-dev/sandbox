-- Add migration script here
alter table users add column salt text not null;
