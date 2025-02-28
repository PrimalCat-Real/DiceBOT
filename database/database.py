from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import sys

class DatabaseManager:
    def __init__(self, connection_string, database_name):
        try:
            self.client = MongoClient(connection_string)
            self.client.admin.command('ping')
            self.db = self.client[database_name]
            self.users = self.db['users']
            self.forms = self.db['forms']
            self.moders = self.db['moders']
            self.discord_embeds = self.db['discord_embeds']
            self.configs = self.db['configs']
            print("Connected to MongoDB!") 
        except Exception as e:
            self.client = None
            self.db = None
            self.discord_embeds = None
        assert self.client is not None, "Cannot connect to MongoDB"
        
    def save_discord_message(self, message_id, channel_id, guild_id, embed_data, view_data=None):
        self.discord_embeds.update_one(
            {'message_id': message_id},
            {'$set': {
                'message_id': message_id,
                'channel_id': channel_id,
                'guild_id': guild_id,
                'embed_data': embed_data,
                'view_data': view_data
            }},
            upsert=True
        )

    def get_discord_messages(self):
        return list(self.discord_embeds.find())

    def get_discord_message(self, message_id):
        return self.discord_embeds.find_one({'message_id': message_id})

    def delete_discord_message(self, message_id):
        self.discord_embeds.delete_one({'message_id': message_id})

    def close(self):
        self.client.close()

    def get_user(self, user_id):
        return self.users.find_one({'user_id': user_id})

    def update_user(self, user_id, update_data):
        self.users.update_one({'user_id': user_id}, {'$set': update_data}, upsert=True)

    def get_form(self, form_id):
        return self.forms.find_one({'form_id': form_id})

    def update_form(self, form_id, update_data):
        self.forms.update_one({'form_id': form_id}, {'$set': update_data}, upsert=True)

    def get_moder(self, moder_id):
        return self.moders.find_one({'moder_id': moder_id})

    def update_moder(self, moder_id, update_data):
        self.moders.update_one({'moder_id': moder_id}, {'$set': update_data}, upsert=True)

    def get_discord_embed(self, message_id):
        return self.discord_embeds.find_one({'message_id': message_id})

    def update_discord_embed(self, message_id, update_data):
        self.discord_embeds.update_one({'message_id': message_id}, {'$set': update_data}, upsert=True)

    def get_config(self, guild_id):
        return self.configs.find_one({'guild_id': guild_id})

    def set_guild_id(self, guild_id):
        self.configs.update_one({'guild_id': guild_id}, {'$set': {'guild_id': guild_id}}, upsert=True)

    def update_config(self, guild_id, update_data):
        self.configs.update_one({'guild_id': guild_id}, {'$set': update_data}, upsert=True)

    def save_message_with_button(self, message_id, channel_id, guild_id):
        self.discord_embeds.update_one(
            {'message_id': message_id},
            {'$set': {'message_id': message_id, 'channel_id': channel_id, 'guild_id': guild_id}},
            upsert=True
        )

    def get_messages_with_buttons(self):
        return list(self.discord_embeds.find())


# Пример использования:
# user_data = db_manager.get_user(12345)
# db_manager.update_user(12345, {'username': 'NewUsername'})
# db_manager.close()