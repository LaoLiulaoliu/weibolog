#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miracle (at) gmail.com>

from pgpool import PGPool


class PGWrapper(PGPool):
    def __init__(self, dbname='postgres'):
        super(PGWrapper, self).__init__(dbname)


    def select(self, table, args='*', condition=None, control=None):
        """ General select form of select
        Usage::

            >>> select('hospital', 'id, city', control='limit 1')
            select id, city from hospital limit 1;


            >>> select('hospital', 'id', 'address is null')
            select id from hospital where address is null;

        """
        sql = 'select {} from {}'.format(args, table)
        sql += self.parse_condition(condition) + (' {};'.format(control) if control else ';')
        return super(PGWrapper, self).execute(sql, result=True).results


    def update(self, table, kwargs, condition=None):
        """ All module update can user this function.
        condition only support string and dictionary.
        Usage::

            >>> update('dept', {'name': 'design', 'quantity': 3}, {'id': 'we4d'})
            update dept set name='design', quantity=3 where id='we4d';

            >>> update('dept', {'name': 'design', 'quantity': 3}, 'introduction is null')
            update dept set name='design', quantity=3 where introduction is null;

            >>> update('physician', {'$inc': {'status': -10}, 'present': 0}, {'id': 'someid'})
            update physician set status=status+-10, present=0 where id='someid';

        """
        sql = "update {} set {}"
        equations = []
        values = []
        for k, v in kwargs.iteritems():
            if k == '$inc' and isinstance(v, dict):
                for ik, iv in v.iteritems():
                    equations.append("{field}={field}+{value}".format(field=ik, value=iv))
            else:
                equations.append("{}=%s".format(k))
                values.append(v)

        sql = sql.format(table, ', '.join(equations))
        sql += self.parse_condition(condition) + ";"
        super(PGWrapper, self).execute(sql, values, result=False)


    def insert(self, table, kwargs):
        """
        Usage::

            >>> insert('hospital', {'id': '12de3wrv', 'province': 'shanghai'})
            insert into hospital (id, province) values ('12de3wrv', 'shanghai');

        """
        sql = "insert into " + table + " ({}) values ({});"
        keys, values = [], []
        [ (keys.append(k), values.append(v)) for k, v in kwargs.iteritems() ]
        sql = sql.format(', '.join(keys), ', '.join(['%s']*len(values)))
        super(PGWrapper, self).execute(sql, values, result=False)


    def delete(self, table, condition):
        """
        Usage::

            >>> delete('hospital', {'id': '12de3wrv'})
            delete from hospital where id='12de3wrv';

        """
        sql = "delete from {}".format(table)
        sql += self.parse_condition(condition) + ";"
        super(PGWrapper, self).execute(sql, result=False)


    def insert_inexistence(self, table, kwargs, condition):
        """
        Usage::

            >>> insert('hospital', {'id': '12de3wrv', 'province': 'shanghai'}, {'id': '12de3wrv'})
            insert into hospital (id, province) select '12de3wrv', 'shanghai' where not exists (select 1 from hospital where id='12de3wrv' limit 1);

        """
        sql = "insert into " + table + " ({}) "
        select = "select {} "
        condition = "where not exists (select 1 from " + table + "{} limit 1);".format( self.parse_condition(condition) )
        keys, values = [], []
        [ (keys.append(k), values.append(v)) for k, v in kwargs.iteritems() ]
        sql = sql.format(', '.join(keys)) + select.format( ', '.join(['%s']*len(values)) ) + condition
        super(PGWrapper, self).execute(sql, values, result=False)


    def parse_condition(self, condition):
        """ parse the condition, support string and dictonary
        """
        if isinstance(condition, bytes):
            sql = " where {}".format(condition)
        elif isinstance(condition, dict):
            conditions = []
            for k, v in condition.iteritems():
                if isinstance(v, unicode):
                    v = v.encode('utf-8')
                s = "{}='{}'".format(k, v) if isinstance(v, bytes) else "{}={}".format(k, v)
                conditions.append(s)
            sql = " where {}".format(', '.join(conditions))
        else:
            sql = ""
        return sql



    def select_join(self, table, field, join_table, join_field):
        """
        Usage::

            >>> select_join('hospital', 'id', 'department', 'hospid')
            select hospital.id from hospital left join department on hospital.id=department.hospid where department.hospid is null;

        """
        sql = "select {table}.{field} from {table} left join {join_table} "\
              "on {table}.{field}={join_table}.{join_field} "\
              "where {join_table}.{join_field} is null;".format(table=table,
                                                                field=field,
                                                                join_table=join_table,
                                                                join_field=join_field)
        return super(PGWrapper, self).execute(sql, result=True).results


    def joint(self, table, fields,
                    join_table, join_fields,
                    condition_field, condition_join_field,
                    join_method='left_join'):
        """
        Usage::

            >>> joint('user', 'name, id_number', 'medical_card', 'number', 'id', 'user_id', 'inner_join')
            select u.name, u.id_number, v.number from user as u inner join medical_card as v on u.id=v.user_id;

        """
        import string
        fields = map(string.strip, fields.split(','))
        select = ', '.join( ['u.{}'.format(field) for field in fields] )
        join_fields = map(string.strip, join_fields.split(','))
        join_select = ', '.join( ['v.{}'.format(field) for field in join_fields] )

        sql = "select {select}, {join_select} from {table} as u {join_method}"\
               " {join_table} as v on u.{condition_field}="\
               "v.{condition_join_field};".format(select=select,
                                                 join_select=join_select,
                                                 table=table,
                                                 join_method=join_method,
                                                 join_table=join_table,
                                                 condition_field=condition_field,
                                                 condition_join_field=condition_join_field)
        return super(PGWrapper, self).execute(sql, result=True).results

