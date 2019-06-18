select 
    object_id as table_id, 
    [name] as table_name
from 
    sys.tables 
where 
    type = 'U';