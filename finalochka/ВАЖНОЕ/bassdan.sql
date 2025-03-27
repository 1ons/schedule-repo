drop table schedule2301;
drop table schedule2302;
drop table schedule2303;
drop table schedule2304;
drop table schedule2305;
drop table schedule2306;
drop table schedule2307;
drop table schedule2308;
drop table schedule2309;
drop table schedule2310;
select * from schedule where group_number = '2306' and day ilike 'пятница'
select * from users
SELECT DISTINCT day FROM schedule;
UPDATE schedule 
SET day = LOWER(day);


drop table users;

drop table subscribers;

create table users ( 
user_id serial primary key, 
username text, 
password varchar(255), 
email varchar(255), 
grup varchar(255)check (grup in ('2301', '2302', '2303', '2304', '2305', '2306', '2307', '2308', '2309', '2310')), 
role VARCHAR(20) not null check (role in ('admin', 'customer')),
created_at timestamp default current_timestamp,
avatar varchar(255)
); 

select * from users

drop table subjects cascade

create table subjects(
subject_id int primary key,
subject_name text);

insert into subjects(subject_id,subject_name)
values 
(1,'database'),
(2,'python'),
(3,'chemistry'),
(4,'history'),
(5,'information communication technology'),
(6,'physical education'),
(7,'english'),
(8,'economy');

drop table teachers cascade
create table teachers(
teacher_id int primary key,
teacher_name text);

insert into teachers(teacher_id, teacher_name)
values
(1,'Хабиев Жангирхан Кайратович'),
(2,'Ауезханов Дархан Азаматович'),
(3,'Дина Рукалиевна'),
(4,'Мадияр Шакиев'),
(5,'Жұмағамбетова Әсел Кұсманқызы'),
(6,'Әшімбекова Арайлым Миллионбекқызы'),
(7,'Кулжанбекова Сара Токтаровна'),
(8,'Акубаева Багдат Аскановна');
drop table teacher_subject cascade
create table teacher_subject(
teacher_id int,
subject_id int,
primary key (teacher_id, subject_id),
foreign key (teacher_id) references teachers(teacher_id),
foreign key (subject_id) references subjects(subject_id));

insert into teacher_subject(teacher_id, subject_id)
values
(1,1),
(2,2),
(3,3),
(4,4),
(5,5), 
(6,6),
(7,7),
(8,8);


update users 
set role = 'admin' 
where email = 'amirokamir@gmail.com';

-------------------------------------------------------------------------------------------------
create table schedule2301 ( 
id serial primary key, 
subject_id varchar(255),
teacher_id int, 
start_time time, 
end_time time, 
day text not null check (day in ('monday','tuesday','wednesday','thursday','friday')) ); 

create table schedule2302 ( 
id serial primary key, 
subject_id varchar(255),
teacher_id int, 
start_time time, 
end_time time, 
day text not null check (day in ('monday','tuesday','wednesday','thursday','friday')) );

create table schedule2303 ( 
id serial primary key, 
subject_id varchar(255),
teacher_id int, 
start_time time, 
end_time time, 
day text not null check (day in ('monday','tuesday','wednesday','thursday','friday')) );

create table schedule2304 ( 
id serial primary key, 
subject_id varchar(255),
teacher_id int,
start_time time, 
end_time time,
day text not null check (day in ('monday','tuesday','wednesday','thursday','friday')) );

create table schedule2305 ( 
id serial primary key, 
subject_id varchar(255),
teacher_id int,
start_time time, 
end_time time, 
day text not null check (day in ('monday','tuesday','wednesday','thursday','friday')) ); 

create table schedule2306 ( 
id serial primary key, 
subject_id varchar(255),
teacher_id int,
start_time time, 
end_time time, 
day text not null check (day in ('monday','tuesday','wednesday','thursday','friday')) ); 

create table schedule2307 ( 
id serial primary key, 
subject_id varchar(255),
teacher_id int, 
start_time time, 
end_time time, 
day text not null check (day in ('monday','tuesday','wednesday','thursday','friday')) ); 
 
create table schedule2308 ( 
id serial primary key, 
subject_id varchar(255),
teacher_id int, 
start_time time, 
end_time time,
day text not null check (day in ('monday','tuesday','wednesday','thursday','friday')) );

create table schedule2309 ( 
id serial primary key, 
subject_id varchar(255),
teacher_id int, 
start_time time, 
end_time time,
day text not null check (day in ('monday','tuesday','wednesday','thursday','friday')) );

create table schedule2310 ( 
id serial primary key, 
subject_id varchar(255),
teacher_id int, 
start_time time, 
end_time time,
day text not null check (day in ('monday','tuesday','wednesday','thursday','friday')) ); 

---------------------------------------------------------------------------------------------------

insert into schedule2301(subject_id, teacher_id, start_time, end_time, day) 
values 
(1, 1, '08:00', '09:30', 'monday'), 
(3, 3, '09:50', '11:20', 'monday'), 
(5, 5, '11:30', '13:00', 'monday'), 
(6, 6, '08:00', '09:30', 'tuesday'), 
(8, 8, '09:50', '11:20', 'tuesday'), 
(2, 2, '11:30', '13:00', 'tuesday'), 
(4, 4, '08:00', '09:30', 'wednesday'), 
(2, 2, '09:50', '11:20', 'wednesday'), 
(1, 1, '11:30', '13:00', 'wednesday'), 
(1, 1, '08:00', '09:30', 'thursday'), 
(5, 5, '09:50', '11:20', 'thursday'), 
(2, 2, '11:30', '13:00', 'thursday'), 
(7, 7, '08:00', '09:30', 'friday'), 
(2, 2, '09:50', '11:20', 'friday'), 
(8, 8, '11:30', '13:00', 'friday');

insert into schedule2302(subject_id, teacher_id, start_time, end_time, day) 
values 
(8, 8, '08:00', '09:30', 'monday'), 
(1, 1, '09:50', '11:20', 'monday'), 
(3, 3, '11:30', '13:00', 'monday'), 
(1, 1, '08:00', '09:30', 'tuesday'), 
(2, 2, '09:50', '11:20', 'tuesday'), 
(8, 8, '11:30', '13:00', 'tuesday'), 
(7, 7, '08:00', '09:30', 'wednesday'), 
(1, 1, '09:50', '11:20', 'wednesday'), 
(2, 2, '11:30', '13:00', 'wednesday'), 
(1, 1, '08:00', '09:30', 'thursday'), 
(2, 2, '09:50', '11:20', 'thursday'), 
(5, 5, '11:30', '13:00', 'thursday'), 
(4, 4, '08:00', '09:30', 'friday'), 
(5, 5, '09:50', '11:20', 'friday'), 
(2, 2, '11:30', '13:00', 'friday');


insert into schedule2303(subject_id, teacher_id, start_time, end_time, day) 
values 
(4, 4, '08:00', '09:30', 'monday'), 
(1, 1, '09:50', '11:20', 'monday'), 
(2, 2, '11:30', '13:00', 'monday'), 
(8, 8, '08:00', '09:30', 'tuesday'), 
(6, 6, '09:50', '11:20', 'tuesday'), 
(1, 1, '11:30', '13:00', 'tuesday'), 
(3, 3, '08:00', '09:30', 'wednesday'), 
(5, 5, '09:50', '11:20', 'wednesday'), 
(7, 7, '11:30', '13:00', 'wednesday'), 
(2, 2, '08:00', '09:30', 'thursday'), 
(4, 4, '09:50', '11:20', 'thursday'), 
(6, 6, '11:30', '13:00', 'thursday'), 
(5, 5, '08:00', '09:30', 'friday'), 
(3, 3, '09:50', '11:20', 'friday'), 
(8, 8, '11:30', '13:00', 'friday');


insert into schedule2304(subject_id, teacher_id, start_time, end_time, day) 
values 
(6, 6, '08:00', '09:30', 'monday'), 
(7, 7, '09:50', '11:20', 'monday'), 
(3, 3, '11:30', '13:00', 'monday'), 
(1, 1, '08:00', '09:30', 'tuesday'), 
(4, 4, '09:50', '11:20', 'tuesday'), 
(5, 5, '11:30', '13:00', 'tuesday'), 
(2, 2, '08:00', '09:30', 'wednesday'), 
(6, 6, '09:50', '11:20', 'wednesday'), 
(8, 8, '11:30', '13:00', 'wednesday'), 
(5, 5, '08:00', '09:30', 'thursday'), 
(7, 7, '09:50', '11:20', 'thursday'), 
(3, 3, '11:30', '13:00', 'thursday'), 
(4, 4, '08:00', '09:30', 'friday'), 
(1, 1, '09:50', '11:20', 'friday'), 
(8, 8, '11:30', '13:00', 'friday');


insert into schedule2305(subject_id, teacher_id, start_time, end_time, day) 
values 
(5, 5, '08:00', '09:30', 'monday'), 
(4, 4, '09:50', '11:20', 'monday'), 
(2, 2, '11:30', '13:00', 'monday'), 
(6, 6, '08:00', '09:30', 'tuesday'), 
(3, 3, '09:50', '11:20', 'tuesday'), 
(8, 8, '11:30', '13:00', 'tuesday'), 
(7, 7, '08:00', '09:30', 'wednesday'), 
(1, 1, '09:50', '11:20', 'wednesday'), 
(2, 2, '11:30', '13:00', 'wednesday'), 
(5, 5, '08:00', '09:30', 'thursday'), 
(4, 4, '09:50', '11:20', 'thursday'), 
(6, 6, '11:30', '13:00', 'thursday'), 
(3, 3, '08:00', '09:30', 'friday'), 
(1, 1, '09:50', '11:20', 'friday'), 
(8, 8, '11:30', '13:00', 'friday');


insert into schedule2306(subject_id, teacher_id, start_time, end_time, day) 
values 
(8, 8, '08:00', '09:30', 'monday'), 
(2, 2, '09:50', '11:20', 'monday'), 
(5, 5, '11:30', '13:00', 'monday'), 
(3, 3, '08:00', '09:30', 'tuesday'), 
(7, 7, '09:50', '11:20', 'tuesday'), 
(1, 1, '11:30', '13:00', 'tuesday'), 
(4, 4, '08:00', '09:30', 'wednesday'), 
(6, 6, '09:50', '11:20', 'wednesday'), 
(8, 8, '11:30', '13:00', 'wednesday'), 
(5, 5, '08:00', '09:30', 'thursday'), 
(2, 2, '09:50', '11:20', 'thursday'), 
(7, 7, '11:30', '13:00', 'thursday'), 
(3, 3, '08:00', '09:30', 'friday'), 
(1, 1, '09:50', '11:20', 'friday'), 
(6, 6, '11:30', '13:00', 'friday');


insert into schedule2307(subject_id, teacher_id, start_time, end_time, day) 
values 
(2, 2, '08:00', '09:30', 'monday'), 
(4, 4, '09:50', '11:20', 'monday'), 
(6, 6, '11:30', '13:00', 'monday'), 
(7, 7, '08:00', '09:30', 'tuesday'), 
(3, 3, '09:50', '11:20', 'tuesday'), 
(8, 8, '11:30', '13:00', 'tuesday'), 
(5, 5, '08:00', '09:30', 'wednesday'), 
(1, 1, '09:50', '11:20', 'wednesday'), 
(4, 4, '11:30', '13:00', 'wednesday'), 
(2, 2, '08:00', '09:30', 'thursday'), 
(6, 6, '09:50', '11:20', 'thursday'), 
(8, 8, '11:30', '13:00', 'thursday'), 
(7, 7, '08:00', '09:30', 'friday'), 
(3, 3, '09:50', '11:20', 'friday'), 
(5, 5, '11:30', '13:00', 'friday');


insert into schedule2308(subject_id, teacher_id, start_time, end_time, day) 
values 
(6, 6, '08:00', '09:30', 'monday'), 
(3, 3, '09:50', '11:20', 'monday'), 
(7, 7, '11:30', '13:00', 'monday'), 
(8, 8, '08:00', '09:30', 'tuesday'), 
(1, 1, '09:50', '11:20', 'tuesday'), 
(4, 4, '11:30', '13:00', 'tuesday'), 
(5, 5, '08:00', '09:30', 'wednesday'), 
(2, 2, '09:50', '11:20', 'wednesday'), 
(6, 6, '11:30', '13:00', 'wednesday'), 
(3, 3, '08:00', '09:30', 'thursday'), 
(8, 8, '09:50', '11:20', 'thursday'), 
(7, 7, '11:30', '13:00', 'thursday'), 
(4, 4, '08:00', '09:30', 'friday'), 
(1, 1, '09:50', '11:20', 'friday'), 
(2, 2, '11:30', '13:00', 'friday');


insert into schedule2309(subject_id, teacher_id, start_time, end_time, day) 
values 
(7, 7, '08:00', '09:30', 'monday'), 
(8, 8, '09:50', '11:20', 'monday'), 
(1, 1, '11:30', '13:00', 'monday'), 
(5, 5, '08:00', '09:30', 'tuesday'), 
(3, 3, '09:50', '11:20', 'tuesday'), 
(2, 2, '11:30', '13:00', 'tuesday'), 
(6, 6, '08:00', '09:30', 'wednesday'), 
(4, 4, '09:50', '11:20', 'wednesday'), 
(8, 8, '11:30', '13:00', 'wednesday'), 
(2, 2, '08:00', '09:30', 'thursday'), 
(7, 7, '09:50', '11:20', 'thursday'), 
(5, 5, '11:30', '13:00', 'thursday'), 
(3, 3, '08:00', '09:30', 'friday'), 
(1, 1, '09:50', '11:20', 'friday'), 
(4, 4, '11:30', '13:00', 'friday');


insert into schedule2310(subject_id, teacher_id, start_time, end_time, day) 
values 
(3, 3, '08:00', '09:30', 'monday'), 
(6, 6, '09:50', '11:20', 'monday'), 
(2, 2, '11:30', '13:00', 'monday'), 
(8, 8, '08:00', '09:30', 'tuesday'), 
(5, 5, '09:50', '11:20', 'tuesday'), 
(7, 7, '11:30', '13:00', 'tuesday'), 
(4, 4, '08:00', '09:30', 'wednesday'), 
(1, 1, '09:50', '11:20', 'wednesday'), 
(3, 3, '11:30', '13:00', 'wednesday'), 
(2, 2, '08:00', '09:30', 'thursday'), 
(6, 6, '09:50', '11:20', 'thursday'), 
(8, 8, '11:30', '13:00', 'thursday'), 
(5, 5, '08:00', '09:30', 'friday'), 
(7, 7, '09:50', '11:20', 'friday'), 
(1, 1, '11:30', '13:00', 'friday');

------------------------------------------------------------------


CREATE TABLE IF NOT EXISTS schedule (
    id SERIAL PRIMARY KEY,
    group_number VARCHAR(10) NOT NULL,
    day VARCHAR(20) NOT NULL,
	subject varchar(200),
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    check_day varchar(20)check (day IN ('Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота')),
    CONSTRAINT check_time CHECK (start_time < end_time)
);

create table teachers (
id serial primary key,
t
)

select * from schedule
select * from schedule_ARCHIVE
SELECT id, group_number, day, subject, start_time, end_time, created_at
FROM schedule_archive
ORDER BY created_at DESC;
CREATE TABLE IF NOT EXISTS schedule_archive (
    id SERIAL PRIMARY KEY,
    group_number VARCHAR(10) NOT NULL,
    day VARCHAR(20) NOT NULL,
    subject VARCHAR(100) NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    check_day varchar(20)check (day IN ('Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота')),
    CONSTRAINT check_time CHECK (start_time < end_time)
);
select * from schedule where group_number ilike '2301'
drop table if exists schedule
drop table if exists schedule_archive
CREATE INDEX idx_schedule_group_day ON schedule(group_number, day);
TRUNCATE TABLE schedule RESTART IDENTITY

-- Функция для массовой вставки расписания группы
CREATE OR REPLACE FUNCTION insert_group_schedule(group_num VARCHAR(4), time_shift INTERVAL)
RETURNS VOID AS $$
BEGIN
    INSERT INTO schedule(group_number, subject, start_time, end_time, day)
    VALUES
    (group_num, 'database', '8:00'::time + time_shift, '9:30'::time + time_shift, 'monday'),
    (group_num, 'chemistry', '9:50'::time + time_shift, '11:20'::time + time_shift, 'monday'),
    (group_num, 'information communication technology', '11:30'::time + time_shift, '13:00'::time + time_shift, 'monday'),
    -- ... (остальные предметы)
    (group_num, 'english', '8:00'::time + time_shift, '9:30'::time + time_shift, 'friday'),
    (group_num, 'python', '9:50'::time + time_shift, '11:20'::time + time_shift, 'friday'),
    (group_num, 'economy', '11:30'::time + time_shift, '13:00'::time + time_shift, 'friday');
END;
$$ LANGUAGE plpgsql;
-- Удалим все старые записи, чтобы заполнить таблицу заново
TRUNCATE TABLE schedule RESTART IDENTITY;
CREATE TABLE news (
    id serial PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    image VARCHAR(255),
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);
drop table news
select * from group_subscribers
drop table group_subscribers
create table  group_subscribers (
id serial primary key,
group_number varchar(10) not null,
chat_id varchar(50) not null,
subscribed_at timestamp default current_timestamp,
unique (group_number, chat_id)
);
-- Вставка данных для группы 2301
INSERT INTO schedule (group_number, day, subject, start_time, end_time)
VALUES
    ('2301', 'Понедельник', 'Database', '08:00', '09:30'),
    ('2301', 'Понедельник', 'Chemistry', '09:50', '11:20'),
    ('2301', 'Понедельник', 'ICT', '11:30', '13:00'),
    ('2301', 'Вторник', 'Physical Education', '08:00', '09:30'),
    ('2301', 'Вторник', 'Social Education', '09:50', '11:20'),
    ('2301', 'Вторник', 'Programming', '11:30', '13:00'),
    ('2301', 'Среда', 'History', '08:00', '09:30'),
    ('2301', 'Среда', 'Python', '09:50', '11:20'),
    ('2301', 'Среда', 'Database', '11:30', '13:00'),
    ('2301', 'Четверг', 'Database', '08:00', '09:30'),
    ('2301', 'Четверг', 'ICT', '09:50', '11:20'),
    ('2301', 'Четверг', 'Python', '11:30', '13:00'),
    ('2301', 'Пятница', 'English', '08:00', '09:30'),
    ('2301', 'Пятница', 'Python', '09:50', '11:20'),
    ('2301', 'Пятница', 'Economy', '11:30', '13:00');

-- Вставка данных для других групп (2302 до 2310)
INSERT INTO schedule (group_number, day, subject, start_time, end_time)
VALUES
    ('2302', 'Понедельник', 'Database', '08:00', '09:30'),
    ('2302', 'Понедельник', 'Chemistry', '09:50', '11:20'),
    ('2302', 'Понедельник', 'ICT', '11:30', '13:00'),
    ('2302', 'Вторник', 'Physical Education', '08:00', '09:30'),
    ('2302', 'Вторник', 'Social Education', '09:50', '11:20'),
    ('2302', 'Вторник', 'Programming', '11:30', '13:00'),
    ('2302', 'Среда', 'History', '08:00', '09:30'),
    ('2302', 'Среда', 'Python', '09:50', '11:20'),
    ('2302', 'Среда', 'Database', '11:30', '13:00'),
    ('2302', 'Четверг', 'Database', '08:00', '09:30'),
    ('2302', 'Четверг', 'ICT', '09:50', '11:20'),
    ('2302', 'Четверг', 'Python', '11:30', '13:00'),
    ('2302', 'Пятница', 'English', '08:00', '09:30'),
    ('2302', 'Пятница', 'Python', '09:50', '11:20'),
    ('2302', 'Пятница', 'Economy', '11:30', '13:00');

-- Продолжаем для групп 2303 до 2310
-- Повторяем аналогичные записи для каждой группы, меняя только номер группы

-- Пример для группы 2303
INSERT INTO schedule (group_number, day, subject, start_time, end_time)
VALUES
    ('2303', 'Понедельник', 'Database', '08:00', '09:30'),
    ('2303', 'Понедельник', 'Chemistry', '09:50', '11:20'),
    ('2303', 'Понедельник', 'ICT', '11:30', '13:00'),
    ('2303', 'Вторник', 'Physical Education', '08:00', '09:30'),
    ('2303', 'Вторник', 'Social Education', '09:50', '11:20'),
    ('2303', 'Вторник', 'Programming', '11:30', '13:00'),
    ('2303', 'Среда', 'History', '08:00', '09:30'),
    ('2303', 'Среда', 'Python', '09:50', '11:20'),
    ('2303', 'Среда', 'Database', '11:30', '13:00'),
    ('2303', 'Четверг', 'Database', '08:00', '09:30'),
    ('2303', 'Четверг', 'ICT', '09:50', '11:20'),
    ('2303', 'Четверг', 'Python', '11:30', '13:00'),
    ('2303', 'Пятница', 'English', '08:00', '09:30'),
    ('2303', 'Пятница', 'Python', '09:50', '11:20'),
    ('2303', 'Пятница', 'Economy', '11:30', '13:00');
INSERT INTO schedule (group_number, day, subject, start_time, end_time)
VALUES
    ('2306', 'Понедельник', 'Database', '08:00', '09:30'),
    ('2306', 'Понедельник', 'Chemistry', '09:50', '11:20'),
    ('2306', 'Понедельник', 'ICT', '11:30', '13:00'),
    ('2306', 'Вторник', 'Physical Education', '08:00', '09:30'),
    ('2306', 'Вторник', 'Social Education', '09:50', '11:20'),
    ('2306', 'Вторник', 'Programming', '11:30', '13:00'),
    ('2306', 'Среда', 'History', '08:00', '09:30'),
    ('2306', 'Среда', 'Python', '09:50', '11:20'),
    ('2306', 'Среда', 'Database', '11:30', '13:00'),
    ('2306', 'Четверг', 'Database', '08:00', '09:30'),
    ('2306', 'Четверг', 'ICT', '09:50', '11:20'),
    ('2306', 'Четверг', 'Python', '11:30', '13:00'),
    ('2306', 'Пятница', 'English', '08:00', '09:30'),
    ('2306', 'Пятница', 'Python', '09:50', '11:20'),
    ('2306', 'Пятница', 'Economy', '11:30', '13:00');

-- Повторить аналогичные вставки для групп 2304, 2305, ..., 2310


INSERT INTO schedule (group_number, day, subject, start_time, end_time)
VALUES
('2301', 'Понедельник', 'Database', '08:00', '09:30'),
('2301', 'Понедельник', 'Chemistry', '09:50', '11:20'),
('2301', 'Понедельник', 'ICT', '11:30', '13:00'),
('2301', 'Вторник', 'Mathematics', '08:00', '09:30'),
('2301', 'Вторник', 'Physics', '09:50', '11:20'),
('2301', 'Среда', 'English', '08:00', '09:30'),
('2302', 'Понедельник', 'Database', '08:00', '09:30'),
('2302', 'Понедельник', 'Chemistry', '09:50', '11:20'),
('2302', 'Понедельник', 'ICT', '11:30', '13:00'),
('2302', 'Вторник', 'Mathematics', '08:00', '09:30'),
('2302', 'Вторник', 'Physics', '09:50', '11:20'),
('2302', 'Среда', 'English', '08:00', '09:30'),
('2303', 'Четверг', 'Database', '08:00', '09:30'),
('2303', 'Четверг', 'Chemistry', '09:50', '11:20'),
('2303', 'Четверг', 'ICT', '11:30', '13:00'),
('2303', 'Пятница', 'Mathematics', '08:00', '09:30'),
('2303', 'Пятница', 'Physics', '09:50', '11:20'),
('2303', 'Пятница', 'English', '11:30', '13:00');

INSERT INTO schedule (group_number, subject_id, teacher_id, start_time, end_time, day)
VALUES
('2301', 'database', 1, '08:00', '09:30', 'monday'),
('2301', 'chemistry', 2, '09:50', '11:20', 'monday'),
('2301', 'english', 3, '11:30', '13:00', 'monday'),
-- ... добавляйте другие предметы для этой группы
('2302', 'python', 1, '08:00', '09:30', 'tuesday'),
('2302', 'economy', 2, '09:50', '11:20', 'tuesday'),
-- и так далее для других групп
('2310', 'mathematics', 4, '08:00', '09:30', 'friday');


-- Вставка расписания для всех групп
DO $$
BEGIN
    -- Утренние группы (2301-2305)
    PERFORM insert_group_schedule('2301', '0'::interval);
    PERFORM insert_group_schedule('2302', '0'::interval);
    PERFORM insert_group_schedule('2303', '0'::interval);
    PERFORM insert_group_schedule('2304', '0'::interval);
    PERFORM insert_group_schedule('2305', '0'::interval);
    -- Дневные группы (2306-2310)
    PERFORM insert_group_schedule('2306', '5 hours 30 minutes'::interval);
    PERFORM insert_group_schedule('2307', '5 hours 30 minutes'::interval);
    PERFORM insert_group_schedule('2308', '5 hours 30 minutes'::interval);
    PERFORM insert_group_schedule('2309', '5 hours 30 minutes'::interval);
    PERFORM insert_group_schedule('2310', '5 hours 30 minutes'::interval);
END $$;
create or replace function notify_change() 
returns trigger  
language plpgsql 
as $$ 
begin 
perform pg_notify(
'schedule_update',
json_build_object('operation', TG_OP, 
'day', NEW.day, 
'subject', NEW.subject, 
'start_time', NEW.start_time, 
'end_time', NEW.end_time, 
'group_number', NEW.group_number)::text
); 
return new; 
end; 
$$;

select * from subscribers

create table subscribers (
user_id serial primary key,
email text,
group_number int
);

create or replace function insert_group_schedule(group_num VARCHAR(4), time_shift INTERVAL)
returns void 
language plpgsql
as $$
begin
insert into schedule(group_number, subject, start_time, end_time, day)
values
(group_num, 'database', '8:00'::time + time_shift, '9:30'::time + time_shift, 'monday'),
(group_num, 'chemistry', '9:50'::time + time_shift, '11:20'::time + time_shift, 'monday'),
(group_num, 'information communication technology', '11:30'::time + time_shift, '13:00'::time + time_shift, 'monday'),
(group_num, 'english', '8:00'::time + time_shift, '9:30'::time + time_shift, 'friday'),
(group_num, 'python', '9:50'::time + time_shift, '11:20'::time + time_shift, 'friday'),
(group_num, 'economy', '11:30'::time + time_shift, '13:00'::time + time_shift, 'friday');
end;
$$;

do $$
begin
perform insert_group_schedule('2301', '0'::interval);
perform insert_group_schedule('2302', '0'::interval);
perform insert_group_schedule('2303', '0'::interval);
perform insert_group_schedule('2304', '0'::interval);
perform insert_group_schedule('2305', '0'::interval);
perform insert_group_schedule('2306', '5 hours 30 minutes'::interval);
perform insert_group_schedule('2307', '5 hours 30 minutes'::interval);
perform insert_group_schedule('2308', '5 hours 30 minutes'::interval);
perform insert_group_schedule('2309', '5 hours 30 minutes'::interval);
perform insert_group_schedule('2310', '5 hours 30 minutes'::interval);
END $$;

set update day from schedule
where group_number = '2301' 
order by 
case 
when day = 'monday' then 1 
when day = 'tuesday' then 2 
when day = 'wednesday' then 3 
when day = 'thursday' then 4 
when day = 'friday' then 5 
end,
start_time;

create or replace function notify_schedule_change()
returns trigger 
language plpgsql
as $$
declare
change_type text;
schedule_info text;
begin
if (tg_op = 'insert') then
change_type = 'insert';
schedule_info = format(
'новая запись в расписании: группа %s, предмет %s, день %s, время %s-%s', 
new.group_number, 
new.subject, 
new.day, 
new.start_time, 
new.end_time
);
elsif (tg_op = 'update') then
change_type = 'update';
schedule_info = format(
'обновление расписания: группа %s, предмет %s, день %s, время %s-%s', 
new.group_number, 
new.subject, 
new.day, 
new.start_time, 
new.end_time
);
elsif (tg_op = 'delete') then
change_type = 'delete';
schedule_info = format(
'удаление из расписания: группа %s, предмет %s, день %s, время %s-%s', 
old.group_number, 
old.subject, 
old.day, 
old.start_time, 
old.end_time
);
end if;
perform pg_notify('schedule_changes', schedule_info);
return new;
end;
$$;

--триггер связанный с функцией уведомления и отслеживающий изменений
create trigger schedule_change_trigger
after insert or update or delete on schedule
for each row execute function notify_schedule_change();