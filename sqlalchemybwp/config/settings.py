from blazeweb.config import PluginSettings

class Settings(PluginSettings):
    def init(self):
        self.for_me.pre_test_init_event_enabled = True
        self.for_me.pre_test_clear_data_only = False
