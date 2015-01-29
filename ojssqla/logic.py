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

def dict_ojs_settings_results(settings_results):
	results_dict = {}

	for row in settings_results:
		results_dict[row.setting_name.replace('-', '_').replace('::', '_')] = row.setting_value

	return results_dict

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
		group_dict[g.setting_value] = [{'first_name': m.user.first_name, 'last_name': m.user.last_name, 'email': m.user.email, 'url': m.user.url,  'affiliation': get_user_affiliation(session, m.user.user_id), 'bio': get_user_bio(session, m.user.user_id)} for m in members]

	return group_dict

def get_user_affiliation(session, user_id):
	user_affiliation = as_dict(session.query(ojs.UserSetting).filter(ojs.UserSetting.user_id == user_id, ojs.UserSetting.setting_name == 'affiliation').one())
	return user_affiliation.get('setting_value', None)

def get_user_bio(session, user_id):
	user_bio = as_dict(session.query(ojs.UserSetting).filter(ojs.UserSetting.user_id == user_id, ojs.UserSetting.setting_name == 'biography').one())
	return user_bio.get('setting_value', None)

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

def get_journal_setting(session, setting_name):
	try:
		return session.query(ojs.JournalSetting.setting_value).filter(ojs.JournalSetting.setting_name == setting_name).one()
	except NoResultFound:
		return None

def get_submission_checklist(session):
	checklist = session.query(ojs.JournalSetting.setting_value).filter(ojs.JournalSetting.setting_name == 'submissionChecklist').one()
	return loads(checklist[0], array_hook=collections.OrderedDict)

def get_article_list(session, filter_checks=None, order_by=None, articles_per_page=25, offset=0):
	order_list = []

	if order_by == 'page_number':
		order_list.append(desc(ojs.Article.pages))
	else:
		order_list.append(desc(ojs.PublishedArticle.date_published))

	if not filter_checks:
		return session.query(ojs.Article).join(ojs.PublishedArticle).order_by(*order_list).offset(offset).limit(articles_per_page)
	else:
		return session.query(ojs.Article).join(ojs.PublishedArticle).filter(ojs.Article.section_id.in_(filter_checks)).order_by(*order_list).limit(articles_per_page)

def get_article_count(session):
	return session.query(func.count(ojs.PublishedArticle.article_id)).one()

def get_article(session, doi):
	return session.query(ojs.Article).join(ojs.ArticleSetting).filter(ojs.ArticleSetting.setting_name == 'pub-id::doi', ojs.ArticleSetting.setting_value == doi).one()

def get_all_article_settings(session, article_id):
	return session.query(ojs.ArticleSetting).filter(ojs.ArticleSetting.article_id == article_id)

def get_article_settings(session, article_id, setting_name):
	return session.query(ojs.ArticleSetting).filter(ojs.ArticleSetting.article_id == article_id, ojs.ArticleSetting.setting_name == setting_name).one()

def get_latest_articles(session, limit):
	return session.query(ojs.Article).join(ojs.PublishedArticle).order_by(ojs.PublishedArticle.date_published.desc()).limit(limit)

def get_popular_articles(session, limit):
	return session.query(ojs.Article).join(ojs.PublishedArticle).order_by(ojs.PublishedArticle.date_published.desc()).limit(limit)

def get_section_setting(session, setting_name, section_id):
	return session.query(ojs.SectionSettings).filter(ojs.SectionSettings.section_id == section_id, ojs.SectionSettings.setting_name == setting_name).one()

def get_article_galley(session, galley_id):
	return session.query(ojs.ArticleGalley).filter(ojs.ArticleGalley.galley_id == galley_id).one()

def get_first_html_galley(session, article_id):
	return session.query(ojs.ArticleGalley).filter(ojs.ArticleGalley.article_id == article_id, ojs.ArticleGalley.html_galley == 1).order_by(ojs.ArticleGalley.seq).first()

def get_article_file(session, file_id):
	return session.query(ojs.ArticleFile).filter(ojs.ArticleFile.file_id == file_id).one()

def get_article_figure(session, article_id, orig_filename):
	return session.query(ojs.ArticleFile).filter(ojs.ArticleFile.article_id == article_id, ojs.ArticleFile.original_file_name == orig_filename).order_by(desc(ojs.ArticleFile.revision)).one()

def get_article_sections(session):
	return session.query(ojs.Section).order_by(ojs.Section.seq)

def get_section_settings(session, section_id):
	return session.query(ojs.SectionSettings).filter(ojs.SectionSettings.section_id == section_id)

def get_issues(session):
	return session.query(ojs.Issue).order_by(desc(ojs.Issue.number), desc(ojs.Issue.volume))

def get_issue(session, volume_id):
	try:
		return session.query(ojs.Issue).filter(ojs.Issue.volume == volume_id).one()
	except NoResultFound:
		return None

def get_issue_settings(session, issue_id):
	return session.query(ojs.IssueSettings).filter(ojs.IssueSettings.issue_id == issue_id)

def get_issue_articles(session, volume_id):
	return session.query(ojs.Article).join(ojs.PublishedArticle).join(ojs.Issue).filter(ojs.Issue.volume == volume_id).order_by(ojs.PublishedArticle.seq)

def get_collections(session):
	return session.query(ojs.Collection).filter(ojs.Collection.disabled == None)

def get_collection(session, col_abbrev):
	try:
		return session.query(ojs.Collection).filter(ojs.Collection.abbrev == col_abbrev).one()
	except NoResultFound:
		return None

def get_collection_users(session, col_abbrev):
	try:
		return session.query(ojs.Collection).options(joinedload(ojs.Collection.articles)).options(joinedload(ojs.Collection.users)).filter(ojs.Collection.abbrev == col_abbrev).one()
	except NoResultFound:
		return None

def get_collection_user_name(session, user_id):
	try:
		return session.query(ojs.User).filter(ojs.User.user_id == user_id).one()
	except NoResultFound:
		pass

def get_collection_articles(session, collection_articles):
	article_ids = [article.get('published_article_id') for article in collection_articles]
	return session.query(ojs.Article).join(ojs.PublishedArticle).filter(ojs.Article.article_id.in_(article_ids)).order_by(ojs.Article.article_id)

def get_latest_announcement(session):
	try:
		return session.query(ojs.Announcement).filter(or_(ojs.Announcement.date_expire >= date.today(), ojs.Announcement.date_expire == None)).order_by(ojs.Announcement.date_posted).first()
	except NoResultFound:
		return None

def get_announcements(session):
	return session.query(ojs.Announcement).filter(or_(ojs.Announcement.date_expire >= date.today(), ojs.Announcement.date_expire == None)).order_by(desc(ojs.Announcement.date_posted))

def get_announcement(session, announcement_id):
	try:
		return session.query(ojs.Announcement).filter(ojs.Announcement.announcement_id == announcement_id).one()
	except NoResultFound:
		return None
		
def get_announcement_settings(session, announcement_id):
	return session.query(ojs.AnnouncementSettings).filter(ojs.AnnouncementSettings.announcement_id == announcement_id)

def transfer_user(session, ojs_user_dict, ojs_user_settings_dict):
	new_obj = ojs.User(**ojs_user_dict)
	session.add(new_obj)
	session.flush()

	for k,v in ojs_user_settings_dict.iteritems():
		kwargs = {
				'user_id': new_obj.user_id,
				'setting_name': k,
				'setting_value': v,
				'locale': 'en_US',
				'setting_type': 'string', # only for introduced settings, so fairly safe but only if we do validation on our end
				'assoc_type': 0,
		}
		new_setting = ojs.UserSetting(**kwargs)
		session.add(new_setting)
		session.flush()

	session.commit()
	return new_obj.user_id

def get_user_by_email(session, email):
	try:
		return session.query(ojs.User).filter(ojs.User.email == email).one()
	except NoResultFound:
		return None

def get_login_user(session, username, password):
	try:
		return session.query(ojs.User).filter(ojs.User.username == username, ojs.User.password == password).one()
	except NoResultFound:
		return None

def get_session_from_sessionid(session, ojs_session_id):
	try:
		return session.query(ojs.Sessions).filter(ojs.Sessions.session_id == ojs_session_id).one()
	except NoResultFound:
		return None

def get_user_from_sessionid(session, ojs_session_id):
	user_session = get_session_from_sessionid(session, ojs_session_id)

	if user_session:
		try:
			return session.query(ojs.User).filter(ojs.User.user_id == user_session.user_id).one()
		except NoResultFound:
			return None
	else:
		return None

def add_session_to_db(db_session, session_id, user, serialised_data, ip, user_agent, time_stamp):
	kwargs = {
		'session_id': session_id,
		'user_id': user.get('user_id'),
		'ip_address': ip,
		'user_agent': user_agent,
		'created': time_stamp,
		'last_used': time_stamp,
		'remember': 0,
		'data': serialised_data,
	}

	new_session = ojs.Sessions(**kwargs)
	db_session.add(new_session)
	db_session.commit()

def get_user_settings(session, user_id):
	return session.query(ojs.UserSetting).filter(ojs.UserSetting.user_id == user_id)


