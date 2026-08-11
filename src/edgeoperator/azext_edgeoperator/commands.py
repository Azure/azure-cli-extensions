def load_command_table(self, _):
    with self.command_group("aldo system-readiness") as group:
        group.custom_show_command("show", "show_system_readiness")
