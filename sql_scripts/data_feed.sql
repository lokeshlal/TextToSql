-- delete any existing data
delete from [student_mark]
delete from [student]
delete from [subject]
-- reseed the identity column 
DBCC CHECKIDENT ('student', RESEED, 1)  
DBCC CHECKIDENT ('subject', RESEED, 1)  
DBCC CHECKIDENT ('student_mark', RESEED, 1)  
-- insert student
insert into [student] ([name], [age], [class]) values ('Lokesh Lal', 17, 12)
insert into [student] ([name], [age], [class]) values ('Munish Sharma', 18, 12)
insert into [student] ([name], [age], [class]) values ('Sumit Chharia', 18, 12)
insert into [student] ([name], [age], [class]) values ('Manoj Gupta', 17, 12)
insert into [student] ([name], [age], [class]) values ('Vishal Gupta', 19, 12)
insert into [student] ([name], [age], [class]) values ('Ambika Shukla', 20, 12)
insert into [student] ([name], [age], [class]) values ('Manoj Garg', 18, 12)
insert into [student] ([name], [age], [class]) values ('Gagandeep sampat', 19, 12)
-- insert subject
insert into [subject] ([name], [class]) values ('English', 12)
insert into [subject] ([name], [class]) values ('Maths', 12)
insert into [subject] ([name], [class]) values ('Physics', 12)
insert into [subject] ([name], [class]) values ('Chemistry', 12)
insert into [subject] ([name], [class]) values ('Computer', 12)
insert into [subject] ([name], [class]) values ('Biology', 12)
-- insert student mark
declare @student_id INT = 1
declare @subject_id INT = 1
declare @max_student_id INT
declare @max_subject_id INT
select @max_student_id = count(1) from [student]
select @max_subject_id = count(1) from [subject]

WHILE @student_id <= @max_student_id
BEGIN
    set @subject_id = 1
    while @subject_id <= @max_subject_id
    BEGIN
        insert into [student_mark] ([student_id], [subject_id], [mark], [year])
        select @student_id, @subject_id, FLOOR(RAND()*(70-40+1)+40), 2019
        set @subject_id = @subject_id + 1
    END
    set @student_id = @student_id + 1
END


