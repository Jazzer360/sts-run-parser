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

    @rx.event
    def change_character(self, value: str):
        self.character = value

    @rx.event
    def change_lookback(self, value: list[int | float]):
        self.lookback = value[0]


def index() -> rx.Component:
    # Welcome Page (Index)
    return rx.container(
        rx.color_mode.button(position="top-right"),
        rx.vstack(
            rx.recharts.line_chart(
                rx.recharts.line(
                    data_key='winrate',
                    stroke='#82ca9d',
                    dot=False,
                    type_='monotone',
                    stroke_width=2),
                rx.recharts.line(
                    data_key='avg_floor',
                    stroke='#8884d8',
                    dot=False,
                    type_='monotone',
                    stroke_width=2),
                rx.recharts.x_axis(data_key='run'),
                rx.recharts.y_axis(),
                rx.recharts.graphing_tooltip(),
                rx.recharts.legend(),
                data=State.data,
                width="100%",
                height=500
            ),
            rx.hstack(
                rx.select(
                    ['ALL', 'IRONCLAD', 'THE_SILENT', 'DEFECT', 'WATCHER'],
                    value=State.character,
                    on_change=State.change_character
                ),
                rx.vstack(
                    rx.heading(State.lookback),
                    rx.slider(
                        on_value_commit=State.change_lookback,
                        min_=1,
                        max=500
                    ),
                    width='100%'
                ),
                width='100%'
            )
        ),
        rx.logo(),
    )


app = rx.App()
app.add_page(index)
