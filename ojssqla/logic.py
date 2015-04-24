import ojs
import collections

from sqlalchemy.orm import joinedload,subqueryload, contains_eager
from sqlalchemy import desc, asc, func, and_, or_
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
	groups = session.query(ojs.GroupSettings).join(ojs.Group, ojs.GroupSettings.group_id == ojs.Group.group_id).order_by(ojs.Group.seq)

	for g in groups:
		members = session.query(ojs.GroupMemberships).filter(ojs.GroupMemberships.group_id == g.group_id).order_by(ojs.GroupMemberships.seq)
		group = session.query(ojs.Group).filter(ojs.Group.group_id == g.group_id).one()

		group_dict[g.setting_value] = [{'first_name': m.user.first_name, 'last_name': m.user.last_name, 'email': m.user.email, 'url': m.user.url,  'affiliation': get_user_affiliation(session, m.user.user_id), 'bio': get_user_bio(session, m.user.user_id), 'country': m.user.country, 'display_email': group.publish_email } for m in members]

	return group_dict

def get_user_affiliation(session, user_id):
	try:
		user_affiliation = as_dict(session.query(ojs.UserSetting).filter(ojs.UserSetting.user_id == user_id, ojs.UserSetting.setting_name == 'affiliation').one())
		return user_affiliation.get('setting_value', None)
	except NoResultFound:
		return None

def get_user_bio(session, user_id):
	try:
		user_bio = as_dict(session.query(ojs.UserSetting).filter(ojs.UserSetting.user_id == user_id, ojs.UserSetting.setting_name == 'biography').one())
		return user_bio.get('setting_value', None)
	except NoResultFound:
		return None

def get_additional_policies(session):
	try:
		serial = session.query(ojs.JournalSetting.setting_value).filter(ojs.JournalSetting.setting_name == 'customAboutItems').one()
		return loads(serial[0], array_hook=collections.OrderedDict)
	except NoResultFound:
		return None

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

def ojs_journal_settings(session):
	return session.query(ojs.JournalSetting)

def get_submission_checklist(session):
	try:
		checklist = session.query(ojs.JournalSetting.setting_value).filter(ojs.JournalSetting.setting_name == 'submissionChecklist').one()
		return loads(checklist[0], array_hook=collections.OrderedDict)
	except NoResultFound:
		return None

def get_article_list(session, filter_checks=None, order_by=None, articles_per_page=25, offset=0):
	order_list = []

	if order_by == 'page_number':
		order_list.append(desc(ojs.Article.pages))
	elif order_by == 'section':
		order_list.append(desc(ojs.Section.seq))
	else:
		order_list.append(desc(ojs.PublishedArticle.date_published))

	if not filter_checks:
		return session.query(ojs.Article).join(ojs.Section).join(ojs.PublishedArticle).join(ojs.Issue).filter(ojs.PublishedArticle.date_published != None, ojs.Issue.date_published != None).order_by(*order_list).offset(offset).limit(articles_per_page)
	else:
		return session.query(ojs.Article).join(ojs.Section).join(ojs.PublishedArticle).join(ojs.Issue).filter(ojs.PublishedArticle.date_published != None, ojs.Issue.date_published != None, ojs.Article.section_id.in_(filter_checks)).order_by(*order_list).offset(offset).limit(articles_per_page)

def get_article_count(session):
	return session.query(func.count(ojs.PublishedArticle.article_id)).filter(ojs.PublishedArticle.date_published != None).one()

def get_article(session, doi):
	try:
		return session.query(ojs.Article).join(ojs.ArticleSetting).filter(ojs.ArticleSetting.setting_name == 'pub-id::doi', ojs.ArticleSetting.setting_value == doi).one()
	except NoResultFound:
		return None

def get_article_by_id(session, doi):
	try:
		return session.query(ojs.Article).filter(ojs.Article.article_id == doi).one()
	except NoResultFound:
		return None

def get_article_by_id(session, article_id):
	try:
		return session.query(ojs.Article).filter(ojs.Article.article_id == article_id).one()
	except NoResultFound:
		return None

def get_article_by_pubid(session, pubid):
	try:
		return session.query(ojs.Article).join(ojs.ArticleSetting).filter(ojs.ArticleSetting.setting_name == 'pub-id::publisher-id', ojs.ArticleSetting.setting_value == pubid).one()
	except NoResultFound:
		return None

def get_all_article_settings(session, article_id):
	return session.query(ojs.ArticleSetting).filter(ojs.ArticleSetting.article_id == article_id)

def get_article_settings(session, article_id, setting_name):
	return session.query(ojs.ArticleSetting).filter(ojs.ArticleSetting.article_id == article_id, ojs.ArticleSetting.setting_name == setting_name).one()

def get_latest_articles(session, limit):
	return session.query(ojs.Article).join(ojs.PublishedArticle).filter(ojs.PublishedArticle.date_published != None).order_by(ojs.PublishedArticle.date_published.desc()).limit(limit)

def get_popular_articles(session, limit):
	return session.query(ojs.Article).join(ojs.PublishedArticle).order_by(ojs.PublishedArticle.date_published.desc()).limit(limit)

def get_section_setting(session, setting_name, section_id):
	return session.query(ojs.SectionSettings).filter(ojs.SectionSettings.section_id == section_id, ojs.SectionSettings.setting_name == setting_name).one()

def get_article_galley(session, galley_id):
	try:
		return session.query(ojs.ArticleGalley).filter(ojs.ArticleGalley.galley_id == galley_id).one()
	except NoResultFound:
		return None

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

def get_section(session, section_id):
	try:
		return session.query(ojs.Section).filter(ojs.Section.section_id == section_id).one()
	except NoResultFound:
		return None

def get_issues(session):
	return session.query(ojs.Issue).filter(ojs.Issue.date_published != None, or_(ojs.Issue.access_status == 0, ojs.Issue.access_status == 1, and_(ojs.Issue.access_status == 2, ojs.Issue.open_access_date<=date.today()))).order_by(desc(ojs.Issue.volume), desc(ojs.Issue.number))

def get_issue(session, volume_id, issue_id, ojs_id):
	try:
		return session.query(ojs.Issue).filter(ojs.Issue.volume == volume_id, ojs.Issue.number == issue_id, ojs.Issue.issue_id == ojs_id, or_(ojs.Issue.access_status == 0, ojs.Issue.access_status == 1, and_(ojs.Issue.access_status == 2, ojs.Issue.open_access_date<=date.today()))).one()
	except NoResultFound:
		return None

def get_issue_settings(session, issue_id):
	return session.query(ojs.IssueSettings).filter(ojs.IssueSettings.issue_id == issue_id)

def get_issue_articles(session, volume_id, issue_id, ojs_id):
	return session.query(ojs.Article).join(ojs.PublishedArticle).join(ojs.Issue).filter(ojs.PublishedArticle.date_published != None, ojs.Issue.volume == volume_id, ojs.Issue.number == issue_id, ojs.Issue.issue_id == ojs_id).order_by(ojs.Article.pages)

def get_issue_articles_by_section_id(session, ojs_id, section_id):
	return session.query(ojs.Article).join(ojs.PublishedArticle).join(ojs.Issue).filter(ojs.PublishedArticle.date_published != None, ojs.Issue.issue_id == ojs_id, ojs.Article.section_id == section_id).order_by(ojs.Article.pages)

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
		return session.query(ojs.Announcement).filter(or_(ojs.Announcement.date_expire >= date.today(), ojs.Announcement.date_expire == None)).order_by(desc(ojs.Announcement.date_posted)).first()
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
			'setting_type': 'seting',
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

def set_password(session, user_id, password):
	user = session.query(ojs.User).filter(ojs.User.user_id == user_id).one()
	print user.password
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

def get_user_settings(session, user_id):
	return session.query(ojs.UserSetting).filter(ojs.UserSetting.user_id == user_id)

def get_author_settings(session, author_id):
	return session.query(ojs.AuthorSetting).filter(ojs.AuthorSetting.author_id == author_id)

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
