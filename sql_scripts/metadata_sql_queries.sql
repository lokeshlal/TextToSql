select 
    object_id as table_id, 
    [name] as table_name
from 
    sys.tables 
where 
    type = 'U';

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
    t.type = 'U';

SELECT
    tp.name 'Parent table',
    cp.name, cp.column_id,
    tr.name 'Refrenced table',
    cr.name, cr.column_id
FROM 
    sys.foreign_keys fk
    INNER JOIN 
    sys.tables tp ON fk.parent_object_id = tp.object_id
    INNER JOIN 
    sys.tables tr ON fk.referenced_object_id = tr.object_id
    INNER JOIN 
    sys.foreign_key_columns fkc ON fkc.constraint_object_id = fk.object_id
    INNER JOIN 
    sys.columns cp ON fkc.parent_column_id = cp.column_id AND fkc.parent_object_id = cp.object_id
    INNER JOIN 
    sys.columns cr ON fkc.referenced_column_id = cr.column_id AND fkc.referenced_object_id = cr.object_id
where
	tr.type = 'U'
ORDER BY
    tp.name, cp.column_id

SELECT  OBJECT_NAME(ic.OBJECT_ID) AS TableName,
        COL_NAME(ic.OBJECT_ID,ic.column_id) AS ColumnName
FROM    sys.indexes AS i INNER JOIN 
        sys.index_columns AS ic ON  i.OBJECT_ID = ic.OBJECT_ID
                                AND i.index_id = ic.index_id
WHERE   i.is_primary_key = 1
