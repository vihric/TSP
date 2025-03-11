from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)

    item_tags = relationship(
        "ItemTag", back_populates="item", cascade="all, delete-orphan"
    )
    tags = relationship(
        "Tag", secondary="item_tags", viewonly=True, overlaps="item_tags"
    )


class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)

    tag_items = relationship(
        "ItemTag", back_populates="tag", cascade="all, delete-orphan"
    )
    items = relationship(
        "Item", secondary="item_tags", viewonly=True, overlaps="tag_items"
    )


class ItemTag(Base):
    __tablename__ = "item_tags"
    item_id = Column(Integer, ForeignKey("items.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id"), primary_key=True)
    weight = Column(Integer)

    item = relationship("Item", back_populates="item_tags", overlaps="tags")
    tag = relationship("Tag", back_populates="tag_items", overlaps="items")


class ModelsMain:
    engine = None
    session = None
    Session = None

    @classmethod
    def _initialize_class(cls):
        if cls.Session is None:
            cls.engine = create_engine("sqlite:///main.db")
            Base.metadata.create_all(cls.engine)
            cls.Session = sessionmaker(bind=cls.engine)
            cls.session = cls.Session()

    def get_new_session(self):
        return ModelsMain.Session()

    def get_persistent_session(self):
        return ModelsMain.session

    def __init__(self):
        ModelsMain._initialize_class()
