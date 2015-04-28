import ojs
import collections

import logic

from sqlalchemy.orm import joinedload,subqueryload, contains_eager
from sqlalchemy import desc, asc, func, and_, or_, not_
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from datetime import date, datetime, timedelta

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
<<<<<<< HEAD
		results_dict[row.setting_name.replace('-', '_').replace('::', '_')] = row.setting_value
=======
		results_dict[row.setting_name] = row.setting_value
>>>>>>> ec5a8f85f08ae0ec4aaedfa5e1cb1752b4b65c46

	return results_dict

def deltadate(days, start_date=None):

	rdate = (start_date or date.today()) - timedelta(days)
	return rdate.strftime('%Y-%m-%d')

#
# ORM Queries
#

def get_user_bio(session, user_id):
	try:
		user_bio = as_dict(session.query(ojs.UserSetting).filter(ojs.UserSetting.user_id == user_id, ojs.UserSetting.setting_name == 'biography').one())
		return user_bio.get('setting_value', None)
	except NoResultFound:
		return None

def get_user_affiliation(session, user_id):
	try:
		user_affiliation = as_dict(session.query(ojs.UserSetting).filter(ojs.UserSetting.user_id == user_id, ojs.UserSetting.setting_name == 'affiliation').one())
		return user_affiliation.get('setting_value', None)
	except NoResultFound:
		return None

def editorial_team(session):
	group_dict = collections.OrderedDict()
	groups = session.query(ojs.GroupSettings).join(ojs.Group, ojs.GroupSettings.group_id == ojs.Group.group_id).order_by(ojs.Group.seq)

	for g in groups:
		members = session.query(ojs.GroupMemberships).filter(ojs.GroupMemberships.group_id == g.group_id).order_by(ojs.GroupMemberships.seq)
		group = session.query(ojs.Group).filter(ojs.Group.group_id == g.group_id).one()

		group_dict[g.setting_value] = [{'user_id':m.user.user_id, 'first_name': m.user.first_name, 'last_name': m.user.last_name, 'email': m.user.email, 'url': m.user.url,  'affiliation': get_user_affiliation(session, m.user.user_id), 'bio': get_user_bio(session, m.user.user_id), 'country': m.user.country, 'seq': group.seq } for m in members]

	return group_dict

def get_section_setting(session, setting_name, section_id):
	return session.query(ojs.SectionSettings).filter(ojs.SectionSettings.section_id == section_id, ojs.SectionSettings.setting_name == setting_name).one()

def get_sections(session):
		
	sections = all_as_dict(session.query(ojs.Section))
	for section in sections:
		setting = get_section_setting(session, 'title', section.get('section_id'))
		section['section_name'] = setting.setting_value
	return sections

def get_article_events(session):
	events = all_as_dict(session.query(ojs.ArticleEventLog))
	return events


def ojs_journal_settings(session):
	return dict_ojs_settings_results(session.query(ojs.JournalSetting).filter(not_(ojs.JournalSetting.setting_name.contains('::'))))

def get_journal_users(session):
	users = all_as_dict(session.query(ojs.User).join(ojs.Roles))

	for user in users:
		user['settings'] = get_user_settings(session, user['user_id'])

	return users

def get_user_settings(session, user_id):
	return dict_ojs_settings_results(session.query(ojs.UserSetting).filter(ojs.UserSetting.user_id == user_id))
