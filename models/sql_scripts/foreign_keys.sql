SELECT
    tr.name 'parent_table',
    cr.name 'parent_table_col', cr.column_id,
    tp.name 'refrenced_table',
    cp.name as 'referenced_table_col', cp.column_id
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
