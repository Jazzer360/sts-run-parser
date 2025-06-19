"""Welcome to Reflex! This file outlines the steps to create a basic app."""
from typing import Any

import reflex as rx

from .parser import average_floor_data, runs, run_filter


class State(rx.State):
    """The app state."""
    character: str = 'ALL'
    lookback: int = 100

    @rx.var
    def data(self) -> list[dict[str, Any]]:
        def sort_key(run):
            return run['local_time']
        rundata = sorted(list(filter(run_filter, runs())), key=sort_key)
        return average_floor_data(rundata, self.lookback, self.character)


def index() -> rx.Component:
    # Welcome Page (Index)
    return rx.container(
        rx.color_mode.button(position="top-right"),
        rx.vstack(
            rx.recharts.line_chart(
                rx.recharts.line(data_key='winrate'),
                rx.recharts.line(data_key='avg_floor'),
                rx.recharts.x_axis(data_key='run'),
                rx.recharts.y_axis(),
                data=State.data,
                width="100%",
                height=300
            )
        ),
        rx.logo(),
    )


app = rx.App()
app.add_page(index)
