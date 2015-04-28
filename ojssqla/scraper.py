import ojs
import collections

from sqlalchemy.orm import joinedload,subqueryload, contains_eager
from sqlalchemy import desc, asc, func, and_, or_, not_
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from datetime import datetime, timedelta
from phpserialize import *

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

def dict_ojs_settings_results(settings_results):
	results_dict = {}

	for row in settings_results:
		results_dict[row.setting_name] = row.setting_value

	return results_dict

def deltadate(days, start_date=None):
	rdate = (start_date or datetime.today()) - timedelta(days)
	return rdate


#
# queries
#

def ojs_journal_settings(session):
	return dict_ojs_settings_results(session.query(ojs.JournalSetting).filter(not_(ojs.JournalSetting.setting_name.contains('::'))))

def get_journal_users(session):
	users = all_as_dict(session.query(ojs.User).join(ojs.Roles))

	for user in users:
		user['settings'] = get_user_settings(session, user['user_id'])

	return users

def get_user_settings(session, user_id):
	return dict_ojs_settings_results(session.query(ojs.UserSetting).filter(ojs.UserSetting.user_id == user_id))
