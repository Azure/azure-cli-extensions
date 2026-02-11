
from rich.console import Console
from rich.table import Table

def format_cameras(cameras):
    console = Console()
    console.print(json_to_table(cameras))
    return cameras

def json_to_table(data: list[dict], title: str = "Cameras"):
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