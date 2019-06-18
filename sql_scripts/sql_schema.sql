drop table [student_mark]
drop table [student]
drop table [subject]

create table student
(
    [id] int not null identity(1,1) primary key,
    [name] nvarchar(50) not null,
    [age] int not null,
    [class] int not null
)

create table [subject]
(
    [id] int not null identity(1,1) primary key,
    [name] nvarchar(50) not null,
    [class] int not null
)

create table [student_mark]
(
    [id] int not null identity(1,1) primary key,
    [student_id] int not null,
    [subject_id] int not null,
    [mark] int not null,
    [year] int not null,
    FOREIGN KEY ([student_id]) REFERENCES [student]([id]),
    FOREIGN KEY ([subject_id]) REFERENCES [subject]([id])
)