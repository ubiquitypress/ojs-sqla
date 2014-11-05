import ojs
from sqlalchemy.orm import joinedload,subqueryload, contains_eager
from sqlalchemy import desc, asc, func, and_, or_
from sqlalchemy.orm.exc import NoResultFound

from datetime import date, timedelta

#
# utils
#

def as_dict(obj):
		"""
		returns a dictionary instead of an object. probably quite expensive, but very convenient for caching.
		"""
		x = {}
		if not obj:
				return x
		valid_keys = filter(lambda k: not k.startswith('_'), obj.__dict__.keys())
		for key in valid_keys:
				val = getattr(obj, key)
				if isinstance(val, list):
						x[key] = [as_dict(row) for row in val]
				else:
						x[key] = val
		return x

def all_as_dict(obj_list):
		return [as_dict(obj) for obj in obj_list]

def deltadate(days, start_date=None):
	rdate = (start_date or date.today()) - timedelta(days)
	return rdate.strftime('%Y-%m-%d')

#
# ORM Queries
#











