-- Add migration script here
insert into users (user_id, username, password_hash)
values (
  'ddf8994f-d522-4659-8d02-c1d479057be6',
  'admin',
  '$argon2id$v=19$m=15000,t=2,p=1$H8YcJR9ADCzYaTSJXrxjRg$NUxr88pioIzOz9yn/7fsTY1SVX8+kcw1doI/AM1DbD4'
)
