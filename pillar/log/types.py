import typing
from types import TracebackType

ArgsType = typing.Union[typing.Tuple[typing.Any, ...], typing.Mapping[str, typing.Any]]
SysExcInfoType = typing.Union[
    typing.Tuple[
        typing.Type[BaseException], BaseException, typing.Optional[TracebackType]
    ],
    typing.Tuple[None, None, None],
]
