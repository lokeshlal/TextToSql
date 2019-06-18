select 
    t.object_id as table_id,
    t.[name] as table_name,
    c.[name] as column_name,
    c.[column_id] as column_id,
    c.[system_type_id],
	ty.[name] as type_name
from 
    sys.columns c 
    join sys.tables t
    on c.object_id = t.object_id 
	join sys.types ty
	on c.system_type_id = ty.user_type_id
where 
    t.type = 'U'
order by 
    t.[name], c.[column_id]
