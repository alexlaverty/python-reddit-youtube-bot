"""Helper utilities."""

import ast
import os
from argparse import Action, ArgumentParser, Namespace
from typing import Any, Optional, Sequence, Union


class EnvDefault(Action):
    """Custom action used to set CLI arguments via environment variables."""

    def __init__(self, envvar: str, required=False, default=None, **kwargs) -> None:
        """Initialize the action.

        Args:
            envvar: Name of the environment variable to read the argument value from.
            required: ```True``` to make the argument mandatory, otherwise ```False```.
            default: Default value is none is specified by the user.
            kwargs: Extra argument configuration options.
        """
        if not default and envvar:
            default = os.getenv(envvar, None)

        if required and default:
            required = False

        super(EnvDefault, self).__init__(default=default, required=required, **kwargs)

    def __call__(
        self,
        parser: ArgumentParser,
        namespace: Namespace,
        values: Optional[Union[str, Sequence[Any]]],
        option_string: Optional[str] = None,
    ) -> None:
        """Class setup executed during object instantiation.

        Args:
            parser: ArgumentParser that contains the user specified CLI parameters.
            namespace: Namespace that contains the argument parser parameters.
            values: Parameter value.
            option_string: Option strings passed to the parameter.
        """
        setattr(namespace, self.dest, values)


class EnvFlagDefault(Action):
    """Custom action used to set CLI flags via environment variables."""

    def __init__(
        self,
        option_strings: Sequence[str],
        dest: str,
        default: Optional[bool] = None,
        required: bool = False,
        help: Optional[str] = None,
        envvar: Optional[str] = None,
        metavar: Optional[str] = None,
    ) -> None:
        """Initialize the action.

        If a default value has not been defined, but an environment variable name has
        been provided, the action will try to set the flag based on the truthiness of
        the provided environment variable (True/False).

        Args:
            option_strings: Raw parameter options.
            dest: Name of the destination parameter that the parameter value will be
                stored under.
            default: Default value is none is specified by the user.
            required: ```True``` to make the argument mandatory, otherwise ```False```.
            help: Help text displayed when the -h/--help parameter is used.
            envvar: Name of the environment variable to read the argument value from.
            metavar: Name of the metavar used as a placeholder on the help screen.
        """
        if not default and envvar:
            default = ast.literal_eval(os.getenv(envvar, "False"))

        if required and default:
            required = False

        super(EnvFlagDefault, self).__init__(
            option_strings=option_strings,
            dest=dest,
            const=True,
            default=default,
            required=required,
            help=help,
            metavar=metavar,
            nargs=0,
        )
        self.envvar = envvar

    def __call__(
        self,
        parser: ArgumentParser,
        namespace: Namespace,
        values: Optional[Union[str, Sequence[Any]]],
        option_string: Optional[str] = None,
    ) -> None:
        """Class setup executed during object instantiation.

        Args:
            parser: ArgumentParser that contains the user specified CLI parameters.
            namespace: Namespace that contains the argument parser parameters.
            values: Parameter value.
            option_string: Option strings passed to the parameter.
        """
        setattr(namespace, self.dest, self.const)
