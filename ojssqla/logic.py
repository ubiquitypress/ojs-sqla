import ojs
import collections
import hashlib

from sqlalchemy.orm import joinedload,subqueryload, contains_eager
from sqlalchemy import desc, asc, func, and_, or_, extract
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

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


def dict_ojs_settings_results(settings_results, locales=None):
	results_dict = {}
	if locales:
		results_dict = dict_ojs_settings_results_localised(settings_results, locales)
	else:
		for row in settings_results:
			if row.setting_type == 'object' and row.setting_name == 'pub-id::doi':
				results_dict[row.setting_name.replace('-', '_').replace('::', '_')] = loads(row.setting_value).get('en_US')
			else:
				results_dict[row.setting_name.replace('-', '_').replace('::', '_')] = row.setting_value

	return results_dict

def dict_ojs_settings_results_localised(settings_results, locales):
	locales.append('') #ensures that non localised settings are also being pulled.
	results_dict = {}
	# get the settings that have the user language
	for row in settings_results:
		if row.locale == locales[0]:
			results_dict[row.setting_name.replace('-', '_').replace('::', '_')] = row.setting_value

	#find any missing settings on the previous language and try with the default language
	for locale in locales:
		for row in settings_results:
			if row.locale == locale:
				try :
					if results_dict[row.setting_name.replace('-', '_').replace('::', '_')] == None or len(results_dict[row.setting_name.replace('-', '_').replace('::', '_')]) <1:
						results_dict[row.setting_name.replace('-', '_').replace('::', '_')] = row.setting_value
				except KeyError:
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

def editorial_team(session, locale='en_US'):
	group_dict = collections.OrderedDict()
	groups = session.query(ojs.GroupSettings).join(ojs.Group, ojs.GroupSettings.group_id == ojs.Group.group_id).filter(ojs.GroupSettings.locale == locale).order_by(ojs.Group.seq)
	for g in groups:
		members = session.query(ojs.GroupMemberships).filter(ojs.GroupMemberships.group_id == g.group_id).order_by(ojs.GroupMemberships.seq)
		group = session.query(ojs.Group).filter(ojs.Group.group_id == g.group_id).one()

		group_dict[g.setting_value] = [{'first_name': m.user.first_name, 'last_name': m.user.last_name, 'email': m.user.email, 'url': m.user.url,  'affiliation': get_user_affiliation(session, m.user.user_id, locale), 'bio': get_user_bio(session, m.user.user_id, locale), 'country': m.user.country, 'display_email': group.publish_email } for m in members if m.user]

	return group_dict


def get_serialized_setting(session, setting_name):
	try:
		serial = session.query(ojs.JournalSetting.setting_value).filter(ojs.JournalSetting.setting_name == setting_name).one()
		return loads(serial[0], array_hook=collections.OrderedDict)
	except NoResultFound:
		return None

def get_user_affiliation(session, user_id, locale=None):
	try:
		user_affiliation = as_dict(session.query(ojs.UserSetting).filter(ojs.UserSetting.locale == locale, ojs.UserSetting.user_id == user_id, ojs.UserSetting.setting_name == 'affiliation').one())
	except NoResultFound:
		try:
			user_affiliation = as_dict(session.query(ojs.UserSetting).filter(ojs.UserSetting.user_id == user_id, ojs.UserSetting.setting_name == 'affiliation').first())
		except NoResultFound:
			return None
	return user_affiliation.get('setting_value', None)

def get_user_bio(session, user_id, locale):

	try:
		user_bio = as_dict(session.query(ojs.UserSetting).filter(ojs.UserSetting.locale == locale, ojs.UserSetting.user_id == user_id, ojs.UserSetting.setting_name == 'biography').one())
	except NoResultFound:
		try:
			user_bio = as_dict(session.query(ojs.UserSetting).filter(ojs.UserSetting.locale == locale, ojs.UserSetting.user_id == user_id, ojs.UserSetting.setting_name == 'biography').first())
		except NoResultFound:
			return None
	return user_bio.get('setting_value', None)

def get_additional_policies(session, locale=None):
	try:
		serial = session.query(ojs.JournalSetting.setting_value).filter(ojs.JournalSetting.setting_name == 'customAboutItems', ojs.JournalSetting.locale == locale).one()
		return loads(serial[0], array_hook=collections.OrderedDict)
	except NoResultFound:
		return None

def get_section_policies(session, locale=None):
	section_dict = collections.OrderedDict()
	sections = session.query(ojs.SectionSettings).join(ojs.Section).filter(ojs.SectionSettings.setting_name == 'title', ojs.Section.hide_about == 0, ojs.SectionSettings.locale == locale).order_by(ojs.Section.seq)

	for s in sections:
		policy = session.query(ojs.SectionSettings).filter(ojs.SectionSettings.setting_name == 'policy', ojs.SectionSettings.section_id == s.section_id, ojs.SectionSettings.locale == locale).first()
		section = as_dict(session.query(ojs.Section).filter(ojs.Section.section_id == s.section_id).one())
		if policy:
			section_dict[s.setting_value] = {'restricted' : section['editor_restricted'], 'indexed': section['meta_indexed'], 'reviews': section['meta_reviewed'], 'policy': policy.setting_value}

	return section_dict

def get_section_editors(session, section_id):
	editors = all_as_dict(session.query(ojs.SectionEditor).filter(ojs.SectionEditor.section_id == section_id).all())
	for editor in editors:
		editor['user'] = as_dict(get_user_from_id(session, editor.get('user_id')))
		editor['section'] = as_dict(get_section(session, editor.get('section_id')))

	return editors

def assign_section_editor(session, article, submission_id, editor):
	assignment_dict = {
		'article_id': submission_id,
		'editor_id': editor.get('user_id'),
		'can_edit':editor.get('can_edit'),
		'can_review': editor.get('can_review'),
		'date_assigned': date.today(),
		'date_notified': date.today(),
	}
	assignment = ojs.EditAssignment(**assignment_dict)
	session.add(assignment)
	session.commit()
	return 'assigned'

def get_journal_setting(session, setting_name, locale=None):
	try:
		return session.query(ojs.JournalSetting.setting_value).filter(ojs.JournalSetting.setting_name == setting_name, ojs.JournalSetting.locale == locale).one()
	except NoResultFound:
		try:
			return session.query(ojs.JournalSetting.setting_value).filter(ojs.JournalSetting.setting_name == setting_name, ojs.JournalSetting.locale == 'en_US').one()
		except NoResultFound:
			return None

def ojs_journal_settings(session, locale=None):
	return session.query(ojs.JournalSetting).filter(ojs.JournalSetting.locale == locale)

def feeling_lucky_settings(session):
	return session.query(ojs.JournalSetting)

def non_localised_setting(session, setting_name):
	try:
		return session.query(ojs.JournalSetting.setting_value).filter(ojs.JournalSetting.setting_name == setting_name).first()
	except NoResultFound:
		return None

def get_submission_checklist(session, locale):
	try:
		checklist = session.query(ojs.JournalSetting.setting_value).filter(ojs.JournalSetting.setting_name == 'submissionChecklist', ojs.JournalSetting.locale == locale).one()
		return loads(checklist[0], array_hook=collections.OrderedDict)
	except NoResultFound:
		return None

def get_article_list(session, filter_checks=None, order_by=None, articles_per_page=25, offset=0, taxonomy=0):
	order_list = []
	print taxonomy
	if order_by == 'page_number':
		order_list.append(desc(ojs.Article.pages))
	elif order_by == 'section':
		order_list.append(desc(ojs.Section.seq))
	else:
		order_list.append(desc(ojs.PublishedArticle.date_published))
	filter_taxonomy, join_taxonomy = [], []
	if taxonomy > 0:
		filter_taxonomy.append(ojs.TaxonomyArticle.taxonomy_id == taxonomy)
		join_taxonomy.append(ojs.TaxonomyArticle)

	if not filter_checks:
		return session.query(ojs.Article).join(ojs.Section).join(*join_taxonomy).join(ojs.PublishedArticle).join(ojs.Issue).filter(ojs.PublishedArticle.date_published != None, ojs.Issue.date_published != None, *filter_taxonomy).order_by(*order_list).offset(offset).limit(articles_per_page)
	else:
		return session.query(ojs.Article).join(ojs.Section).join(*join_taxonomy).join(ojs.PublishedArticle).join(ojs.Issue).filter(ojs.PublishedArticle.date_published != None, ojs.Issue.date_published != None, ojs.Article.section_id.in_(filter_checks), *filter_taxonomy).order_by(*order_list).offset(offset).limit(articles_per_page)

def get_article_count(session):
	return session.query(func.count(ojs.Article.article_id)).join(ojs.PublishedArticle).join(ojs.Issue).filter(ojs.PublishedArticle.date_published != None, ojs.Issue.date_published != None).one()

def get_article(session, doi):
	try:
		return session.query(ojs.Article).join(ojs.ArticleSetting).join(ojs.PublishedArticle).join(ojs.Issue).filter(ojs.ArticleSetting.setting_name == 'pub-id::doi', ojs.ArticleSetting.setting_value == doi, ojs.Issue.date_published != None).one()
	except NoResultFound:
		try:
			return session.query(ojs.Article).join(ojs.ArticleSetting).join(ojs.PublishedArticle).join(ojs.Issue).filter(ojs.ArticleSetting.setting_name == 'pub-id::publisher-id', ojs.ArticleSetting.setting_value == doi, ojs.Issue.date_published != None).one()
		except NoResultFound:
			return None

def get_article_by_id(session, doi):
	try:
		return session.query(ojs.Article).join(ojs.PublishedArticle).join(ojs.Issue).filter(ojs.Article.article_id == doi, ojs.Issue.date_published != None).one()
	except NoResultFound:
		try:
			return session.query(ojs.Article).join(ojs.ArticleSetting).join(ojs.PublishedArticle).join(ojs.Issue).filter(ojs.ArticleSetting.setting_name == 'pub-id::publisher-id', ojs.ArticleSetting.setting_value == doi, ojs.Issue.date_published != None).one()
		except NoResultFound:
			return None

def get_article_by_pubid(session, pubid):
	try:
		return session.query(ojs.Article).join(ojs.ArticleSetting).join(ojs.PublishedArticle).join(ojs.Issue).filter(ojs.ArticleSetting.setting_name == 'pub-id::publisher-id', ojs.ArticleSetting.setting_value == pubid, ojs.Issue.date_published != None).one()
	except NoResultFound:
		try:
			return session.query(ojs.Article).join(ojs.ArticleSetting).filter(ojs.Article.article_id == pubid).one()
		except NoResultFound:
			return None

def get_articles_by_year(session, year):
	return session.query(ojs.Article).join(ojs.PublishedArticle).filter(extract('year', ojs.PublishedArticle.date_published) == year)

def get_issues_by_year(session, year):
	return session.query(ojs.Issue).filter(extract('year', ojs.Issue.date_published) == year)

def get_all_article_settings(session, article_id):
	return session.query(ojs.ArticleSetting).filter(ojs.ArticleSetting.article_id == article_id)

def get_article_settings(session, article_id, setting_name):
	return session.query(ojs.ArticleSetting).filter(ojs.ArticleSetting.article_id == article_id, ojs.ArticleSetting.setting_name == setting_name).one()

def get_latest_articles(session, limit):
	return session.query(ojs.Article).join(ojs.PublishedArticle).join(ojs.Issue).filter(ojs.PublishedArticle.date_published != None, ojs.Issue.date_published != None).order_by(ojs.PublishedArticle.date_published.desc(), ojs.PublishedArticle.seq.desc()).limit(limit)

def get_popular_articles(session, limit):
	return session.query(ojs.Article).join(ojs.PublishedArticle).order_by(ojs.PublishedArticle.date_published.desc()).limit(limit)

def get_section_setting(session, setting_name, section_id):
	return session.query(ojs.SectionSettings).filter(ojs.SectionSettings.section_id == section_id, ojs.SectionSettings.setting_name == setting_name).one()

def get_journal_licenses(session):
	return session.query(ojs.Licenses).filter(ojs.Licenses.enabled == 1)

def get_article_galley(session, galley_id):
	try:
		return session.query(ojs.ArticleGalley).filter(ojs.ArticleGalley.galley_id == galley_id).one()
	except NoResultFound:
		return None

def get_first_html_galley(session, article_id):
	try:
		return session.query(ojs.ArticleGalley).join(ojs.ArticleFile).filter(ojs.ArticleGalley.article_id == article_id, or_(ojs.ArticleFile.file_type == 'application/xml', ojs.ArticleFile.file_type == 'text/html')).order_by(ojs.ArticleFile.file_type).first()
	except NoResultFound:
		return None

def get_article_file(session, file_id):
	try:
		return session.query(ojs.ArticleFile).filter(ojs.ArticleFile.file_id == file_id).one()
	except NoResultFound:
		return None

def get_article_figure(session, article_id, orig_filename):
	try:
		return session.query(ojs.ArticleFile).filter(ojs.ArticleFile.article_id == article_id, ojs.ArticleFile.original_file_name == orig_filename).order_by(desc(ojs.ArticleFile.revision)).first()
	except NoResultFound:
		return None

def get_article_sections(session):
	return session.query(ojs.Section).order_by(ojs.Section.seq)

def get_section_settings(session, section_id):
	return session.query(ojs.SectionSettings).filter(ojs.SectionSettings.section_id == section_id)

def get_section(session, section_id):
	try:
		return session.query(ojs.Section).filter(ojs.Section.section_id == section_id).one()
	except NoResultFound:
		return None

def get_issues(session):
	return session.query(ojs.Issue).join(ojs.CustomIssueOrder, ojs.Issue.issue_id == ojs.CustomIssueOrder.issue_id).filter(ojs.Issue.date_published != None, or_(ojs.Issue.access_status == 0, ojs.Issue.access_status == 1, and_(ojs.Issue.access_status == 2, ojs.Issue.open_access_date<=date.today()))).order_by(asc(ojs.CustomIssueOrder.seq), desc(ojs.Issue.issue_id))

def get_issue(session, volume_id, issue_id, ojs_id):
	try:
		return session.query(ojs.Issue).filter(ojs.Issue.volume == volume_id, ojs.Issue.number == issue_id, ojs.Issue.issue_id == ojs_id, or_(ojs.Issue.access_status == 0, ojs.Issue.access_status == 1, and_(ojs.Issue.access_status == 2, ojs.Issue.open_access_date<=date.today()))).one()
	except NoResultFound:
		return None

def get_issue_preview(session, ojs_id):
	try:
		return session.query(ojs.Issue).filter(ojs.Issue.issue_id == ojs_id).one()
	except NoResultFound:
		return None

def get_issue_settings(session, issue_id):
	return session.query(ojs.IssueSettings).filter(ojs.IssueSettings.issue_id == issue_id)

def get_issue_articles(session, volume_id, issue_id, ojs_id):
	return session.query(ojs.Article).join(ojs.PublishedArticle).join(ojs.Issue).filter(ojs.PublishedArticle.date_published != None, ojs.Issue.volume == volume_id, ojs.Issue.number == issue_id, ojs.Issue.issue_id == ojs_id).order_by(ojs.PublishedArticle.seq)

def get_issue_articles_by_section_id(session, ojs_id, section_id):
	return session.query(ojs.Article).join(ojs.PublishedArticle).join(ojs.Issue).filter(ojs.PublishedArticle.date_published != None, ojs.Issue.issue_id == ojs_id, ojs.Article.section_id == section_id).order_by(ojs.PublishedArticle.seq)

def get_issue_preview_articles_by_section_id(session, ojs_id, section_id):
	return session.query(ojs.Article).join(ojs.PublishedArticle).join(ojs.Issue).filter(ojs.Issue.issue_id == ojs_id, ojs.Article.section_id == section_id).order_by(ojs.PublishedArticle.seq)


def get_issue_file(session, issue_id, file_id):
	try:
		return session.query(ojs.IssueFile).filter(ojs.IssueFile.issue_id == issue_id, ojs.IssueFile.file_id == file_id).one()
	except NoResultFound:
		return None

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
	return session.query(ojs.Article).join(ojs.PublishedArticle).filter(ojs.PublishedArticle.published_article_id.in_(article_ids)).order_by(desc(ojs.PublishedArticle.date_published))

def get_collections_from_article(session, article):
	if article.get('published_article'):
		collections_article = all_as_dict(session.query(ojs.CollectionArticle).filter(ojs.CollectionArticle.published_article_id == article['published_article'].published_article_id))
		collections = []
		for collection_article in collections_article:
			collections.append(as_dict(session.query(ojs.Collection).filter(ojs.Collection.id == collection_article.get('collection_id')).one()))
		return collections
	else:
		return None

def get_latest_announcement(session):
	try:
		return session.query(ojs.Announcement).filter(or_(ojs.Announcement.date_expire >= date.today(), ojs.Announcement.date_expire == None)).order_by(desc(ojs.Announcement.date_posted)).first()
	except NoResultFound:
		return None

def get_announcements(session):
	return session.query(ojs.Announcement).filter(or_(ojs.Announcement.date_expire >= date.today(), ojs.Announcement.date_expire == None)).order_by(desc(ojs.Announcement.date_posted))

def get_multi_announcements(session, limit):

	print limit
	return session.query(ojs.Announcement).filter(or_(ojs.Announcement.date_expire >= date.today(), ojs.Announcement.date_expire == None)).order_by(desc(ojs.Announcement.date_posted)).limit(limit)

def get_announcement(session, announcement_id):
	try:
		return session.query(ojs.Announcement).filter(ojs.Announcement.announcement_id == announcement_id).one()
	except NoResultFound:
		return None

def get_announcement_settings(session, announcement_id):
	return session.query(ojs.AnnouncementSettings).filter(ojs.AnnouncementSettings.announcement_id == announcement_id)

def get_announcement_type_settings(session, type_id):
	try:
		return session.query(ojs.AnnouncementTypeSettings).filter(ojs.AnnouncementTypeSettings.type_id == type_id)
	except NoResultFound:
		return None


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

def transfer_taxonomy(session, article_id, taxonomy_id):
	new_taxonomy_article = ojs.TaxonomyArticle(article_id=article_id, taxonomy_id=taxonomy_id)
	session.add(new_taxonomy_article)
	session.flush()


def article_transfer_stage_one(session, article_one, article_settings, taxonomy_id=None):
	'''
	Creates the initial article, gets the id and creates its settings values
	'''

	new_article = ojs.Article(**article_one)
	session.add(new_article)
	session.flush()

	# Add Article Settings
	for k,v in article_settings.iteritems():
		kwargs = {
			'article_id': new_article.article_id,
			'locale': 'en_US',
			'setting_name': k,
			'setting_value': v,
			'setting_type': 'string',
		}
		new_article_setting = ojs.ArticleSetting(**kwargs)
		session.add(new_article_setting)
		session.flush()

	# Add Review Round
	review_kwargs = {
		'submission_id': new_article.article_id,
		'stage_id': None,
		'round': 1,
		'review_revision': 1,
		'status': None,
	}
	new_review_round = ojs.ReviewRound(**review_kwargs)
	session.add(new_review_round)
	session.flush()

	if taxonomy_id:
		transfer_taxonomy(session, new_article.article_id, taxonomy_id)

	session.commit()
	return new_article.article_id

def file_transfer(session, _dict, file_id, file_type, file_extension):
	'''
	Creates file records in OJS associated with an article
	'''
	new_file = ojs.ArticleFile(**_dict)
	session.add(new_file)
	session.commit()

	if file_type == 'manuscript':
		file_abbrev = 'SM'
	elif file_type == 'figure':
		file_abbrev = 'SP'
	elif file_type == 'review':
		file_abbrev = 'RV'
	elif file_type == 'data':
		file_abbrev = 'SP'

	new_file.file_name = '%s-%s-%s-%s%s' % (new_file.article_id, new_file.file_id, '1', file_abbrev, file_extension)
	session.commit()

	return {
		'file_id': file_id,
		'file_type': file_type,
		'ojs_file_id': new_file.file_id,
		'file_name': new_file.file_name,
	}

def create_supp_record(session, _dict):
	new_supp = ojs.ArticleSupplementaryFile(**_dict)
	session.add(new_supp)
	session.commit()

def insert_article_author(session, article_author, article_author_settings):
	new_author = ojs.Author(**article_author)
	session.add(new_author)
	session.commit()

	for k,v in article_author_settings.iteritems():
		kwargs = {
			'author_id': new_author.author_id,
			'locale': 'en_US',
			'setting_name': k,
			'setting_value': v,
			'setting_type': 'string',
		}
		new_author_setting = ojs.AuthorSetting(**kwargs)
		session.add(new_author_setting)

	session.commit()

def update_article_manuscript(session, ojs_article_id, file_id):
	article = session.query(ojs.Article).filter(ojs.Article.article_id == ojs_article_id).one()
	article.submission_file_id = file_id
	session.commit()

def update_article_revision(session, ojs_article_id, file_id):
	article = session.query(ojs.Article).filter(ojs.Article.article_id == ojs_article_id).one()
	article.review_file_id = file_id
	session.commit()

def add_review_Reound(session, ojs_article_id):
	kwargs = {
		'submission_id': ojs_article_id,
		'round': 1,
		'review_revision': 1,
	}
	new_review_round = ojs.ReviewRound(**kwargs)
	session.commit()

def insert_roles(session, user_id, roles):
	for role in roles:
		kwargs = {
			'journal_id': 1,
			'user_id': user_id,
			'role_id': role,
		}
		new_role = ojs.Roles(**kwargs)
		session.add(new_role)
		session.flush()

	session.commit()
	return True

def remove_role_from_user(session, user_id, role_id):
	role = get_role(session, user_id, role_id)
	session.delete(role)
	session.commit()
	return True

def get_user_by_email(session, email):
	try:
		return session.query(ojs.User).filter(ojs.User.email == email).one()
	except NoResultFound:
		return None

def get_user_by_username(session, username):
	try:
		return session.query(ojs.User).filter(ojs.User.username == username).one()
	except NoResultFound:
		return None

def hash_password(username, password):
	return hashlib.sha1(("%s%s" % (username, password)).encode('utf-8')).hexdigest()

def get_login_user(session, username, password, unhashed_password):
	try:
		return session.query(ojs.User).filter(ojs.User.username == username, ojs.User.password == password).one()
	except NoResultFound:

		# If the user is not found, we move on to try and get the user based on email address, then rehash the password with that username to see if there is a match
		try:
			user = get_user_from_email(session, username)
			if user:
				password = hash_password(user.username, unhashed_password)
				return session.query(ojs.User).filter(ojs.User.username == user.username, ojs.User.password == password).one()
			else:
				return None
		except NoResultFound:
			return None

def set_password(session, user_id, password):
	user = session.query(ojs.User).filter(ojs.User.user_id == user_id).one()
	user.password = password
	session.commit()

def get_user_from_email(session, email):
	try:
		return session.query(ojs.User).filter(ojs.User.email == email).one()
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
			return session.query(ojs.User).join(ojs.Roles).filter(ojs.User.user_id == user_session.user_id).one()
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

def basic_search(session, search_term):
	return session.query(ojs.Article).join(ojs.ArticleSetting).join(ojs.PublishedArticle).filter(ojs.PublishedArticle.date_published != None).filter(or_(and_(ojs.ArticleSetting.setting_name == 'title', ojs.ArticleSetting.setting_value.match(search_term)), and_(ojs.ArticleSetting.setting_name == 'abstract', ojs.ArticleSetting.setting_value.match(search_term)) ) )

def cloud_search_articles(session, dois):
	return session.query(ojs.Article).join(ojs.ArticleSetting).join(ojs.PublishedArticle).filter(ojs.PublishedArticle.date_published != None).filter(ojs.ArticleSetting.setting_name == 'pub-id::doi').filter(ojs.ArticleSetting.setting_value.in_(dois))

def get_user_settings(session, user_id):
	return session.query(ojs.UserSetting).filter(ojs.UserSetting.user_id == user_id)

def get_user_settings_dict(session, user_id):
	return dict_ojs_settings_results(session.query(ojs.UserSetting).filter(ojs.UserSetting.user_id == user_id))

def get_author_settings(session, author_id):
	return session.query(ojs.AuthorSetting).filter(ojs.AuthorSetting.author_id == author_id)

def get_author_settings_dict(session, author_id):
	return dict_ojs_settings_results(session.query(ojs.AuthorSetting).filter(ojs.AuthorSetting.author_id == author_id))

def get_orcid(session, orcid):
	try:
		try:
			return session.query(ojs.UserSetting).filter(ojs.UserSetting.setting_name == 'orcid', ojs.UserSetting.setting_value == orcid).one()
		except NoResultFound:
			return None
	except MultipleResultsFound:
		return session.query(ojs.UserSetting).filter(ojs.UserSetting.setting_name == 'orcid', ojs.UserSetting.setting_value == orcid).first()

def get_user_from_id(session, user_id):
	try:
		return session.query(ojs.User).filter(ojs.User.user_id == user_id).one()
	except NoResultFound:
		return None

def get_footer_settings(session):
	return session.query(ojs.JournalSetting).filter(or_(ojs.JournalSetting.setting_name == 'publisherInstitution', ojs.JournalSetting.setting_name == 'publisherUrl',  ojs.JournalSetting.setting_name == 'onlineIssn',  ojs.JournalSetting.setting_name == 'printIssn'), ojs.JournalSetting.journal_id == 1)

def get_current_issue(session):
	try:
		return session.query(ojs.Issue).filter(ojs.Issue.current == 1).one()
	except NoResultFound:
		return None


def get_custom_order(session, issue_id):
	try:
		return session.query(ojs.CustomSectionOrders).filter(ojs.CustomSectionOrders.issue_id == issue_id).order_by(ojs.CustomSectionOrders.seq)
	except NoResultFound:
		return None

def get_section_order(session):
	return session.query(ojs.Section).order_by(ojs.Section.seq)


def get_taxonomies(session):
	return session.query(ojs.Taxonomy).filter(ojs.Taxonomy.front_end == 1).order_by(ojs.Taxonomy.name)

def get_article_taxonomies(session, article_id):
	return session.query(ojs.Taxonomy).join(ojs.TaxonomyArticle).filter(ojs.TaxonomyArticle.article_id == article_id)

def get_role(session, user_id, role_id):
	try:
		return session.query(ojs.Roles).filter(ojs.Roles.user_id == user_id, ojs.Roles.role_id == role_id).one()
	except NoResultFound:
		return None

def get_ojs_metrics(session, article_id):
	return session.query(ojs.Metrics).filter(ojs.Metrics.submission_id == article_id).order_by(asc(ojs.Metrics.assoc_type))

def add_role_to_user(session, role, user_id):
	kwargs = {
		'journal_id': 1,
		'user_id': user_id,
		'role_id': role,
	}

	new_role = ojs.Roles(**kwargs)
	session.add(new_role)
	session.commit()

def set_new_user_details(session, user_id, user_dict, settings_dict):
	user = session.query(ojs.User).filter(ojs.User.user_id == user_id).one()
	# update user details
	for k,v, in user_dict.iteritems():
		setattr(user, k, v)
		session.flush

	for k,v in settings_dict.iteritems():
		# update user setting
		try:
			setting = session.query(ojs.UserSetting).filter(ojs.UserSetting.user_id == user_id, ojs.UserSetting.setting_name == k).one()
			setattr(setting, 'setting_value', v )
			session.flush()

		# or create it:
		except NoResultFound:
			kwargs = {
					'user_id': user_id,
					'setting_name': k,
					'setting_value': v,
					'locale': 'en_US',
					'setting_type': 'string', # only for introduced settings, so fairly safe but only if we do validation on our end
					'assoc_type': 0,
				}
			new_setting = ojs.UserSetting(**kwargs)
			session.add(new_setting)

	session.commit()

def get_reviewing_interests(session, user_id):
	user_interests = all_as_dict(session.query(ojs.UserInterests).join(ControlledVocabEntry).filter(ojs.UserInterests.user_id == user_id))
	for interest in user_interest:
		interest['controlled_vocab']['settings'] = get_controlled_vocab_entry_settings(session, interest['controlled_vocab'].get('controlled_vocab_entry_id'))

	return user_interests

def get_controlled_vocab_entry_settings(session, entry_id):
	return dict_ojs_settings_results(session.query(ojs.ControlledVocabEntrySettings).filter(ojs.ControlledVocabEntrySettings.controlled_vocab_entry_id == entry_id))

def delete_reviewing_interests(session, user_id):
	user_interests = session.query(ojs.UserInterests).filter(ojs.UserInterests.user_id == user_id).all()
	[session.delete(interest) for interest in user_interests]
	session.commit()
	return True

def set_reviewing_interest(session, interest, user):
	#First, the new vocab entry
	kwargs = {
		'controlled_vocab_id': 302
	}

	new_vocab_entry = ojs.ControlledVocabEntry(**kwargs)
	session.add(new_vocab_entry)
	session.commit()

	#second, relate it to the user
	kwargs = {
		'controlled_vocab_entry_id': new_vocab_entry.controlled_vocab_entry_id,
		'user_id': user
	}
	new_user_interest =  ojs.UserInterests(**kwargs)
	session.add(new_user_interest)
	session.commit()

	#third, insert the vocab details
	kwargs = {
		'controlled_vocab_entry_id': new_vocab_entry.controlled_vocab_entry_id,
		'setting_name': 'interest',
		'setting_type': 'string',
	}
	
	try:
		kwargs['setting_value'] = interest.name
	except:
		kwargs['setting_value'] = interest

	new_controlled_vocab_settings = ojs.ControlledVocabEntrySettings(**kwargs)
	session.add(new_controlled_vocab_settings)
	session.commit()

def get_static_page(session, page):
	try:
		return session.query(ojs.StaticPage).filter(ojs.StaticPage.path == page).one()
	except NoResultFound:
		return None

def get_page_settings(session, page_id):
	return session.query(ojs.StaticPageSetting).filter(ojs.StaticPageSetting.static_page_id == page_id)

def latest_articles_feed(session):
	return session.query(ojs.Article).join(ojs.PublishedArticle).join(ojs.Issue).filter(ojs.PublishedArticle.date_published != None, ojs.Issue.date_published != None).order_by(desc(ojs.PublishedArticle.date_published)).limit(10)

def get_any_article(session, article_id):
	return session.query(ojs.Article).join(ojs.ArticleSetting).filter(ojs.Article.article_id == article_id).one()

def get_file_from_ojs_name(session, article_id, ojs_file_name):
	return session.query(ojs.ArticleFile).filter(ojs.ArticleFile.article_id == article_id, ojs.ArticleFile.file_name == ojs_file_name).one()

def get_supp_file_settings(session, file_id):
	return session.query(ojs.ArticleSuppFileSettings).join(ojs.ArticleSupplementaryFile).filter(ojs.ArticleSupplementaryFile.file_id == file_id)

def get_handling_editors(session, article_id):
	users = all_as_dict(session.query(ojs.User).join(ojs.EditAssignment).filter(ojs.EditAssignment.article_id == article_id))
	for user in users:
		user['settings'] = get_user_settings_dict(session, user.get('user_id'))
	return users

def get_event_log_setting(session, log_id):
	return dict_ojs_settings_results(session.query(ojs.EventLogSettings).filter(ojs.EventLogSettings.log_id == log_id))

def get_log_entries(session, article_id, log_type):
	entries = all_as_dict(session.query(ojs.EventLog).filter(ojs.EventLog.assoc_id == article_id, ojs.EventLog.message == log_type).order_by(ojs.EventLog.date_logged))
	for entry in entries:
		entry['settings'] = get_event_log_setting(session, entry.get('log_id'))
	return entries

def get_review_field_name(session, element_id):
	return dict_ojs_settings_results(session.query(ojs.ReviewFormElementSettings).filter(ojs.ReviewFormElementSettings.setting_name == 'question', ojs.ReviewFormElementSettings.review_form_element_id == element_id))

def get_possible_answers(session, element_id):
	try:
		responses = session.query(ojs.ReviewFormElementSettings.setting_value).filter(ojs.ReviewFormElementSettings.setting_name == 'possibleResponses', ojs.ReviewFormElementSettings.review_form_element_id == element_id).one()
		return loads(responses[0])
	except NoResultFound:
		return None

def get_review_responses(session, review_id):
	review_responses = all_as_dict(session.query(ojs.ReviewFormResponses).filter(ojs.ReviewFormResponses.review_id == review_id))

	for response in review_responses:
		response['field_name'] = get_review_field_name(session, response['review_form_element_id'])
		response['possible_answers'] = get_possible_answers(session, response['review_form_element_id'])
	return review_responses

def get_review_details(session, article_id):
	review_assignments = all_as_dict(session.query(ojs.ReviewAssignment).filter(ojs.ReviewAssignment.submission_id == article_id).order_by(ojs.ReviewAssignment.round, ojs.ReviewAssignment.date_assigned))
	for assignment in review_assignments:
		assignment['reviewer_settings'] = get_user_settings_dict(session, assignment.get('reviewer').user_id)
		assignment['form_answers'] = get_review_responses(session, assignment.get('review_id'))

	return review_assignments

def get_article_comments(session, article_id=None, date=None, article_ids=None, count=None):

	filters = [ojs.ArticleComment.comment_type == 4]
	if date:
		filters.append(ojs.ArticleComment.date_posted > date)
	if article_id:
		filters.append(ojs.ArticleComment.article_id == article_id)
	elif article_ids:
		filters.append(ojs.ArticleComment.article_id in article_ids)

	if count:
		return session.query(ojs.ArticleComment.article_id).filter(*filters).count()
	else:
		return all_as_dict(session.query(ojs.ArticleComment).filter(*filters).order_by('date_posted desc'))

# def get_article_comments(session, article_id, date=None):
# 	return all_as_dict(session.query(ojs.ArticleComment).filter(ojs.ArticleComment.article_id == article_id, ojs.ArticleComment.comment_type == 4))

def get_email_template(session, email_key):
	return as_dict(session.query(ojs.EmailTemplateData).filter(ojs.EmailTemplateData.email_key == email_key).one())
