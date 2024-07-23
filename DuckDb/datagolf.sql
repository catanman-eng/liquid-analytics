CREATE TABLE tbl (i INT PRIMARY KEY, j INT UNIQUE, k INT);

INSERT INTO tbl VALUES (1, 20, 300);

SELECT * FROM tbl;

INSERT INTO tbl VALUES (1, 40, 700) ON CONFLICT (i) DO UPDATE SET k = 3 * EXCLUDED.k WHERE k > 100;


insert into users values ('1', 'test', null);

select * from users;

insert into users values ('1', 'test', null) on conflict (id) do update set config_id = 'test2';