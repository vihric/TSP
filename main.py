from PlaylistManager import PlaylistManager, Playlist
import DbManagement
from Util import PseudoItem

if __name__ == '__main__':
    dbm = DbManagement.DbInteractionManager()
    playlist_manager = PlaylistManager(dbm)
    item1 = PseudoItem(name="test1")
    item2 = PseudoItem(name="test2")
    item3 = PseudoItem(name="test3")
    item4 = PseudoItem(name="test4")
    dbm.insert_item(item1, {"tag1": 2, "tag2": 3})
    dbm.insert_item(item2, {"tag2": 2, "tag3": -1})
    dbm.insert_item(item3, {"tag1": 2, "tag2": 0, "tag4": 4})
    dbm.insert_item(item4, {"tag1": 2, "tag3": 1})

    playlist_manager.add_blacklisted_tag("tag4")
    playlist_manager.add_required_tag("tag2")

    playlist_manager.get_playlist_prototype()
    playlist = playlist_manager.get_playlist()
    print(len(playlist))
    print(playlist_manager.prototype)
    for item in playlist:
        print(item)
