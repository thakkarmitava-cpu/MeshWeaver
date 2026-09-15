import asyncio
import time

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table

from dht.node import DHTNode
from dht.network import heartbeat_peer


class MeshWeaverDashboard:
    """
    Rich terminal dashboard for monitoring a MeshWeaver node.
    """

    def __init__(
        self,
        node: DHTNode,
        protocol,
        console: Console | None = None,
    ):
        self.node = node
        self.protocol = protocol

        self.console = (
            console
            if console is not None
            else Console()
        )

        self.peer_health: dict[int, bool] = {}

    def _format_last_seen(
        self,
        node_id: int,
    ) -> str:
        last_seen = self.node.get_last_seen(
            node_id
        )

        if last_seen is None:
            return "Unknown"

        elapsed = time.time() - last_seen

        if elapsed < 1:
            return "Just now"

        if elapsed < 60:
            return f"{elapsed:.1f}s ago"

        return f"{elapsed / 60:.1f}m ago"

    def _build_header(self) -> Panel:
        node_id = (
            f"{self.node.node_id:040x}"
        )

        text = (
            f"[bold]Node:[/bold] "
            f"{self.node.host}:{self.node.port}\n"
            f"[bold]Node ID:[/bold] "
            f"{node_id}\n"
            f"[bold]Known Peers:[/bold] "
            f"{self.node.peer_count()}"
        )

        return Panel(
            text,
            title="MeshWeaver Node",
            border_style="blue",
        )

    def _build_peer_table(self) -> Table:
        table = Table(
            title="Peer Status"
        )

        table.add_column(
            "Node ID",
            style="cyan",
        )

        table.add_column(
            "Address",
            style="green",
        )

        table.add_column(
            "Health",
            style="yellow",
        )

        table.add_column(
            "Last Seen",
            style="magenta",
        )

        for peer in self.node.get_peers():
            health = self.peer_health.get(
                peer.node_id,
                None,
            )

            if health is True:
                health_text = "ALIVE"
            elif health is False:
                health_text = "TIMEOUT"
            else:
                health_text = "UNKNOWN"

            short_id = (
                f"{peer.node_id:040x}"[:12]
                + "..."
            )

            table.add_row(
                short_id,
                f"{peer.host}:{peer.port}",
                health_text,
                self._format_last_seen(
                    peer.node_id
                ),
            )

        if not self.node.get_peers():
            table.add_row(
                "-",
                "No peers",
                "-",
                "-",
            )

        return table

    def _build_summary(self) -> Panel:
        alive_count = sum(
            1
            for value in self.peer_health.values()
            if value is True
        )

        timeout_count = sum(
            1
            for value in self.peer_health.values()
            if value is False
        )

        total = self.node.peer_count()

        summary = (
            f"[bold]Total peers:[/bold] {total}    "
            f"[bold]Alive:[/bold] {alive_count}    "
            f"[bold]Timeout:[/bold] {timeout_count}"
        )

        return Panel(
            summary,
            title="Network Summary",
            border_style="green",
        )

    def render(self):
        """
        Build the complete dashboard layout.
        """

        from rich.console import Group

        return Group(
            self._build_header(),
            self._build_peer_table(),
            self._build_summary(),
        )

    async def refresh_health(
        self,
        timeout: float = 1.0,
    ):
        """
        Perform one heartbeat round and update
        the dashboard health information.
        """

        peers = list(
            self.node.get_peers()
        )

        current_health = {}

        for peer in peers:
            alive = await heartbeat_peer(
                self.protocol,
                peer,
                timeout=timeout,
            )

            current_health[
                peer.node_id
            ] = alive

        self.peer_health = current_health


async def run_dashboard(
    node: DHTNode,
    protocol,
    interval: float = 2.0,
    heartbeat_timeout: float = 1.0,
):
    """
    Run the live MeshWeaver Rich dashboard.
    """

    dashboard = MeshWeaverDashboard(
        node,
        protocol,
    )

    with Live(
        dashboard.render(),
        console=dashboard.console,
        refresh_per_second=4,
    ) as live:

        while True:
            await dashboard.refresh_health(
                timeout=heartbeat_timeout
            )

            live.update(
                dashboard.render()
            )

            await asyncio.sleep(
                interval
            )