UPDATE users
SET config_id = '9bb58f3e-627b-408f-a11b-0efdbb5abd37'
WHERE id = 'd0a21dbb-81c1-4002-8c59-c1c0cb3a9b07';

INSERT INTO users
values (
    'd0a21dbb-81c1-4002-8c59-c1c0cb3a9b07',
    'evanc',
    '9bb58f3e-627b-408f-a11b-0efdbb5abd37'
  ) on conflict do
update
set config_id = '9bb58f3e-627b-408f-a11b-0efdbb5abd37'
where id = 'd0a21dbb-81c1-4002-8c59-c1c0cb3a9b07';

select *
from users;