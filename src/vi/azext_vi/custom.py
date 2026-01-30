# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError
from rich.console import Console
from rich.table import Table

def my_vi_command(client):
    return {"message": "This is my custom VI command!"}


def show_vi_extension(client, resource_group_name):
    extension = client.show_vi_extension(resource_group_name=resource_group_name)
    return extension


def troubleshoot_vi_extension(client, resource_group_name):
    extension = client.troubleshoot_vi_extension(resource_group_name=resource_group_name)
    return extension


def list_cameras(client, resource_group_name):
    response = client.list_cameras(resource_group_name=resource_group_name)
    cameras = response.get('results')
    console = Console()
    console.print(json_to_table(cameras))
    return cameras


def json_to_table(data: list[dict], title: str = "Cameras") -> Table:
    """Convert a list of dicts to a Rich table"""
    if not data:
        return Table(title="No Results")
    
    table = Table(title=title, show_header=True, header_style="bold blue")

    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Status", style="green")
    table.add_column("Rtsp url", style="yellow")
    table.add_column("live Enabled", style="green")
    table.add_column("recording Enabled", style="green")
    
    # Add all rows
    for item in data:
        table.add_row(
            item["name"],
            item["status"],
            item["rtspUrl"],
            str(item["liveStreamingEnabled"]),
            str(item["recordingEnabled"]))
    
    return table


def list_vi(cmd, resource_group_name=None):
    raise CLIError('TODO: Implement `vi list`')


def update_vi(cmd, instance, tags=None):
    with cmd.update_context(instance) as c:
        c.set_param('tags', tags)
    return instance