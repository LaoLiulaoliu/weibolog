#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miracle (at) gmail.com>

from pgpool import PGPool


class PGWrapper(object):
    def __init__(self, dbname='postgres'):
        self.db = PGPool(dbname)


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
        return self.db.execute(sql, result=True).results


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
        self.db.execute(sql, values, result=False)


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
        self.db.execute(sql, values, result=False)


    def delete(self, table, condition):
        """
        Usage::

            >>> delete('hospital', {'id': '12de3wrv'})
            delete from hospital where id='12de3wrv';

        """
        sql = "delete from {}".format(table)
        sql += self.parse_condition(condition) + ";"
        self.db.execute(sql, result=False)


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
        self.db.execute(sql, values, result=False)


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
        return self.db.execute(sql, result=True).results

