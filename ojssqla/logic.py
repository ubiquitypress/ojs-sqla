import ojs
import collections

from sqlalchemy.orm import joinedload,subqueryload, contains_eager
from sqlalchemy import desc, asc, func, and_, or_
from sqlalchemy.orm.exc import NoResultFound

from datetime import date, timedelta
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

def deltadate(days, start_date=None):
	rdate = (start_date or date.today()) - timedelta(days)
	return rdate.strftime('%Y-%m-%d')

#
# ORM Queries
#


def contact_settings(session, settings_to_get):
	return session.query(ojs.JournalSetting).filter(ojs.JournalSetting.setting_name.in_(settings_to_get))

def editorial_team(session):
	group_dict = collections.OrderedDict()
	groups = session.query(ojs.GroupSettings)

	for g in groups:
		members = session.query(ojs.GroupMemberships).filter(ojs.GroupMemberships.group_id == g.group_id)
		group_dict[g.setting_value] = ['%s %s' % (m.user.first_name, m.user.last_name) for m in members]

	return group_dict

def get_policy_scope(session):
	return session.query(ojs.JournalSetting.setting_value).filter(ojs.JournalSetting.setting_name == 'focusScopeDesc').one()

def get_policy_review(session):
	return session.query(ojs.JournalSetting.setting_value).filter(ojs.JournalSetting.setting_name == 'reviewPolicy').one()

def get_policy_pubfreq(session):
	return session.query(ojs.JournalSetting.setting_value).filter(ojs.JournalSetting.setting_name == 'pubFreqPolicy').one()

def get_policy_oapolicy(session):
	return session.query(ojs.JournalSetting.setting_value).filter(ojs.JournalSetting.setting_name == 'openAccessPolicy').one()

def get_policy_lockss(session):
	return session.query(ojs.JournalSetting.setting_value).filter(ojs.JournalSetting.setting_name == 'lockssLicense').one()

def get_additional_policies(session):
	serial = session.query(ojs.JournalSetting.setting_value).filter(ojs.JournalSetting.setting_name == 'customAboutItems').one()
	return loads(serial[0], array_hook=collections.OrderedDict)

def get_section_policies(session):
	section_dict = collections.OrderedDict()
	sections = session.query(ojs.SectionSettings).join(ojs.Section).filter(ojs.SectionSettings.setting_name == 'title').order_by(ojs.Section.seq)

	for s in sections:
		section = as_dict(session.query(ojs.Section).filter(ojs.Section.section_id == s.section_id).one())
		section_dict[s.setting_value] = {'restricted' : section['editor_restricted'], 'indexed': section['meta_indexed'], 'reviews': section['meta_reviewed'] }

	return section_dict





