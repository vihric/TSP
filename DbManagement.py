from DbModels import ModelsMain, Tag, ItemTag, Item
from builtins import Exception


class DbInteractionManager:
    def __init__(self, model=None):
        if model is None:
            self.model = ModelsMain()
        else:
            self.model = model

    def add_tag(self, tag_name, old_session=None):
        if old_session is None:
            session = self.model.get_new_session()
        else:
            session = old_session
        try:
            tag = session.query(Tag).filter(Tag.name == tag_name).first()
            if tag:
                # Tag exists, return its ID
                return tag.id
            else:
                # Tag does not exist, create a new tag
                new_tag = Tag(name=tag_name)
                session.add(new_tag)
                session.commit()

                # Return the ID of the newly created tag
                return new_tag.id
        finally:
            if old_session is None:
                session.close()

    def filter_by_tags(self, items_with_tags, tags_required=None, tags_blacklisted=None):
        final_items = []
        for item in items_with_tags:
            tags = item['tags']
            if self._is_under_filter(tags, tags_required, tags_blacklisted):
                final_items.append(item)
        return final_items

    def _is_under_filter(self, tags, tags_required, tags_blacklisted):
        for tag in tags:
            if tag in tags_blacklisted:
                return False
        for tag in tags_required:
            if tag not in tags:
                return False
        return True

    def get_items(self, filters_basic=None, filters_tags_required=None, filters_tags_blacklist=None, table=Item):
        session = self.model.get_new_session()
        try:
            if filters_basic is None:
                items = session.query(Item).all()
                items_with_tags = []
                for item in items:
                    item_data = {
                        'item': {
                            'id': item.id,
                            'name': item.name,
                        },
                        'tags': {tag.name: link.weight for tag, link in zip(item.tags, item.item_tags)}
                    }
                    items_with_tags.append(item_data)
                return self.filter_by_tags(items_with_tags, filters_tags_required, filters_tags_blacklist)
            elif filter is dict:
                if table is None:
                    ValueError("if filters are not empty, table must not be empty either")
                items_with_tags = self._get_items_with_filters(self, filters_basic, session, table)
                return self.filter_by_tags(items_with_tags, filters_tags_required, filters_tags_blacklist, table)
            else:
                raise ValueError("invalid filter structure")
        finally:
            session.close()

    def _get_items_with_filters(self, filters, session, table):
        query = session.query(table)
        for field, value in filters.items():
            query = query.filter(getattr(table, field) == value)
        items = query.all()
        items_with_tags = []
        for item in items:
            item_data = {
                'item': {
                    'id': item.id,
                    'name': item.name,
                },
                'tags': {tag.name: link.weight for tag, link in zip(item.tags, item.item_tags)}
            }
            items_with_tags.append(item_data)
        return items_with_tags

    def get_items_raw(self):
        session = self.model.get_new_session()
        try:
            return session.query(Item).all()
        finally:
            session.close()

    def update_items(self, updated):
        try:
            for updated_item in updated:
                item, tags = updated_item
                updated_id = item.id
                self.delete_item(updated_id)
                self.insert_item(item, tags)
            return True
        except Exception:
            return False

    def insert_item(self, item, tags):
        session = self.model.get_new_session()
        try:
            new_item = Item(name=item.name)
            session.add(new_item)
            session.flush()
            for tag, tag_weight in tags.items():
                new_tag_id = self.add_tag(tag, session)
                new_link = ItemTag(item_id=new_item.id, weight=tag_weight, tag_id=new_tag_id)
                session.add(new_link)
                if new_link is None:
                    raise IOError("Db write error")
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def insert_items(self, items, many_tags):
        if len(items) != len(many_tags):
            raise ValueError("len of items and tags must be equal!")
        for i in range(len(items)):
            self.insert_item(items[i], many_tags[i])

    def delete_item(self, item_id):
        session = self.model.get_new_session()
        try:
            item_to_delete = session.query(Item).filter(Item.id == item_id).first()
            if item_to_delete:
                # Delete the item if it exists
                session.delete(item_to_delete)
                session.commit()
        finally:
            session.close()

    def delete_items(self, ids):
        for item_id in ids:
            self.delete_item(item_id)
