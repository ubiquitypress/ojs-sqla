import ojs
import collections

import logic

from sqlalchemy.orm import joinedload,subqueryload, contains_eager
from sqlalchemy import desc, asc, func, and_, or_, not_
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from datetime import date, datetime, timedelta
from pprint import pprint

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
		results_dict[row.setting_name.replace('-', '_').replace('::', '_')] = row.setting_value
		#results_dict[row.setting_name] = row.setting_value

	return results_dict

def deltadate(days, start_date=None):

	rdate = (start_date or datetime.today()) - timedelta(days)
	return rdate

#
# ORM Queries
#

def get_user_bio(session, user_id):
	try:
		user_bio = as_dict(session.query(ojs.UserSetting).filter(ojs.UserSetting.user_id == user_id, ojs.UserSetting.setting_name == 'biography').first())
		return user_bio.get('setting_value', None)
	except NoResultFound:
		return None

def get_user_affiliation(session, user_id):
	try:
		user_affiliation = as_dict(session.query(ojs.UserSetting).filter(ojs.UserSetting.user_id == user_id, ojs.UserSetting.setting_name == 'affiliation').first())
		return user_affiliation.get('setting_value', None)
	except NoResultFound:
		return None

def editorial_team(session):
	group_dict = collections.OrderedDict()
	groups = session.query(ojs.GroupSettings).join(ojs.Group, ojs.GroupSettings.group_id == ojs.Group.group_id).order_by(ojs.Group.seq)

	for g in groups:
		members = session.query(ojs.GroupMemberships).filter(ojs.GroupMemberships.group_id == g.group_id).order_by(ojs.GroupMemberships.seq)
		group = session.query(ojs.Group).filter(ojs.Group.group_id == g.group_id).one()

		group_dict[g.setting_value] = [{'user_id':m.user.user_id, 'first_name': m.user.first_name, 'last_name': m.user.last_name, 'email': m.user.email, 'url': m.user.url,  'affiliation': get_user_affiliation(session, m.user.user_id), 'bio': get_user_bio(session, m.user.user_id), 'country': m.user.country, 'seq': group.seq } for m in members if m]

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

def get_article_events(session, assoc_id):
	return all_as_dict(session.query(ojs.EventLog).filter(ojs.EventLog.assoc_id == assoc_id, ojs.EventLog.assoc_type == 257))

def get_published_article(session, article_id):
	try:
		return as_dict(session.query(ojs.PublishedArticle).filter(ojs.PublishedArticle.article_id == article_id).one())
	except NoResultFound:
		return None

def get_editor_decissions(session, article_id, decision_to_get):

	return as_dict(session.query(ojs.EditDecision).filter(ojs.EditDecision.article_id == article_id, ojs.EditDecision.decision == decision_to_get).order_by(desc(ojs.EditDecision.edit_decision_id)).first())

def get_author_settings(session, authors):

	for author in authors:
		author['settings'] = dict_ojs_settings_results(session.query(ojs.AuthorSetting).filter(ojs.AuthorSetting.author_id == author.get('author_id')))
	return authors

def get_articles(session):

	articles = all_as_dict(session.query(ojs.Article).join(ojs.Section).filter(ojs.Article.date_submitted != None))

	for article in articles:
		article['events'] = get_article_events(session, article['article_id'])
		article['settings'] = get_article_settings(session, article['article_id'])
		article['published_article'] = get_published_article(session, article['article_id'])
		article['latest_rejected_decission'] = get_editor_decissions(session, article['article_id'], 4)
		article['latest_accepted_decission'] = get_editor_decissions(session, article['article_id'], 1)
		article['authors'] = get_author_settings(session, article['authors'])

	return articles

def get_article_settings(session, article_id):
	return dict_ojs_settings_results(session.query(ojs.ArticleSetting).filter(ojs.ArticleSetting.article_id == article_id))

def get_galley_file(session, galley_file_id):
	try:
		return as_dict(session.query(ojs.ArticleFile).filter(ojs.ArticleFile.file_id == galley_file_id).one())
	except NoResultFound:
		return None

def get_edit_assignments(session, article_id):
	return all_as_dict(session.query(ojs.EditAssignment).filter(ojs.EditAssignment.article_id == article_id))

def get_revi_assignments(session, article_id):
	return all_as_dict(session.query(ojs.ReviewAssignment).filter(ojs.ReviewAssignment.submission_id == article_id))

def get_issues(session):
	issues = all_as_dict(session.query(ojs.Issue))
	for issue in issues:
	 	issue['title'] = as_dict(session.query(ojs.IssueSettings).filter(ojs.IssueSettings.issue_id == issue.get('issue_id'), ojs.IssueSettings.setting_name == 'title')).get('setting_value')
	 	issue['description'] = as_dict(session.query(ojs.IssueSettings).filter(ojs.IssueSettings.issue_id == issue.get('issue_id'), ojs.IssueSettings.setting_name == 'description')).get('setting_value')
	 	issue.pop('journal_id')
	return issues
