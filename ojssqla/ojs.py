# coding: utf-8
from sqlalchemy import (
    BigInteger,
    Column,
    Date,
    DateTime,
    Float,
    Index,
    Integer,
    SmallInteger,
    String,
    Table,
    Text,
    ForeignKey,
    PrimaryKeyConstraint,
)
from sqlalchemy.dialects.mysql.base import BIT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, column_property


Base = declarative_base()
metadata = Base.metadata


class AccessKey(Base):

    __tablename__ = 'access_keys'
    __table_args__ = (
        Index('access_keys_hash', 'key_hash', 'user_id', 'context'),
    )

    access_key_id = Column(
        BigInteger,
        primary_key=True
    )
    context = Column(
        String(40),
        nullable=False
    )
    key_hash = Column(
        String(40),
        nullable=False
    )
    user_id = Column(
        BigInteger,
        nullable=False
    )
    assoc_id = Column(
        BigInteger
    )
    expiry_date = Column(
        DateTime,
        nullable=False
    )


class AnnouncementSettings(Base):

    __tablename__ = 'announcement_settings'
    __table_args__ = (
        Index(
            'announcement_settings_pkey',
            'announcement_id',
            'locale',
            'setting_name',
        ),
    )

    announcement_id = Column(
        BigInteger,
        nullable=False,
        primary_key=True,
    )
    locale = Column(
        String(5),
        nullable=False,
        server_default=u"''",
        primary_key=True,
    )
    setting_name = Column(
        String(255),
        nullable=False,
        primary_key=True,
    )
    setting_value = Column(
        Text
    )
    setting_type = Column(
        String(6),
        nullable=False,
    )


class AnnouncementTypeSettings(Base):

    __tablename__ = 'announcement_type_settings'
    __table_args__ = (
        Index(
            'announcement_type_settings_pkey',
            'type_id',
            'locale',
            'setting_name'
        ),
    )

    type_id = Column(
        BigInteger,
        nullable=False,
        primary_key=True,
    )
    locale = Column(
        String(5),
        nullable=False,
        server_default=u"''",
        primary_key=True,
    )
    setting_name = Column(
        String(255),
        nullable=False,
        primary_key=True
    )
    setting_value = Column(
        Text
    )
    setting_type = Column(
        String(6),
        nullable=False,
    )


class AnnouncementType(Base):

    __tablename__ = 'announcement_types'
    __table_args__ = (
        Index(
            'announcement_types_assoc',
            'assoc_type',
            'assoc_id',
        ),
    )

    type_id = Column(
        BigInteger,
        primary_key=True,
    )
    assoc_type = Column(
        SmallInteger,
    )
    assoc_id = Column(
        BigInteger,
        nullable=False,
    )


class Announcement(Base):
    __tablename__ = 'announcements'
    __table_args__ = (
        Index('announcements_assoc', 'assoc_type', 'assoc_id'),
    )

    announcement_id = Column(
        BigInteger,
        primary_key=True,
    )
    assoc_type = Column(
        SmallInteger,
    )
    assoc_id = Column(
        BigInteger,
        nullable=False,
    )
    type_id = Column(
        BigInteger,
    )
    date_expire = Column(
        DateTime,
    )
    date_posted = Column(
        DateTime,
        nullable=False,
    )


class ArticleComment(Base):

    __tablename__ = 'article_comments'

    comment_id = Column(
        BigInteger,
        primary_key=True,
    )
    comment_type = Column(
        BigInteger,
    )
    role_id = Column(
        BigInteger,
        nullable=False,
    )
    article_id = Column(
        BigInteger,
        nullable=False,
        index=True,
    )
    assoc_id = Column(
        BigInteger,
        nullable=False,
    )
    author_id = Column(
        BigInteger,
        nullable=False,
    )
    comment_title = Column(
        String(255),
        nullable=False,
    )
    comments = Column(
        Text,
    )
    date_posted = Column(
        DateTime,
    )
    date_modified = Column(
        DateTime,
    )
    viewable = Column(
        Integer,
    )


class ArticleEventLog(Base):

    __tablename__ = 'article_event_log'

    log_id = Column(
        BigInteger,
        primary_key=True
    )
    article_id = Column(
        BigInteger,
        ForeignKey('articles.article_id'),
        nullable=False,
        primary_key=True,
    )
    user_id = Column(
        BigInteger,
        nullable=False,
    )
    date_logged = Column(
        DateTime,
        nullable=False,
    )
    ip_address = Column(
        String(15),
        nullable=False,
    )
    log_level = Column(
        String(1),
    )
    event_type = Column(
        BigInteger,
    )
    assoc_type = Column(
        BigInteger,
    )
    assoc_id = Column(
        BigInteger,
    )
    message = Column(
        Text,
    )


class ArticleFile(Base):

    __tablename__ = 'article_files'

    file_id = Column(BigInteger, primary_key=True, nullable=False)
    revision = Column(BigInteger, primary_key=True, nullable=False)
    source_file_id = Column(BigInteger)
    source_revision = Column(BigInteger)
    article_id = Column(BigInteger, nullable=False, index=True)
    file_name = Column(String(90), nullable=False)
    file_type = Column(String(255), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    original_file_name = Column(String(127))
    file_stage = Column(BigInteger, nullable=False)
    viewable = Column(Integer)
    date_uploaded = Column(DateTime, nullable=False)
    date_modified = Column(DateTime, nullable=False)
    round = Column(Integer, nullable=False)
    assoc_id = Column(BigInteger)


t_article_galley_settings = Table(
    'article_galley_settings', metadata,
    Column('galley_id', BigInteger, nullable=False, index=True),
    Column('locale', String(5), nullable=False, server_default=u"''"),
    Column('setting_name', String(255), nullable=False),
    Column('setting_value', Text),
    Column('setting_type', String(6), nullable=False),
    Index('article_galley_settings_pkey', 'galley_id', 'locale', 'setting_name'),
    Index('article_galley_settings_name_value', 'setting_name', 'setting_value')
)


t_article_html_galley_images = Table(
    'article_html_galley_images', metadata,
    Column('galley_id', BigInteger, nullable=False),
    Column('file_id', BigInteger, nullable=False),
    Index('article_html_galley_images_pkey', 'galley_id', 'file_id')
)


class ArticleNote(Base):
    __tablename__ = 'article_notes'

    note_id = Column(BigInteger, primary_key=True)
    article_id = Column(BigInteger, nullable=False, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    date_created = Column(DateTime, nullable=False)
    date_modified = Column(DateTime, nullable=False)
    title = Column(String(255), nullable=False)
    note = Column(Text)
    file_id = Column(BigInteger, nullable=False, index=True)


class ArticleSearchKeywordList(Base):
    __tablename__ = 'article_search_keyword_list'

    keyword_id = Column(BigInteger, primary_key=True)
    keyword_text = Column(String(60), nullable=False, unique=True)


t_article_search_object_keywords = Table(
    'article_search_object_keywords', metadata,
    Column('object_id', BigInteger, nullable=False),
    Column('keyword_id', BigInteger, nullable=False, index=True),
    Column('pos', Integer, nullable=False),
    Index('article_search_object_keywords_pkey', 'object_id', 'pos')
)


class ArticleSearchObject(Base):
    __tablename__ = 'article_search_objects'

    object_id = Column(BigInteger, primary_key=True)
    article_id = Column(BigInteger, nullable=False)
    type = Column(Integer, nullable=False)
    assoc_id = Column(BigInteger)


class ArticleSupplementaryFile(Base):
    __tablename__ = 'article_supplementary_files'

    supp_id = Column(BigInteger, primary_key=True)
    file_id = Column(BigInteger, nullable=False, index=True)
    article_id = Column(BigInteger, nullable=False, index=True)
    type = Column(String(255))
    language = Column(String(10))
    remote_url = Column(String(255))
    date_created = Column(Date)
    show_reviewers = Column(Integer, server_default=u"'0'")
    date_submitted = Column(DateTime, nullable=False)
    seq = Column(Float(asdecimal=True), nullable=False, server_default=u"'0'")

    settings = relationship(
        "ArticleSuppFileSettings",
        backref="ArticleSupplementaryFile",
        lazy='subquery',
    )


class ArticleSuppFileSettings(Base):

    __tablename__ = 'article_supp_file_settings'

    supp_id = Column(BigInteger, ForeignKey(ArticleSupplementaryFile.supp_id), nullable=False, primary_key=True)
    locale = Column(String(5), nullable=False, server_default=u"''", primary_key=True)
    setting_name = Column(String(255), nullable=False, primary_key=True)
    setting_value = Column(Text)
    setting_type = Column(String(6), nullable=False)


class ArticleXmlGalley(Base):
    __tablename__ = 'article_xml_galleys'

    xml_galley_id = Column(BigInteger, primary_key=True)
    galley_id = Column(BigInteger, nullable=False)
    article_id = Column(BigInteger, nullable=False)
    label = Column(String(32), nullable=False)
    galley_type = Column(String(255), nullable=False)
    views = Column(Integer, nullable=False, server_default=u"'0'")


class Article(Base):
    __tablename__ = 'articles'

    article_id = Column(BigInteger, primary_key=True)
    locale = Column(String(5))
    user_id = Column(BigInteger, nullable=False, index=True)
    journal_id = Column(BigInteger, nullable=False, index=True)
    section_id = Column(ForeignKey('sections.section_id'), index=True, primary_key=True)
    language = Column(String(10), server_default=u"'en'")
    comments_to_ed = Column(Text)
    citations = Column(Text)
    date_submitted = Column(DateTime)
    last_modified = Column(DateTime)
    date_status_modified = Column(DateTime)
    status = Column(Integer, nullable=False, server_default=u"'1'")
    submission_progress = Column(Integer, nullable=False, server_default=u"'1'")
    current_round = Column(Integer, nullable=False, server_default=u"'1'")
    submission_file_id = Column(BigInteger)
    revised_file_id = Column(BigInteger)
    review_file_id = Column(BigInteger)
    editor_file_id = Column(BigInteger)
    pages = Column(String(255))
    fast_tracked = Column(Integer, nullable=False, server_default=u"'0'")
    hide_author = Column(Integer, nullable=False, server_default=u"'0'")
    comments_status = Column(Integer, nullable=False, server_default=u"'0'")

    published_article = relationship(
        "PublishedArticle",
        uselist=False,
        backref="article",
        lazy='joined',
    )

    settings = relationship(
        "ArticleSetting",
        backref="Article",
        lazy='subquery',
    )

    authors = relationship(
        "Author",
        backref="Article",
        lazy='subquery',
        order_by="Author.seq")

    galleys = relationship(
        "ArticleGalley",
        backref="Article",
        lazy='subquery',
        order_by="ArticleGalley.seq")

    taxonomies = relationship(
        "TaxonomyArticle",
        backref="Article",
        lazy='subquery',
    )

    decisions = relationship(
        "EditDecision",
        backref="Article",
        lazy='subquery',
    )


class Issue(Base):

    __tablename__ = 'issues'

    issue_id = Column(BigInteger, primary_key=True)
    journal_id = Column(BigInteger, nullable=False, index=True)
    volume = Column(SmallInteger)
    number = Column(String(10))
    year = Column(SmallInteger)
    published = Column(Integer, nullable=False, server_default=u"'0'")
    current = Column(Integer, nullable=False, server_default=u"'0'")
    date_published = Column(DateTime)
    date_notified = Column(DateTime)
    access_status = Column(Integer, nullable=False, server_default=u"'1'")
    open_access_date = Column(DateTime)
    show_volume = Column(Integer, nullable=False, server_default=u"'0'")
    show_number = Column(Integer, nullable=False, server_default=u"'0'")
    show_year = Column(Integer, nullable=False, server_default=u"'0'")
    show_title = Column(Integer, nullable=False, server_default=u"'0'")
    style_file_name = Column(String(90))
    original_style_file_name = Column(String(255))
    last_modified = Column(DateTime)

    galleys = relationship(
        "IssueGalley",
        backref="Issue",
        lazy='subquery',
        order_by="IssueGalley.seq")


class PublishedArticle(Base):

    __tablename__ = 'published_articles'

    published_article_id = Column(
        BigInteger,
        primary_key=True
    )
    article_id = Column(  # Lying to SQLAlchemy. no fkey exists.
        BigInteger,
        ForeignKey(Article.article_id),
        nullable=False,
        unique=True,
    )
    issue_id = Column(
        BigInteger,
        ForeignKey(Issue.issue_id),
        nullable=False,
        index=True,
    )
    date_published = Column(
        DateTime,
    )
    seq = Column(
        Float(asdecimal=True),
        nullable=False,
        server_default=u"'0'",
    )
    access_status = Column(
        Integer,
        nullable=False,
        server_default=u"'0'",
    )
    issue = relationship(
        "Issue",
        uselist=False,
        backref="Issue",
        lazy='joined',
    )


class ArticleSetting(Base):
    __tablename__ = 'article_settings'

    article_id = Column(BigInteger, ForeignKey(Article.article_id), nullable=False, primary_key=True)
    locale = Column(String(5), nullable=False, server_default=u"''", primary_key=True)
    setting_name = Column(String(255), nullable=False, primary_key=True)
    setting_value = Column(Text)
    setting_type = Column(String(6), nullable=False)

class ArticleGalley(Base):
    __tablename__ = 'article_galleys'

    galley_id = Column(BigInteger, primary_key=True)
    locale = Column(String(5))
    article_id = Column(BigInteger, ForeignKey(Article.article_id), nullable=False, index=True)
    file_id = Column(BigInteger, ForeignKey(ArticleFile.file_id), nullable=False)
    label = Column(String(32))
    html_galley = Column(Integer, nullable=False, server_default=u"'0'")
    style_file_id = Column(BigInteger)
    seq = Column(Float(asdecimal=True), nullable=False, server_default=u"'0'")
    remote_url = Column(String(255))

    issue = relationship(
        "ArticleFile",
        uselist=False,
        backref="ArticleFile",
        lazy='subquery',
    )


class AuthSource(Base):
    __tablename__ = 'auth_sources'

    auth_id = Column(BigInteger, primary_key=True)
    title = Column(String(60), nullable=False)
    plugin = Column(String(32), nullable=False)
    auth_default = Column(Integer, nullable=False, server_default=u"'0'")
    settings = Column(Text)


class AuthorSetting(Base):
    __tablename__ = 'author_settings'

    author_id = Column(BigInteger, nullable=False, index=True, primary_key=True)
    locale = Column(String(5), nullable=False, server_default=u"''", primary_key=True)
    setting_name = Column(String(255), nullable=False, primary_key=True)
    setting_value = Column(Text)
    setting_type = Column(String(6), nullable=False)


class Author(Base):
    __tablename__ = 'authors'

    author_id = Column(BigInteger, primary_key=True)
    submission_id = Column(BigInteger, ForeignKey(Article.article_id), nullable=False, index=True)
    primary_contact = Column(Integer, nullable=False, server_default=u"'0'")
    seq = Column(Float(asdecimal=True), nullable=False, server_default=u"'0'")
    first_name = Column(String(40), nullable=False)
    middle_name = Column(String(40))
    last_name = Column(String(90), nullable=False)
    country = Column(String(90))
    email = Column(String(90), nullable=False)
    url = Column(String(255))
    user_group_id = Column(BigInteger)
    suffix = Column(String(40))

    fullname = column_property(first_name + ' ' + last_name)

class Licenses(Base):
    __tablename__ = 'licenses'

    id = Column(BigInteger, primary_key=True)
    name = Column(String(200))
    pretty_name = Column(String(200))
    enabled = Column(SmallInteger)


class BooksForReview(Base):
    __tablename__ = 'books_for_review'

    book_id = Column(BigInteger, primary_key=True, index=True)
    journal_id = Column(BigInteger, nullable=False)
    status = Column(SmallInteger, nullable=False)
    author_type = Column(SmallInteger, nullable=False)
    publisher = Column(String(255), nullable=False)
    year = Column(SmallInteger, nullable=False)
    language = Column(String(10), nullable=False, server_default=u"'en'")
    copy = Column(Integer, nullable=False, server_default=u"'0'")
    url = Column(String(255))
    edition = Column(Integer)
    pages = Column(SmallInteger)
    isbn = Column(String(30))
    date_created = Column(DateTime, nullable=False)
    date_requested = Column(DateTime)
    date_assigned = Column(DateTime)
    date_mailed = Column(DateTime)
    date_due = Column(DateTime)
    date_submitted = Column(DateTime)
    user_id = Column(BigInteger)
    editor_id = Column(BigInteger)
    article_id = Column(BigInteger)
    notes = Column(Text)


class BooksForReviewAuthor(Base):
    __tablename__ = 'books_for_review_authors'

    author_id = Column(BigInteger, primary_key=True)
    book_id = Column(BigInteger, nullable=False, index=True)
    seq = Column(Float(asdecimal=True), nullable=False, server_default=u"'0'")
    first_name = Column(String(40), nullable=False)
    middle_name = Column(String(40))
    last_name = Column(String(90), nullable=False)


t_books_for_review_settings = Table(
    'books_for_review_settings', metadata,
    Column('book_id', BigInteger, nullable=False, index=True),
    Column('locale', String(5), nullable=False, server_default=u"''"),
    Column('setting_name', String(255), nullable=False),
    Column('setting_value', Text),
    Column('setting_type', String(6), nullable=False),
    Index('bfr_settings_pkey', 'book_id', 'locale', 'setting_name')
)


class Captcha(Base):
    __tablename__ = 'captchas'

    captcha_id = Column(BigInteger, primary_key=True)
    session_id = Column(String(40), nullable=False)
    value = Column(String(20), nullable=False)
    date_created = Column(DateTime, nullable=False)


t_citation_settings = Table(
    'citation_settings', metadata,
    Column('citation_id', BigInteger, nullable=False, index=True),
    Column('locale', String(5), nullable=False, server_default=u"''"),
    Column('setting_name', String(255), nullable=False),
    Column('setting_value', Text),
    Column('setting_type', String(6), nullable=False),
    Index('citation_settings_pkey', 'citation_id', 'locale', 'setting_name')
)


class Citation(Base):
    __tablename__ = 'citations'
    __table_args__ = (
        Index('citations_assoc', 'assoc_type', 'assoc_id'),
        Index('citations_assoc_seq', 'assoc_type', 'assoc_id', 'seq')
    )

    citation_id = Column(BigInteger, primary_key=True)
    assoc_type = Column(BigInteger, nullable=False, server_default=u"'0'")
    assoc_id = Column(BigInteger, nullable=False, server_default=u"'0'")
    citation_state = Column(BigInteger, nullable=False)
    raw_citation = Column(Text)
    seq = Column(BigInteger, nullable=False, server_default=u"'0'")
    lock_id = Column(String(23))


class Collection(Base):
    __tablename__ = 'collection'

    id = Column(BigInteger, primary_key=True)
    name = Column(String(150), nullable=False)
    abbrev = Column(String(150), nullable=False)
    short_description = Column(Text)
    description = Column(Text, nullable=False)
    image_filename = Column(String(150))
    date_published = Column(Date, nullable=False)
    date_updated = Column(Date)
    tba = Column(BIT(1))
    disabled = Column(BIT(1))
    discussions = Column(Integer)

    users = relationship(u'CollectionUser', primaryjoin='Collection.id == CollectionUser.collection_id', order_by='CollectionUser.order')
    articles = relationship(u'CollectionArticle', primaryjoin='Collection.id == CollectionArticle.collection_id', order_by='CollectionArticle.order')


class CollectionArticle(Base):
    __tablename__ = 'collection_article'

    collection_id = Column(ForeignKey('collection.id', deferrable=True, initially=u'DEFERRED'), primary_key=True, nullable=False)
    published_article_id = Column(BigInteger, primary_key=True, nullable=False)
    order = Column(Integer, nullable=True)

    __mapper_args__ = {
        "order_by": order
    }


class CollectionUser(Base):
    __tablename__ = 'collection_user'

    collection_id = Column(ForeignKey('collection.id', deferrable=True, initially=u'DEFERRED'), primary_key=True, nullable=False)
    user_id = Column(BigInteger, primary_key=True, nullable=False)
    role_name = Column(String(50), nullable=False, server_default=u"'editor'")
    order = Column(Integer, nullable=True)

    __mapper_args__ = {
        "order_by": order
    }


class Comment(Base):
    __tablename__ = 'comments'

    comment_id = Column(BigInteger, primary_key=True)
    submission_id = Column(BigInteger, nullable=False, index=True)
    parent_comment_id = Column(BigInteger, index=True)
    num_children = Column(Integer, nullable=False, server_default=u"'0'")
    user_id = Column(BigInteger, index=True)
    poster_ip = Column(String(15), nullable=False)
    poster_name = Column(String(90))
    poster_email = Column(String(90))
    title = Column(String(255), nullable=False)
    body = Column(Text)
    date_posted = Column(DateTime)
    date_modified = Column(DateTime)


class CompletedPayment(Base):
    __tablename__ = 'completed_payments'

    completed_payment_id = Column(BigInteger, primary_key=True)
    timestamp = Column(DateTime, nullable=False)
    payment_type = Column(BigInteger, nullable=False)
    journal_id = Column(BigInteger, nullable=False)
    user_id = Column(BigInteger)
    assoc_id = Column(BigInteger)
    amount = Column(Float(asdecimal=True), nullable=False)
    currency_code_alpha = Column(String(3))
    payment_method_plugin_name = Column(String(80))


class ControlledVocabEntry(Base):
    __tablename__ = 'controlled_vocab_entries'
    __table_args__ = (
        Index('controlled_vocab_entries_cv_id', 'controlled_vocab_id', 'seq'),
    )

    controlled_vocab_entry_id = Column(BigInteger, primary_key=True)
    controlled_vocab_id = Column(BigInteger, nullable=False)
    seq = Column(Float(asdecimal=True))

    settings = relationship(
        u'ControlledVocabEntrySettings', 
        primaryjoin='ControlledVocabEntry.controlled_vocab_entry_id == ControlledVocabEntrySettings.controlled_vocab_entry_id',
        backref=backref('controlled_vocab_entry_settings', cascade="all, delete")
    )


class ControlledVocabEntrySettings(Base):
    __tablename__ = 'controlled_vocab_entry_settings'

    controlled_vocab_entry_id = Column(ForeignKey(ControlledVocabEntry.controlled_vocab_entry_id, deferrable=True, initially=u'DEFERRED'), nullable=False, primary_key=True)
    locale = Column(String(5), nullable=False, server_default=u"''")
    setting_name = Column(String(255), nullable=False)
    setting_value = Column(String(255), nullable=False)
    setting_type = Column(String(6), nullable=False)

'''
t_controlled_vocab_entry_settings = Table(
    'controlled_vocab_entry_settings', metadata,
    Column('controlled_vocab_entry_id', BigInteger, nullable=False, index=True),
    Column('locale', String(5), nullable=False, server_default=u"''"),
    Column('setting_name', String(255), nullable=False),
    Column('setting_value', Text),
    Column('setting_type', String(6), nullable=False),
    Index('c_v_e_s_pkey', 'controlled_vocab_entry_id', 'locale', 'setting_name')
)
'''


class ControlledVocab(Base):
    __tablename__ = 'controlled_vocabs'
    __table_args__ = (
        Index('controlled_vocab_symbolic', 'symbolic', 'assoc_type', 'assoc_id'),
    )

    controlled_vocab_id = Column(BigInteger, primary_key=True)
    symbolic = Column(String(64), nullable=False)
    assoc_type = Column(BigInteger, nullable=False, server_default=u"'0'")
    assoc_id = Column(BigInteger, nullable=False, server_default=u"'0'")


class CustomIssueOrder(Base):
    __tablename__ = 'custom_issue_orders'

    issue_id = Column(ForeignKey('issue.issue_id'), nullable=False, unique=True, primary_key=True)
    journal_id = Column(BigInteger, nullable=False, primary_key=True)
    seq = Column(Float(asdecimal=True), nullable=False, server_default=u"'0'")


class CustomSectionOrders(Base):
    __tablename__ = 'custom_section_orders'
    issue_id = Column(BigInteger, nullable=False, primary_key=True)
    section_id = Column(BigInteger, nullable=False, primary_key=True)
    seq = Column(Float(asdecimal=True), nullable=False, server_default=u"'0'")


class DataObjectTombstoneOaiSetObject(Base):
    __tablename__ = 'data_object_tombstone_oai_set_objects'

    object_id = Column(BigInteger, primary_key=True)
    tombstone_id = Column(BigInteger, nullable=False, index=True)
    assoc_type = Column(BigInteger, nullable=False)
    assoc_id = Column(BigInteger, nullable=False)


t_data_object_tombstone_settings = Table(
    'data_object_tombstone_settings', metadata,
    Column('tombstone_id', BigInteger, nullable=False, index=True),
    Column('locale', String(5), nullable=False, server_default=u"''"),
    Column('setting_name', String(255), nullable=False),
    Column('setting_value', Text),
    Column('setting_type', String(6), nullable=False),
    Index('data_object_tombstone_settings_pkey', 'tombstone_id', 'locale', 'setting_name')
)


class DataObjectTombstone(Base):
    __tablename__ = 'data_object_tombstones'

    tombstone_id = Column(BigInteger, primary_key=True)
    data_object_id = Column(BigInteger, nullable=False, index=True)
    date_deleted = Column(DateTime, nullable=False)
    set_spec = Column(String(255), nullable=False)
    set_name = Column(String(255), nullable=False)
    oai_identifier = Column(String(255), nullable=False)


class EditAssignment(Base):
    __tablename__ = 'edit_assignments'

    edit_id = Column(BigInteger, primary_key=True)
    article_id = Column(BigInteger, nullable=False, index=True)
    editor_id = Column(ForeignKey('users.user_id'), nullable=False, index=True)
    can_edit = Column(Integer, nullable=False, server_default=u"'1'")
    can_review = Column(Integer, nullable=False, server_default=u"'1'")
    date_assigned = Column(DateTime)
    date_notified = Column(DateTime)
    date_underway = Column(DateTime)

    editor = relationship(
        "User",
        uselist=False,
        backref="User",
        lazy='subquery',
        primaryjoin='EditAssignment.editor_id == User.user_id')


class EditDecision(Base):
    __tablename__ = 'edit_decisions'

    edit_decision_id = Column(BigInteger, primary_key=True)
    article_id = Column(BigInteger, ForeignKey(Article.article_id), nullable=False, unique=True)
    round = Column(Integer, nullable=False)
    editor_id = Column(BigInteger, nullable=False, index=True)
    decision = Column(Integer, nullable=False)
    date_decided = Column(DateTime, nullable=False)


class EmailLog(Base):
    __tablename__ = 'email_log'
    __table_args__ = (
        Index('email_log_assoc', 'assoc_type', 'assoc_id'),
    )

    log_id = Column(BigInteger, primary_key=True)
    sender_id = Column(BigInteger, nullable=False)
    date_sent = Column(DateTime, nullable=False)
    ip_address = Column(String(39))
    event_type = Column(BigInteger)
    assoc_type = Column(BigInteger)
    assoc_id = Column(BigInteger)
    from_address = Column(String(255))
    recipients = Column(Text)
    cc_recipients = Column(Text)
    bcc_recipients = Column(Text)
    subject = Column(String(255))
    body = Column(Text)


t_email_log_users = Table(
    'email_log_users', metadata,
    Column('email_log_id', BigInteger, nullable=False),
    Column('user_id', BigInteger, nullable=False),
    Index('email_log_user_id', 'email_log_id', 'user_id')
)


class EmailTemplate(Base):
    __tablename__ = 'email_templates'
    __table_args__ = (
        Index('email_templates_email_key', 'email_key', 'assoc_type', 'assoc_id'),
        Index('email_templates_assoc', 'assoc_type', 'assoc_id')
    )

    email_id = Column(BigInteger, primary_key=True)
    email_key = Column(String(64), nullable=False)
    assoc_type = Column(BigInteger, server_default=u"'0'")
    assoc_id = Column(BigInteger, server_default=u"'0'")
    enabled = Column(Integer, nullable=False, server_default=u"'1'")


class EmailTemplateData(Base):
    __tablename__ = 'email_templates_data'
    __table_args__ = (Index('email_templates_data_pkey', 'email_key', 'locale', 'assoc_type', 'assoc_id'),)
    email_key = Column(String(64), nullable=False, primary_key=True)
    locale = Column(String(5), nullable=False, server_default=u"'en_US'")
    assoc_type = Column(BigInteger, primary_key=True)
    assoc_id = Column(BigInteger, primary_key=True)
    subject = Column(String(120), nullable=False)
    body = Column(Text)


class EmailTemplatesDefault(Base):
    __tablename__ = 'email_templates_default'

    email_id = Column(BigInteger, primary_key=True)
    email_key = Column(String(64), nullable=False, index=True)
    can_disable = Column(Integer, nullable=False, server_default=u"'1'")
    can_edit = Column(Integer, nullable=False, server_default=u"'1'")
    from_role_id = Column(BigInteger)
    to_role_id = Column(BigInteger)

class EmailTemplatesDefaultData(Base):
    __tablename__ = 'email_templates_default_data'
    __table_args__ = (
        Index('email_templates_default_data_pkey', 'email_key', 'locale'),
        PrimaryKeyConstraint('email_key', 'locale')
    )

    email_key = Column(String(64), nullable=False, index=True)
    locale = Column(String(5), nullable=False, server_default=u"'en_US'")
    subject = Column(String(120), nullable=False)
    body = Column(Text)
    description = Column(Text)


class EventLog(Base):
    __tablename__ = 'event_log'
    __table_args__ = (
        Index('event_log_assoc', 'assoc_type', 'assoc_id'),
    )

    log_id = Column(BigInteger, primary_key=True)
    assoc_type = Column(BigInteger)
    assoc_id = Column(BigInteger)
    user_id = Column(BigInteger, nullable=False)
    date_logged = Column(DateTime, nullable=False)
    ip_address = Column(String(39), nullable=False)
    event_type = Column(BigInteger)
    message = Column(Text)
    is_translated = Column(Integer)


class EventLogSettings(Base):
    __tablename__ = 'event_log_settings'
    __table_args__ = (
        Index('log_id', 'setting_name'),
    )

    log_id = Column(BigInteger, nullable=False, primary_key=True)
    setting_name = Column(String(255), nullable=False, primary_key=True)
    setting_value = Column(Text)
    setting_type = Column(String(6), nullable=False)


t_external_feed_settings = Table(
    'external_feed_settings', metadata,
    Column('feed_id', BigInteger, nullable=False),
    Column('locale', String(5), nullable=False, server_default=u"''"),
    Column('setting_name', String(255), nullable=False),
    Column('setting_value', Text),
    Column('setting_type', String(6), nullable=False),
    Index('external_feed_settings_pkey', 'feed_id', 'locale', 'setting_name')
)


class ExternalFeed(Base):
    __tablename__ = 'external_feeds'

    feed_id = Column(BigInteger, primary_key=True)
    journal_id = Column(BigInteger, nullable=False, index=True)
    url = Column(String(255), nullable=False)
    seq = Column(Float(asdecimal=True), nullable=False, server_default=u"'0'")
    display_homepage = Column(Integer, nullable=False, server_default=u"'0'")
    display_block = Column(SmallInteger, nullable=False, server_default=u"'0'")
    limit_items = Column(Integer, server_default=u"'0'")
    recent_items = Column(SmallInteger)


class FilterGroup(Base):
    __tablename__ = 'filter_groups'

    filter_group_id = Column(BigInteger, primary_key=True)
    symbolic = Column(String(255), unique=True)
    display_name = Column(String(255))
    description = Column(String(255))
    input_type = Column(String(255))
    output_type = Column(String(255))


t_filter_settings = Table(
    'filter_settings', metadata,
    Column('filter_id', BigInteger, nullable=False, index=True),
    Column('locale', String(5), nullable=False, server_default=u"''"),
    Column('setting_name', String(255), nullable=False),
    Column('setting_value', Text),
    Column('setting_type', String(6), nullable=False),
    Index('filter_settings_pkey', 'filter_id', 'locale', 'setting_name')
)


class Filter(Base):
    __tablename__ = 'filters'

    filter_id = Column(BigInteger, primary_key=True)
    context_id = Column(BigInteger, nullable=False, server_default=u"'0'")
    display_name = Column(String(255))
    class_name = Column(String(255))
    is_template = Column(Integer, nullable=False, server_default=u"'0'")
    parent_filter_id = Column(BigInteger, nullable=False, server_default=u"'0'")
    seq = Column(BigInteger, nullable=False, server_default=u"'0'")
    filter_group_id = Column(BigInteger, nullable=False, server_default=u"'0'")


class Gift(Base):
    __tablename__ = 'gifts'
    __table_args__ = (
        Index('gifts_assoc', 'assoc_type', 'assoc_id'),
    )

    gift_id = Column(BigInteger, primary_key=True)
    assoc_type = Column(SmallInteger, nullable=False)
    assoc_id = Column(BigInteger, nullable=False)
    status = Column(Integer, nullable=False)
    gift_type = Column(SmallInteger, nullable=False)
    gift_assoc_id = Column(BigInteger, nullable=False)
    buyer_first_name = Column(String(40), nullable=False)
    buyer_middle_name = Column(String(40))
    buyer_last_name = Column(String(90), nullable=False)
    buyer_email = Column(String(90), nullable=False)
    buyer_user_id = Column(BigInteger)
    recipient_first_name = Column(String(40), nullable=False)
    recipient_middle_name = Column(String(40))
    recipient_last_name = Column(String(90), nullable=False)
    recipient_email = Column(String(90), nullable=False)
    recipient_user_id = Column(BigInteger)
    date_redeemed = Column(DateTime)
    locale = Column(String(5), nullable=False, server_default=u"''")
    gift_note_title = Column(String(90))
    gift_note = Column(Text)
    notes = Column(Text)


class GroupSettings(Base):
    __tablename__ = 'group_settings'
    __table_args__ = (
        Index('group_settings_pkey', 'group_id', 'locale', 'setting_name'),
    )
    group_id = Column(BigInteger, nullable=False, index=True, primary_key=True)
    locale = Column(String(5), nullable=False, server_default=u"''", primary_key=True)
    setting_name = Column(String(255), nullable=False, primary_key=True)
    setting_value = Column(Text)
    setting_type = Column(String(6), nullable=False)


class Group(Base):
    __tablename__ = 'groups'
    __table_args__ = (
        Index('groups_assoc', 'assoc_type', 'assoc_id'),
    )

    group_id = Column(BigInteger, primary_key=True)
    assoc_type = Column(SmallInteger)
    publish_email = Column(SmallInteger)
    assoc_id = Column(BigInteger)
    context = Column(BigInteger)
    about_displayed = Column(Integer, nullable=False, server_default=u"'0'")
    seq = Column(Float(asdecimal=True), nullable=False, server_default=u"'0'")


class InstitutionalSubscriptionIp(Base):
    __tablename__ = 'institutional_subscription_ip'

    institutional_subscription_ip_id = Column(BigInteger, primary_key=True)
    subscription_id = Column(BigInteger, nullable=False, index=True)
    ip_string = Column(String(40), nullable=False)
    ip_start = Column(BigInteger, nullable=False, index=True)
    ip_end = Column(BigInteger, index=True)


class InstitutionalSubscription(Base):
    __tablename__ = 'institutional_subscriptions'

    institutional_subscription_id = Column(BigInteger, primary_key=True)
    subscription_id = Column(BigInteger, nullable=False, index=True)
    institution_name = Column(String(255), nullable=False)
    mailing_address = Column(String(255))
    domain = Column(String(255), index=True)


class IssueFile(Base):
    __tablename__ = 'issue_files'

    file_id = Column(BigInteger, primary_key=True)
    issue_id = Column(BigInteger, nullable=False, index=True)
    file_name = Column(String(90), nullable=False)
    file_type = Column(String(255), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    content_type = Column(BigInteger, nullable=False)
    original_file_name = Column(String(127))
    date_uploaded = Column(DateTime, nullable=False)
    date_modified = Column(DateTime, nullable=False)


t_issue_galley_settings = Table(
    'issue_galley_settings', metadata,
    Column('galley_id', BigInteger, nullable=False, index=True),
    Column('locale', String(5), nullable=False, server_default=u"''"),
    Column('setting_name', String(255), nullable=False),
    Column('setting_value', Text),
    Column('setting_type', String(6), nullable=False),
    Index('issue_galley_settings_pkey', 'galley_id', 'locale', 'setting_name')
)


class IssueGalley(Base):
    __tablename__ = 'issue_galleys'

    galley_id = Column(BigInteger, primary_key=True)
    locale = Column(String(5))
    issue_id = Column(BigInteger, ForeignKey(Issue.issue_id), nullable=False, index=True)
    file_id = Column(BigInteger, nullable=False)
    label = Column(String(32))
    seq = Column(Float(asdecimal=True), nullable=False, server_default=u"'0'")


class IssueSettings(Base):
    __tablename__ = 'issue_settings'

    issue_id = Column(BigInteger, nullable=False, index=True, primary_key=True)
    locale = Column(String(5), nullable=False, primary_key=True)
    setting_name = Column(String(255), nullable=False, primary_key=True)
    setting_value = Column(Text)
    setting_type = Column(String(6), nullable=False)


class JournalSetting(Base):
    __tablename__ = 'journal_settings'

    journal_id = Column(BigInteger, nullable=False, primary_key=True)
    locale = Column(String(5), nullable=False, server_default=u"''", primary_key=True)
    setting_name = Column(String(255), nullable=False, primary_key=True)
    setting_value = Column(Text)
    setting_type = Column(String(6), nullable=False)


class Journal(Base):
    __tablename__ = 'journals'

    journal_id = Column(BigInteger, primary_key=True)
    path = Column(String(32), nullable=False, unique=True)
    seq = Column(Float(asdecimal=True), nullable=False, server_default=u"'0'")
    primary_locale = Column(String(5), nullable=False)
    enabled = Column(Integer, nullable=False, server_default=u"'1'")


t_metadata_description_settings = Table(
    'metadata_description_settings', metadata,
    Column('metadata_description_id', BigInteger, nullable=False, index=True),
    Column('locale', String(5), nullable=False, server_default=u"''"),
    Column('setting_name', String(255), nullable=False),
    Column('setting_value', Text),
    Column('setting_type', String(6), nullable=False),
    Index('metadata_descripton_settings_pkey', 'metadata_description_id', 'locale', 'setting_name')
)


class MetadataDescription(Base):
    __tablename__ = 'metadata_descriptions'
    __table_args__ = (
        Index('metadata_descriptions_assoc', 'assoc_type', 'assoc_id'),
    )

    metadata_description_id = Column(BigInteger, primary_key=True)
    assoc_type = Column(BigInteger, nullable=False, server_default=u"'0'")
    assoc_id = Column(BigInteger, nullable=False, server_default=u"'0'")
    schema_namespace = Column(String(255), nullable=False)
    schema_name = Column(String(255), nullable=False)
    display_name = Column(String(255))
    seq = Column(BigInteger, nullable=False, server_default=u"'0'")


class Metrics(Base):
    __tablename__ = 'metrics'
    load_id = Column(String(255), nullable=False, index=True)
    assoc_type = Column(BigInteger, nullable=False, primary_key=True)
    context_id = Column(BigInteger, nullable=False)
    issue_id = Column(BigInteger)
    submission_id = Column(BigInteger, primary_key=True)
    assoc_id = Column(BigInteger, nullable=False, primary_key=True)
    day = Column(String(8))
    month = Column(String(6))
    file_type = Column(Integer)
    country_id = Column(String(2))
    region = Column(SmallInteger)
    city = Column(String(255))
    metric_type = Column(String(255), nullable=False, index=True)
    metric = Column(Integer)


class Mutex(Base):
    __tablename__ = 'mutex'

    i = Column(Integer, primary_key=True)


class Note(Base):
    __tablename__ = 'notes'
    __table_args__ = (
        Index('notes_assoc', 'assoc_type', 'assoc_id'),
    )

    note_id = Column(BigInteger, primary_key=True)
    assoc_type = Column(BigInteger)
    assoc_id = Column(BigInteger)
    user_id = Column(BigInteger, nullable=False)
    date_created = Column(DateTime, nullable=False)
    date_modified = Column(DateTime)
    title = Column(String(255))
    file_id = Column(BigInteger)
    contents = Column(Text)


class NotificationMailList(Base):
    __tablename__ = 'notification_mail_list'
    __table_args__ = (
        Index('notification_mail_list_email_context', 'email', 'context'),
    )

    notification_mail_list_id = Column(BigInteger, primary_key=True)
    email = Column(String(90), nullable=False)
    confirmed = Column(Integer, nullable=False, server_default=u"'0'")
    token = Column(String(40), nullable=False)
    context = Column(BigInteger, nullable=False)


t_notification_settings = Table(
    'notification_settings', metadata,
    Column('notification_id', BigInteger, nullable=False),
    Column('locale', String(5)),
    Column('setting_name', String(64), nullable=False),
    Column('setting_value', Text),
    Column('setting_type', String(6), nullable=False),
    Index('notification_settings_pkey', 'notification_id', 'locale', 'setting_name')
)


class NotificationSubscriptionSetting(Base):
    __tablename__ = 'notification_subscription_settings'

    setting_id = Column(BigInteger, primary_key=True)
    setting_name = Column(String(64), nullable=False)
    setting_value = Column(Text)
    user_id = Column(BigInteger, nullable=False)
    context = Column(BigInteger, nullable=False)
    setting_type = Column(String(6), nullable=False)


class Notification(Base):
    __tablename__ = 'notifications'
    __table_args__ = (
        Index('notifications_context_id_user_id', 'context_id', 'user_id', 'level'),
        Index('notifications_assoc', 'assoc_type', 'assoc_id'),
        Index('notifications_context_id', 'context_id', 'level')
    )

    notification_id = Column(BigInteger, primary_key=True)
    context_id = Column(BigInteger, nullable=False)
    user_id = Column(BigInteger)
    level = Column(BigInteger, nullable=False)
    type = Column(BigInteger, nullable=False)
    date_created = Column(DateTime, nullable=False)
    date_read = Column(DateTime)
    assoc_type = Column(BigInteger)
    assoc_id = Column(BigInteger)


t_oai_resumption_tokens = Table(
    'oai_resumption_tokens', metadata,
    Column('token', String(32), nullable=False, unique=True),
    Column('expire', BigInteger, nullable=False),
    Column('record_offset', Integer, nullable=False),
    Column('params', Text)
)


class PaypalTransaction(Base):
    __tablename__ = 'paypal_transactions'

    txn_id = Column(String(17), primary_key=True)
    txn_type = Column(String(20))
    payer_email = Column(String(127))
    receiver_email = Column(String(127))
    item_number = Column(String(127))
    payment_date = Column(String(127))
    payer_id = Column(String(13))
    receiver_id = Column(String(13))


t_plugin_settings = Table(
    'plugin_settings', metadata,
    Column('plugin_name', String(80), nullable=False, index=True),
    Column('locale', String(5), nullable=False, server_default=u"''"),
    Column('journal_id', BigInteger, nullable=False),
    Column('setting_name', String(80), nullable=False),
    Column('setting_value', Text),
    Column('setting_type', String(6), nullable=False),
    Index('plugin_settings_pkey', 'plugin_name', 'locale', 'journal_id', 'setting_name')
)


t_processes = Table(
    'processes', metadata,
    Column('process_id', String(23), nullable=False, unique=True),
    Column('process_type', Integer, nullable=False),
    Column('time_started', BigInteger, nullable=False),
    Column('obliterated', Integer, nullable=False, server_default=u"'0'")
)




class QueuedPayment(Base):
    __tablename__ = 'queued_payments'

    queued_payment_id = Column(BigInteger, primary_key=True)
    date_created = Column(DateTime, nullable=False)
    date_modified = Column(DateTime, nullable=False)
    expiry_date = Column(Date)
    payment_data = Column(Text)


t_referral_settings = Table(
    'referral_settings', metadata,
    Column('referral_id', BigInteger, nullable=False, index=True),
    Column('locale', String(5), nullable=False, server_default=u"''"),
    Column('setting_name', String(255), nullable=False),
    Column('setting_value', Text),
    Column('setting_type', String(6), nullable=False),
    Index('referral_settings_pkey', 'referral_id', 'locale', 'setting_name')
)


class Referral(Base):
    __tablename__ = 'referrals'
    __table_args__ = (
        Index('referral_article_id', 'article_id', 'url'),
    )

    referral_id = Column(BigInteger, primary_key=True)
    article_id = Column(BigInteger, nullable=False)
    status = Column(SmallInteger, nullable=False)
    url = Column(String(255), nullable=False)
    date_added = Column(DateTime, nullable=False)
    link_count = Column(BigInteger, nullable=False)


class ReviewAssignment(Base):
    __tablename__ = 'review_assignments'

    review_id = Column(BigInteger, primary_key=True)
    submission_id = Column(BigInteger, nullable=False, index=True)
    reviewer_id = Column(ForeignKey('users.user_id'), nullable=False, index=True, primary_key=True)
    competing_interests = Column(Text)
    regret_message = Column(Text)
    recommendation = Column(Integer)
    date_assigned = Column(DateTime)
    date_notified = Column(DateTime)
    date_confirmed = Column(DateTime)
    date_completed = Column(DateTime)
    date_acknowledged = Column(DateTime)
    date_due = Column(DateTime)
    date_response_due = Column(DateTime)
    last_modified = Column(DateTime)
    reminder_was_automatic = Column(Integer, nullable=False, server_default=u"'0'")
    declined = Column(Integer, nullable=False, server_default=u"'0'")
    replaced = Column(Integer, nullable=False, server_default=u"'0'")
    cancelled = Column(Integer, nullable=False, server_default=u"'0'")
    reviewer_file_id = Column(BigInteger)
    date_rated = Column(DateTime)
    date_reminded = Column(DateTime)
    quality = Column(Integer)
    review_method = Column(Integer, nullable=False, server_default=u"'1'")
    round = Column(Integer, nullable=False, server_default=u"'1'")
    step = Column(Integer, nullable=False, server_default=u"'1'")
    review_form_id = Column(BigInteger, index=True)
    review_round_id = Column(BigInteger)
    stage_id = Column(Integer, nullable=False, server_default=u"'1'")
    unconsidered = Column(Integer)

    reviewer = relationship(
        "User",
        primaryjoin='ReviewAssignment.reviewer_id == User.user_id',
        uselist=False,
        lazy='subquery',
    )


class ReviewFormElementSettings(Base):
    __tablename__ = 'review_form_element_settings'
    __table_args__ = (
        Index('review_form_element_settings_pkey', 'review_form_element_id', 'locale', 'setting_name'),
    )

    review_form_element_id = Column(BigInteger, nullable=False, index=True, primary_key=True)
    locale = Column(String(5), nullable=False, server_default=u"''", primary_key=True)
    setting_name = Column(String(255), nullable=False, primary_key=True)
    setting_value = Column(Text)
    setting_type = Column(String(6), nullable=False)


class ReviewFormElement(Base):
    __tablename__ = 'review_form_elements'

    review_form_element_id = Column(BigInteger, primary_key=True)
    review_form_id = Column(BigInteger, nullable=False, index=True)
    seq = Column(Float(asdecimal=True))
    element_type = Column(BigInteger)
    required = Column(Integer)
    included = Column(Integer)


class ReviewFormResponses(Base):
    __tablename__ = 'review_form_responses'
    __table_args__ = (
       Index('review_form_responses_pkey', 'review_form_element_id', 'review_id'),
    )

    review_form_element_id = Column(ForeignKey('review_form_elements.review_form_element_id'), nullable=False, primary_key=True)
    review_id = Column(BigInteger, nullable=False, primary_key=True)
    response_type = Column(String(6))
    response_value = Column(Text)

    element = relationship(
        "ReviewFormElement",
        primaryjoin='ReviewFormResponses.review_form_element_id == ReviewFormElement.review_form_element_id',
        uselist=False,
        lazy='subquery',
    )


class ReviewFormSettings(Base):
    __tablename__ = 'review_form_settings'
    __table_args__ = (
       Index('review_form_settings_pkey', 'review_form_id', 'locale', 'setting_name'),
    )
    review_form_id = Column(BigInteger, nullable=False, index=True, primary_key=True)
    locale = Column(String(5), nullable=False, server_default=u"''", primary_key=True)
    setting_name = Column(String(255), nullable=False, primary_key=True)
    setting_value = Column(Text)
    setting_type = Column(String(6), nullable=False)


class ReviewForm(Base):
    __tablename__ = 'review_forms'

    review_form_id = Column(BigInteger, primary_key=True)
    assoc_type = Column(BigInteger)
    assoc_id = Column(BigInteger)
    seq = Column(Float(asdecimal=True))
    is_active = Column(Integer)


class ReviewRound(Base):
    __tablename__ = 'review_rounds'
    __table_args__ = (
        Index('review_rounds_submission_id_stage_id_round_pkey', 'submission_id', 'stage_id', 'round'),
    )

    submission_id = Column(BigInteger, nullable=False, index=True)
    round = Column(Integer, nullable=False)
    review_revision = Column(BigInteger)
    status = Column(BigInteger)
    review_round_id = Column(BigInteger, primary_key=True)
    stage_id = Column(BigInteger)


class Roles(Base):
    __tablename__ = 'roles'

    journal_id = Column(BigInteger, nullable=False, index=True, primary_key=True)
    user_id = Column(ForeignKey('users.user_id'), nullable=False, index=True, primary_key=True)
    role_id = Column(BigInteger, nullable=False, index=True, primary_key=True)


class RtContext(Base):
    __tablename__ = 'rt_contexts'

    context_id = Column(BigInteger, primary_key=True)
    version_id = Column(BigInteger, nullable=False, index=True)
    title = Column(String(120), nullable=False)
    abbrev = Column(String(32), nullable=False)
    description = Column(Text)
    cited_by = Column(Integer, nullable=False, server_default=u"'0'")
    author_terms = Column(Integer, nullable=False, server_default=u"'0'")
    define_terms = Column(Integer, nullable=False, server_default=u"'0'")
    geo_terms = Column(Integer, nullable=False, server_default=u"'0'")
    seq = Column(Float(asdecimal=True), nullable=False, server_default=u"'0'")


class RtSearch(Base):
    __tablename__ = 'rt_searches'

    search_id = Column(BigInteger, primary_key=True)
    context_id = Column(BigInteger, nullable=False, index=True)
    title = Column(String(120), nullable=False)
    description = Column(Text)
    url = Column(Text)
    search_url = Column(Text)
    search_post = Column(Text)
    seq = Column(Float(asdecimal=True), nullable=False, server_default=u"'0'")


class RtVersion(Base):
    __tablename__ = 'rt_versions'

    version_id = Column(BigInteger, primary_key=True)
    journal_id = Column(BigInteger, nullable=False, index=True)
    version_key = Column(String(40), nullable=False, index=True)
    locale = Column(String(5), server_default=u"'en_US'")
    title = Column(String(120), nullable=False)
    description = Column(Text)


t_scheduled_tasks = Table(
    'scheduled_tasks', metadata,
    Column('class_name', String(255), nullable=False, unique=True),
    Column('last_run', DateTime)
)


class SectionEditor(Base):
    __tablename__ = 'section_editors'

    journal_id = Column(ForeignKey('journal.journal_id', deferrable=True, initially=u'DEFERRED'), nullable=False, index=True, primary_key=True)
    section_id = Column(ForeignKey('sections.section_id', deferrable=True, initially=u'DEFERRED'), nullable=False, index=True, primary_key=True)
    user_id = Column(ForeignKey('users.user_id', deferrable=True, initially=u'DEFERRED'), nullable=False, index=True, primary_key=True)
    can_edit = Column(Integer, nullable=False, server_default=u"'1'")
    can_review = Column(Integer, nullable=False, server_default=u"'1'")


class SectionSettings(Base):
    __tablename__ = 'section_settings'
    __table_args__ = (
        Index('section_settings_pkey', 'section_id', 'locale', 'setting_name'),
    )

    section_id = Column(ForeignKey('sections.section_id', deferrable=True, initially=u'DEFERRED'), nullable=False, index=True, primary_key=True)
    locale = Column('locale', String(5), nullable=False, server_default=u"''", primary_key=True)
    setting_name = Column('setting_name', String(255), nullable=False, primary_key=True)
    setting_value = Column('setting_value', Text)
    setting_type = Column('setting_type', String(6), nullable=False)


class Section(Base):
    __tablename__ = 'sections'

    section_id = Column(BigInteger, primary_key=True)
    journal_id = Column(BigInteger, nullable=False, index=True)
    review_form_id = Column(BigInteger)
    seq = Column(Float(asdecimal=True), nullable=False, server_default=u"'0'")
    editor_restricted = Column(Integer, nullable=False, server_default=u"'0'")
    meta_indexed = Column(Integer, nullable=False, server_default=u"'0'")
    meta_reviewed = Column(Integer, nullable=False, server_default=u"'1'")
    abstracts_not_required = Column(Integer, nullable=False, server_default=u"'0'")
    hide_title = Column(Integer, nullable=False, server_default=u"'0'")
    hide_author = Column(Integer, nullable=False, server_default=u"'0'")
    hide_about = Column(Integer, nullable=False, server_default=u"'0'")
    disable_comments = Column(Integer, nullable=False, server_default=u"'0'")
    abstract_word_count = Column(BigInteger)

    settings = relationship(u'SectionSettings', primaryjoin='Section.section_id == SectionSettings.section_id')
    settings = relationship(u'Article', primaryjoin='Section.section_id == Article.section_id')


class Sessions(Base):
    __tablename__ = 'sessions'
    __table_args__ = (
        Index('session_id', 'user_id'),
    )

    session_id = Column(String(40), nullable=False, unique=True, primary_key=True)
    user_id = Column(BigInteger, index=True, primary_key=True)
    ip_address = Column(String(39), nullable=False)
    user_agent = Column(String(255))
    created = Column(BigInteger, nullable=False, server_default=u"'0'")
    last_used = Column(BigInteger, nullable=False, server_default=u"'0'")
    remember = Column(Integer, nullable=False, server_default=u"'0'")
    data = Column(Text)


class Signoff(Base):
    __tablename__ = 'signoffs'
    __table_args__ = (
        Index('signoff_symbolic', 'assoc_type', 'assoc_id', 'symbolic', 'user_id', 'user_group_id', 'file_id', 'file_revision'),
    )

    signoff_id = Column(BigInteger, primary_key=True)
    symbolic = Column(String(32), nullable=False)
    assoc_type = Column(BigInteger, nullable=False, server_default=u"'0'")
    assoc_id = Column(BigInteger, nullable=False, server_default=u"'0'")
    user_id = Column(BigInteger, nullable=False)
    file_id = Column(BigInteger)
    file_revision = Column(BigInteger)
    date_notified = Column(DateTime)
    date_underway = Column(DateTime)
    date_completed = Column(DateTime)
    date_acknowledged = Column(DateTime)
    user_group_id = Column(BigInteger)


t_site = Table(
    'site', metadata,
    Column('redirect', BigInteger, nullable=False, server_default=u"'0'"),
    Column('primary_locale', String(5), nullable=False),
    Column('min_password_length', Integer, nullable=False, server_default=u"'6'"),
    Column('installed_locales', String(255), nullable=False, server_default=u"'en_US'"),
    Column('supported_locales', String(255)),
    Column('original_style_file_name', String(255))
)


t_site_settings = Table(
    'site_settings', metadata,
    Column('setting_name', String(255), nullable=False),
    Column('locale', String(5), nullable=False, server_default=u"''"),
    Column('setting_value', Text),
    Column('setting_type', String(6), nullable=False),
    Index('site_settings_pkey', 'setting_name', 'locale')
)


class StaticPageSetting(Base):
    __tablename__ = 'static_page_settings'

    static_page_id = Column(BigInteger, nullable=False, index=True, primary_key=True)
    locale = Column(String(5), nullable=False, server_default=u"''", primary_key=True)
    setting_name = Column(String(255), nullable=False, primary_key=True)
    setting_value = Column(String)
    setting_type = Column(String(6), nullable=False)


class StaticPage(Base):
    __tablename__ = 'static_pages'

    static_page_id = Column(BigInteger, primary_key=True)
    path = Column(String(255), nullable=False)
    journal_id = Column(BigInteger, nullable=False)


t_subscription_type_settings = Table(
    'subscription_type_settings', metadata,
    Column('type_id', BigInteger, nullable=False, index=True),
    Column('locale', String(5), nullable=False, server_default=u"''"),
    Column('setting_name', String(255), nullable=False),
    Column('setting_value', Text),
    Column('setting_type', String(6), nullable=False),
    Index('subscription_type_settings_pkey', 'type_id', 'locale', 'setting_name')
)


class SubscriptionType(Base):
    __tablename__ = 'subscription_types'

    type_id = Column(BigInteger, primary_key=True)
    journal_id = Column(BigInteger, nullable=False)
    cost = Column(Float(asdecimal=True), nullable=False)
    currency_code_alpha = Column(String(3), nullable=False)
    non_expiring = Column(Integer, nullable=False, server_default=u"'0'")
    duration = Column(SmallInteger)
    format = Column(SmallInteger, nullable=False)
    institutional = Column(Integer, nullable=False, server_default=u"'0'")
    membership = Column(Integer, nullable=False, server_default=u"'0'")
    disable_public_display = Column(Integer, nullable=False)
    seq = Column(Float(asdecimal=True), nullable=False)


class Subscription(Base):
    __tablename__ = 'subscriptions'

    subscription_id = Column(BigInteger, primary_key=True)
    journal_id = Column(BigInteger, nullable=False)
    user_id = Column(BigInteger, nullable=False)
    type_id = Column(BigInteger, nullable=False)
    date_start = Column(Date)
    date_end = Column(DateTime)
    status = Column(Integer, nullable=False, server_default=u"'1'")
    membership = Column(String(40))
    reference_number = Column(String(40))
    notes = Column(Text)


class TemporaryFile(Base):
    __tablename__ = 'temporary_files'

    file_id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    file_name = Column(String(90), nullable=False)
    file_type = Column(String(255))
    file_size = Column(BigInteger, nullable=False)
    original_file_name = Column(String(127))
    date_uploaded = Column(DateTime, nullable=False)


class Thes(Base):
    __tablename__ = 'theses'

    thesis_id = Column(BigInteger, primary_key=True)
    journal_id = Column(BigInteger, nullable=False, index=True)
    status = Column(SmallInteger, nullable=False)
    degree = Column(SmallInteger, nullable=False)
    degree_name = Column(String(255))
    department = Column(String(255), nullable=False)
    university = Column(String(255), nullable=False)
    date_approved = Column(DateTime, nullable=False)
    title = Column(String(255), nullable=False)
    url = Column(Text)
    abstract = Column(Text)
    comment = Column(Text)
    student_first_name = Column(String(40), nullable=False)
    student_middle_name = Column(String(40))
    student_last_name = Column(String(90), nullable=False)
    student_email = Column(String(90), nullable=False)
    student_email_publish = Column(Integer, server_default=u"'0'")
    student_bio = Column(Text)
    supervisor_first_name = Column(String(40), nullable=False)
    supervisor_middle_name = Column(String(40))
    supervisor_last_name = Column(String(90), nullable=False)
    supervisor_email = Column(String(90), nullable=False)
    discipline = Column(String(255))
    subject_class = Column(String(255))
    subject = Column(String(255))
    coverage_geo = Column(String(255))
    coverage_chron = Column(String(255))
    coverage_sample = Column(String(255))
    method = Column(String(255))
    language = Column(String(10), server_default=u"'en'")
    date_submitted = Column(DateTime, nullable=False)


t_usage_stats_temporary_records = Table(
    'usage_stats_temporary_records', metadata,
    Column('assoc_id', BigInteger, nullable=False),
    Column('assoc_type', BigInteger, nullable=False),
    Column('day', BigInteger, nullable=False),
    Column('metric', BigInteger, nullable=False, server_default=u"'1'"),
    Column('country_id', String(2)),
    Column('region', SmallInteger),
    Column('city', String(255)),
    Column('load_id', String(255), nullable=False),
    Column('file_type', Integer)
)


class UserInterests(Base):
    __tablename__ = 'user_interests'

    user_id = Column(
        ForeignKey('users.user_id', deferrable=True, initially=u'DEFERRED'),
        nullable=False,
        primary_key=True,
    )
    controlled_vocab_entry_id = Column(
        ForeignKey(
            ControlledVocabEntry.controlled_vocab_entry_id,
            deferrable=True,
            initially=u'DEFERRED'
        ),
        nullable=False,
        primary_key=True,
    )

    controlled_vocab = relationship(
        u'ControlledVocabEntry',
        primaryjoin='UserInterests.controlled_vocab_entry_id == '
                    'ControlledVocabEntry.controlled_vocab_entry_id',
        lazy='joined',
    )
    Column(ForeignKey(
        ControlledVocabEntry.controlled_vocab_entry_id,
        deferrable=True,
        initially=u'DEFERRED'),
        nullable=False,
        primary_key=True,
    )


'''
t_user_interests = Table(
    'user_interests', metadata,
    Column('user_id', BigInteger, nullable=False),
    Column('controlled_vocab_entry_id', BigInteger, nullable=False),
    Index('u_e_pkey', 'user_id', 'controlled_vocab_entry_id')
)
'''


class UserSetting(Base):
    __tablename__ = 'user_settings'

    user_id = Column(BigInteger, nullable=False, index=True, primary_key=True)
    locale = Column(String(5), nullable=False, primary_key=True)
    setting_name = Column(String(255), nullable=False, primary_key=True)
    assoc_type = Column(BigInteger, primary_key=True)
    assoc_id = Column(BigInteger, primary_key=True)
    setting_value = Column(Text)
    setting_type = Column(String(6), nullable=False)
    Index('user_settings_pkey', 'user_id', 'locale', 'setting_name', 'assoc_type', 'assoc_id')


class User(Base):
    __tablename__ = 'users'

    user_id = Column(BigInteger, primary_key=True)
    username = Column(String(32), nullable=False, unique=True)
    password = Column(String(40), nullable=False)
    salutation = Column(String(40))
    first_name = Column(String(40), nullable=False)
    middle_name = Column(String(40))
    last_name = Column(String(90), nullable=False)
    gender = Column(String(1))
    initials = Column(String(5))
    email = Column(String(90), nullable=False, unique=True)
    url = Column(String(255))
    phone = Column(String(24))
    fax = Column(String(24))
    mailing_address = Column(String(255))
    country = Column(String(90))
    locales = Column(String(255))
    date_last_email = Column(DateTime)
    date_registered = Column(DateTime, nullable=False)
    date_validated = Column(DateTime)
    date_last_login = Column(DateTime, nullable=False)
    must_change_password = Column(Integer)
    auth_id = Column(BigInteger)
    auth_str = Column(String(255))
    disabled = Column(Integer, nullable=False, server_default=u"'0'")
    disabled_reason = Column(Text)
    suffix = Column(String(40))
    billing_address = Column(String(255))
    inline_help = Column(Integer)

    roles = relationship(u'Roles', primaryjoin='User.user_id == Roles.user_id', lazy='joined')
    interests = relationship(u'UserInterests', primaryjoin='User.user_id == UserInterests.user_id', lazy='joined')


class GroupMemberships(Base):
    __tablename__ = 'group_memberships'
    __table_args__ = (
        Index('group_memberships_pkey', 'user_id', 'group_id'),
    )
    user_id = Column(ForeignKey('users.user_id', deferrable=True, initially=u'DEFERRED'), nullable=False, primary_key=True)
    group_id = Column(BigInteger, nullable=False, primary_key=True)
    about_displayed = Column(Integer, nullable=False, server_default=u"'1'")
    seq = Column(Float(asdecimal=True), nullable=False, server_default=u"'0'")

    user = relationship(u'User', primaryjoin='GroupMemberships.user_id == User.user_id')


t_versions = Table(
    'versions', metadata,
    Column('major', Integer, nullable=False, server_default=u"'0'"),
    Column('minor', Integer, nullable=False, server_default=u"'0'"),
    Column('revision', Integer, nullable=False, server_default=u"'0'"),
    Column('build', Integer, nullable=False, server_default=u"'0'"),
    Column('date_installed', DateTime, nullable=False),
    Column('current', Integer, nullable=False, server_default=u"'0'"),
    Column('product_type', String(30)),
    Column('product', String(30)),
    Column('product_class_name', String(80)),
    Column('lazy_load', Integer, nullable=False, server_default=u"'0'"),
    Column('sitewide', Integer, nullable=False, server_default=u"'0'"),
    Index('versions_pkey', 'product_type', 'product', 'major', 'minor', 'revision', 'build')
)


class Taxonomy(Base):
    __tablename__ = 'taxonomy'

    id = Column(BigInteger, primary_key=True)
    name = Column(String(100))
    note = Column(Text)
    front_end = Column(Integer)

    editors = relationship(u'TaxonomyEditor')
    articles = relationship(u'TaxonomyArticle')


class TaxonomyEditor(Base):
    __tablename__ = 'taxonomy_editor'

    id = Column(BigInteger, primary_key=True)
    user_id = Column(ForeignKey('users.user_id'), nullable=False)
    taxonomy_id = Column(ForeignKey('taxonomy.id'), nullable=False)

    user = relationship(u'User')


class TaxonomyArticle(Base):

    __tablename__ = 'taxonomy_article'

    id = Column(BigInteger, primary_key=True)
    taxonomy_id = Column(ForeignKey('taxonomy.id'), nullable=False)
    article_id = Column(ForeignKey('articles.article_id'), nullable=False)

    taxonomy = relationship(
        "Taxonomy",
        backref="taxonomy_id",
        lazy='joined')
