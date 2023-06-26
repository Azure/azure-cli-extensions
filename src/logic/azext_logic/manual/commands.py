
def load_command_table(self, _):  # pylint: disable=unused-argument
    with self.command_group('logic integration-account map'):
        from azext_logic.manual.custom import MapCreate, MapUpdate
        self.command_table['logic integration-account map create'] = MapCreate(loader=self)
        self.command_table['logic integration-account map update'] = MapUpdate(loader=self)
