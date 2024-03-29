# Logging

ASAB logging is built on top of the [`logging` module](https://docs.python.org/3/library/logging.html).
It provides standard logging to `stderr` output when running on a console, and also file and syslog output (both RFC5424 and RFC3164) for background mode of operations.

Log timestamps are captured with sub-second precision (depending on the
system capabilities) and displayed including microsecond part.

## Recommended use

We recommend to create a logger `L` in every module that captures all
necessary logging output. Alternative logging strategies are also
supported.

!!! example

    The following code

    ```python title="myapp/mymodule.py"
    import logging

    L = logging.getLogger(__name__)

    ...

    L.warning("Hello world!")
    ```

    will produce the following output to the console:

    ```
    25-Mar-2018 23:33:58.044595 WARNING myapp.mymodule Hello world!
    ```


## Logging Levels

ASAB uses Python logging levels with the addition of `LOG_NOTICE` level.
`LOG_NOTICE` level is similar to `logging.INFO` level but it is visible
in even in non-verbose mode.

Level | Numeric value | Syslog Severity level |
| --- | --- | --- |
| `CRITICAL` | 50 | Critical / `crit` / 2 |
| `ERROR` | 40 | Error / `err` / 3 |
| `WARNING` | 30 | Warning / `warning` / 4 |
| `LOG_NOTICE` | 25 | Notice / `notice` / 5 |
| `INFO` | 20 | Informational / `info` / 6 |
| `DEBUG` | 10 | Debug / `debug` / 7 |
| `NOTSET` | 0  | |


!!! example "Usage of the `LOG_NOTICE` level:"

    ```python
    L.log(asab.LOG_NOTICE, "This message will be visible regardless verbose configuration.")
    ```

!!! example "Setting the level for the entire application:"

    ```ini
    [logging]
    level = DEBUG
    ```

!!! example "Setting levels for particular modules:"

    ```ini
    [logging]
    levels=
        myApp.module1 DEBUG
        myApp.module2 WARNING
    ```

    Each logger must be on a separate line.
    The logger name and the corresponding logging level have to be separated by a space.


## Verbose mode

By default, only logs with a level greater than 20 are visible, so `DEBUG` and `INFO` levels are not displayed. For accessing these levels, the application must be started with the **verbose mode**. This is done by the command-line argument `-v`.

!!! example

    There are three ways to display `DEBUG` and `INFO` log messages.

    1. By enabling the verbose mode with command-line argument:

        ```shell
        python3 myapp.py -v
        ```

    2. By accessing the `asab.Config["logging"]["verbose"]` boolean option:

        ```ini
        [logging]
        verbose = true
        ```

        The string `true` is interpreted by `ConfigParser` via [`this method`](#asab.utils.string_to_boolean).

    3. By setting the logging level directly:

        ```ini
        [logging]
        level = DEBUG
        ```


!!! note

    The verbose mode also enables `asyncio` and Zookeeper debug logging.


## Structured data

ASAB supports a structured data to be added to a log entry. Structured data is passed to the log message as a dictionary that has to be JSON-serializable.

!!! example

    The following warning message with structured data

    ```python title="myapp/mymodule.py"
    L.warning("Hello world!", struct_data={'key1':'value1', 'key2':2})
    ```

    will produce the following output to the console:

    ```
    25-Mar-2018 23:33:58.044595 WARNING myapp.mymodule [sd key1="value1" key2="2"] Hello world!
    ```


!!! info
    ASAB structured data logging follows the [RFC 5424](https://datatracker.ietf.org/doc/html/rfc5424#section-6.3).


!!! tip

    Use logging with structured data to provide better error messages:

    ```python title='myapp/mymodule.py'
    try:
        print(a / b)
    except ZeroDivisionError:
        L.error("Division by zero.", struct_data={"a": a, "b": b})
    ``` 

    Output:

    ```
    27-Jul-2023 16:54:22.311522 ERROR myapp.mymodule [sd a="24" b="0"] Division by zero.
    ```

## Logging to console

The ASAB application will log to the console only if it detects that it is running on the terminal 
(using [`os.isatty()`](https://www.w3schools.com/python/ref_os_isatty.asp) function) or if the
environment variable `ASABFORCECONSOLE` is set to `1`. This is useful setup for eg. PyCharm.


## Logging to a file

The command-line argument `-l` enables logging to a file.
Non-empty `path` option in the section `[logging:file]` of the configuration file also enables logging to a file.

!!! example "Example of the configuration section:"

    ```ini
    [logging:file]
    path=/var/log/asab.log
    format="%(asctime)s %(levelname)s %(name)s %(struct_data)s%(message)s",
    datefmt="%d-%b-%Y %H:%M:%S.%f"
    backup_count=3
    rotate_every=1d
    ```

!!! tip

    When the deployment expects more instances of the same application to be
    logging into the same file, it is recommended to use
    [`${HOSTNAME}`](../../configuration/#environment-variables) variable in the file path:

    ```ini
    [logging:file]
    path=/var/log/${HOSTNAME}/asab.log
    ```

    In this way, the applications will log to separate log files in
    different folders, which is an intended behavior, since race conditions
    may occur when different application instances log into the same file.

## Log rotation

ASAB supports a [log rotation](https://en.wikipedia.org/wiki/Log_rotation). 
The log rotation is triggered by a UNIX signal `SIGHUP`, which can be used e.g. to integrate with `logrotate` utility.
It is implemented using [`logging.handlers.RotatingFileHandler`](https://docs.python.org/3/library/logging.handlers.html#baserotatinghandler) from the Python standard library.
Also, a time-based log rotation can be configured using `rotate_every` option.

| Option | Meaning |
| --- | --- |
| `backup_count` | A number of old files to be kept prior their removal. The system will save old log files by appending the extensions '.1', '.2' etc., to the filename. |
| `rotate_every` | Time interval of a log rotation. Default value is empty string, which means that the time-based log rotation is disabled.  The interval is specified by an integer value and an unit, e.g. 1d (for 1 day) or 30M (30 minutes). Known units are `H` for hours, `M` for minutes, `d` for days and `s` for seconds.|


## Logging to syslog


The command-line argument `-s` enables logging to syslog.

A configuration section `[logging:syslog]` can be used to specify
details about desired syslog logging.

Example of the configuration file section:

```ini
[logging:syslog]
enabled=true
format=5
address=tcp://syslog.server.lan:1554/
```

- `enabled` is equivalent to command-line switch `-s` and it enables syslog logging target.

- `format` specifies which logging format will be used.

| Option | Format | Note | 
| --- | --- | --- | 
| `5` | syslog format [RFC 5424](https://tools.ietf.org/html/rfc5424) |  |
| `5micro` | syslog format RFC 5424 with microseconds | |
| `3` | the old BSD syslog format [RFC 3164](https://tools.ietf.org/html/rfc3164) | It is typically used by `/dev/log`. |
| `m` | Mac OSX syslog flavour | It is based on BSD syslog format but it is not fully compatible. |

The default value is `3` on Linux and `m` on Mac OSX.

- `address` specifies the location of the Syslog server. It could be a UNIX path such as `/dev/log` or URL. Possible URL values:

-   `tcp://syslog.server.lan:1554/` for Syslog over TCP
-   `udp://syslog.server.lan:1554/` for Syslog over UDP
-   `unix-connect:///path/to/syslog.socket` for Syslog over UNIX socket
    (stream)
-   `unix-sendto:///path/to/syslog.socket` for Syslog over UNIX socket
    (datagram), equivalent to `/path/to/syslog.socket`, used by a
    `/dev/log`.

The default value is a `/dev/log` on Linux or `/var/run/syslog` on Mac OSX.

## Logging of obsolete features

It proved to be essential to inform operators about features that are going to be obsoleted.
ASAB offers the unified `asab.LogObsolete` logger which can indicate that a particular feature is marked as *obsolete* thru logs.
Such a log message can then be *grepped* from logs uniformly.

!!! example

    ```python
    asab.LogObsolete.warning("Use of the obsolete function", struct_data={'eol':'2022-31-12'})
    ```

    produces the output:

    ```
    21-Jul-2022 14:32:40.983884 WARNING OBSOLETE [eol="2022-31-12"] Use of the obsolete function
    ```

    We suggest to add the `eol` attribute in the `struct_data` of the log with a `YYYY-MM-DD`
    date/time of the planned *end of life* of the feature.

!!! tip

    We suggest automating the detection of obsolete warnings in logs
    so that the operations are informed well ahead of the actual removal of
    the feature. The string to seek in logs is "OBSOLETE".

## Reference

### Command-line arguments

| Argument | Action |
| --- | --- |
| `-v` | Enables verbose logging so that `DEBUG` and `INFO` levels are visible. |
| `-s`| Enables logging to syslog. |


::: asab.log.LOG_NOTICE

::: asab.log.Logging

