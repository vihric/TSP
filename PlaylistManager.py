from DbManagement import DbInteractionManager
from random import randint


class Playlist:
    def __init__(self, playlist=None, loop=False):
        if playlist is None:
            playlist = []
        self.position = 0
        self.playlist = playlist
        self.loop = loop

    def __iter__(self):
        return self

    def __next__(self):
        if not self.loop:
            while self.position < len(self.playlist):
                result = self.playlist[self.position]
                self.position += 1
                return result
            raise StopIteration
        else:
            while True:
                result = self.playlist[self.position]
                self.position = (self.position + 1) % len(self.playlist)
                return result

    def __reversed__(self):
        if not self.loop:
            while self.position >= 0:
                result = self.playlist[self.position]
                self.position -= 1
                return result
            raise StopIteration
        else:
            while True:
                result = self.playlist[self.position]
                self.position = (self.position - 1) % len(self.playlist)
                return result

    def __contains__(self, item):
        return item in self.playlist

    def __getitem__(self, position):
        return self.playlist[position % len(self.playlist)]

    def __len__(self):
        return len(self.playlist)

    def reset_position(self):
        self.position = 0

    def set_position(self, position):
        self.position = position


class PlaylistManager:
    def __init__(self, db_manager=None, desired_length=100):
        if db_manager is None:
            self.db_manager = DbInteractionManager()
        else:
            self.db_manager = db_manager
        self.blacklist = []
        self.required_tags = []
        self.weights = {}
        self.constructed_playlist = None
        self.prototype = None
        self.desired_length = desired_length

    def set_weights(self, weights):
        self.weights = weights

    def add_weight(self, tag, weight):
        self.weights[tag] = weight

    def add_weights(self, tags, weights):
        if len(tags) != len(weights):
            raise ValueError("length of tags and weights must be equal!")
        for i in range(len(tags)):
            self.add_weight(tags[i], weights[i])

    def add_weights(self, weights):
        for tag, weight in weights:
            self.weights[tag] = weight

    def add_blacklisted_tag(self, tag):
        self.blacklist.append(tag)

    def add_blacklisted_tags(self, tags):
        for tag in tags:
            self.add_blacklisted_tag(tag)

    def add_required_tag(self, tag):
        self.required_tags.append(tag)

    def add_required_tags(self, tags):
        for tag in tags:
            self.add_required_tag(tag)

    def set_desired_length(self, new_length):
        self.desired_length = new_length

    def get_playlist_prototype(self):
        raw = self.db_manager.get_items(filters_tags_required=self.required_tags, filters_tags_blacklist=self.blacklist)
        if len(self.weights.keys()) == 0:
            self.prototype = raw
            return self.prototype
        else:
            prototype = []
            for raw_item in raw:
                prototype_item = raw_item['item']
                print(raw_item)
                print("!!!")
                weight = 0
                for tag, tag_weight in self.weights:
                    if tag in raw_item['tags'].keys():
                        weight += tag_weight * raw_item['tags'][tag]
                if weight > 0:
                    for i in range(weight):
                        prototype.append(prototype_item)
            self.prototype = prototype
            return self.prototype

    def get_playlist(self):
        if self.prototype is None:
            raise ValueError("Prototype is not initialized: try running get_playlist_prototype() before this method!")
        playlist = []
        try:
            domain = len(self.prototype)
        except Exception:
            raise ValueError("Unable to get prototype length: Manager is in invalid state!")
        if domain == 0:
            return Playlist()
        else:
            for i in range(self.desired_length):
                next_key = randint(0, domain-1)
                playlist.append(self.prototype[next_key])
        return Playlist(playlist=playlist)