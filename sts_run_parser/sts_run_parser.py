from typing import Any

import reflex as rx

from .parser import average_floor_data, runs, run_filter


class State(rx.State):
    character: str = 'ALL'
    lookback: list[int | float] = [100]
    live_lookback: list[int | float] = [100]

    @rx.var
    def data(self) -> list[dict[str, Any]]:
        def sort_key(run):
            return run['local_time']
        rundata = sorted(list(filter(run_filter, runs())), key=sort_key)
        return average_floor_data(rundata, self.lookback[0], self.character)

    @rx.var
    def data_exists(self) -> bool:
        return bool(self.data)


def index() -> rx.Component:
    return rx.container(
        rx.color_mode.button(position="bottom-right"),
        rx.vstack(
            rx.cond(
                State.data_exists,
                rx.heading(
                    'Average floor reached and winrate over the last'
                    f" {State.data[-1]['run']} runs, with a lookback period"
                    f" of {State.lookback[0]} runs.",
                    align='center'),
                None),
            rx.recharts.line_chart(
                rx.recharts.line(
                    data_key='winrate',
                    stroke='#82ca9d',
                    dot=False,
                    type_='monotone',
                    stroke_width=2,
                    y_axis_id='left'),
                rx.recharts.line(
                    data_key='avg_floor',
                    stroke='#8884d8',
                    dot=False,
                    type_='monotone',
                    stroke_width=2,
                    y_axis_id='right'),
                rx.recharts.reference_line(
                    y=17,
                    y_axis_id='right',
                    stroke='#8884d8',
                    label='Act 1'),
                rx.recharts.reference_line(
                    y=34,
                    y_axis_id='right',
                    stroke='#8884d8',
                    label='Act 2'),
                rx.recharts.x_axis(data_key='run'),
                rx.recharts.y_axis(data_key='winrate', y_axis_id='left'),
                rx.recharts.y_axis(data_key='avg_floor', y_axis_id='right',
                                   orientation='right'),
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
                    on_change=State.set_character
                ),
                rx.slider(
                    on_value_commit=State.set_lookback,
                    on_change=State.set_live_lookback.throttle(100),
                    min=10,
                    max=500,
                    step=10,
                    width='200px'
                ),
                rx.text(State.live_lookback[0]),
                align='center'
            ),
            align='center'
        )
    )


app = rx.App()
app.add_page(index)
