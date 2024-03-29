# Creating a web server


Now that know how to create and run [a basic ASAB application](./installation_first_app.md), you can create your first web server.

## Creating and running a web server

Set up a new project and create a new file `app.py` with the following code:

``` python title="app.py"

#!/usr/bin/env python3
import asab.web.rest

class MyWebApplication(asab.Application):

    def __init__(self):
        super().__init__()

        # Create the Web server
        web = asab.web.create_web_server(self)

        # Add a route to the handler method
        web.add_get('/hello', self.hello)

    # This is the web request handler
    async def hello(self, request):
        return asab.web.rest.json_response(
            request,
            data="Hello, world!"
        )

if __name__ == '__main__':
    app = MyWebApplication()
    app.run()

```

You can run the new application with the command:

``` bash
python3 app.py
```


The ASAB web server is now available at [http://localhost:8080/](http://localhost:8080/).

??? note "What is http://localhost:8080?"

    In case you don't know, **localhost** refers to the loopback network interface address of a device, usually represented as the IP address 127.0.0.1. It is used to refer to the device itself, allowing software to communicate with services running on the same device. In simpler terms, it's like talking to yourself within a computer to access and test applications or websites without going online.

    `:8080` refers to a port. A **port** is a communication endpoint in a computer network. It is represented by a numeric value, in this case 8080, and it allows applications and services to establish connections and exchange data. Ports enable the proper routing and delivery of network traffic, ensuring that information reaches the intended destination within a device or across different devices on a network.

Now open your web browser and open [http://localhost:8080/](http://localhost:8080/). You'll see the error:

``` bash
404: Not Found
```

That is correct, because the endpoint "/" is not handled by the router. But now, if you open [http://localhost:8080/hello](http://localhost:8080/hello), you should see the response:

``` json
"Hello world!"
```

You can get the same result from a terminal using the cURL command:

``` bash
curl --location 'localhost:8080/hello'
```

## Taking a closer look

Let's examine the code to understand how the ASAB server is constructed.

Click on the :material-plus-circle: icons to learn what each line of code means.

``` python title="app.py" linenums="1"

#!/usr/bin/env python3
import asab.web.rest # (1)!

class MyWebApplication(asab.Application):

    def __init__(self):
        super().__init__() # (2)!

        # Create the Web server
        web = asab.web.create_web_server(self) # (3)!

        # Add a route to the handler method
        web.add_get('/hello', self.hello) # (4)!

    # This is the web request handler
    async def hello(self, request): # (5)!
        return asab.web.rest.json_response( # (6)!
            request,
            data="Hello, world!"
        )

if __name__ == '__main__':
    app = MyWebApplication()
    app.run()

```

1. Let's start by importing the `asab.web.rest` module. Note that this enables calling functions from `asab` and `asab.web` modules.

2. As you will see later, `asab.Application` has a lifecycle with three phases. This time, we have modified the initialization of the application. In order not to completely override the whole application initialization, call the `super.__init__()` method.

3. The `asab.web` module provides a `create_web_server()` method that
simplifies creation of the web server in the ASAB application. It returns an object, which is used as a router to which you can add new routes.

4. With the `add_get()` method, you can define a new route that requests can be sent to. If you now access the web server with the path `/hello`, it will be handled by a `hello()` method. In other words, the `hello()` method is installed in the web server at the `/hello` endpoint with the `GET` HTTP method. Similar methods for `PUT`, `POST`, and `DELETE` methods exist, as we will see in the next tutorial.

5. This is a handler method, which is called by the router when a `GET` request is send to a `/hello` endpoint. Every handler method must be a coroutine! That means, it has to be defined with `async def` keyword. You have to include the `request` argument, even if you (for some peculiar reason) don't want to use it in the function body. Otherwise it won't work together with the `add_get()` method.

6. The `asab.web.rest` module provides a `json_response()` method that simply sends back any data you want to the client in JSON format. In this case, the output is just a single string, but it could be any JSON-serializable document.


As you can see, it is easy to create a fully functioning web server using ASAB, so that you can concentrate more on the application logic. 
`asab` is built on the top of the [asyncio](https://docs.python.org/3/library/asyncio.html) and [aiohttp](https://docs.aiohttp.org/en/stable/) libraries which are designed to make the most out of [non-blocking network operations](https://docs.aiohttp.org/en/stable/http_request_lifecycle.html#aiohttp-request-lifecycle).


## Logging


At this point, let us also mention the basics of ASAB logging.

ASAB applications provide a structured logging tool, which is used to trace back useful information about various events during the application run-time.

The default configuration sends logs to the standard output, so you can see the logs directly in the terminal. If you want to add your a different logger or send logs to a different output, you need to change the configuration.

If you check the terminal where an ASAB application is running, you should see messages similar to these:

``` python
23-Jun-2023 08:08:44.683943 NOTICE asab.application is ready. # (1)
23-Jun-2023 08:18:04.116786 NOTICE asab.web.al [sd I="127.0.0.1" ...] # (2)
```

1. This log informs you that the initialization of the application is finished. It means that configuration is loaded, logging is set up, the event loop is constructed, etc.

2. This log is displayed every time a valid HTTP request is processed. 
If you deconstruct the message, you learn what request method was used, what application sent the request, the response status code, etc.


If you stop the application using `Control+C`, another log shows up:

``` python
23-Jun-2023 08:32:23.292862 NOTICE asab.application is exiting ... #(1)!
```

1. This log informs you that the application is in exit-time. 
Note that there may be processes that take a long time to terminate, so terminating an application might take a noticeably long time.

ASAB uses a formatted logger on top of [the standard logging library](https://docs.python.org/3/library/logging.html) provided with utilities such as

- Colors indicating the log level
- Structured data formatting
- Log rotation
- Logging to syslog

## Configuration

In order to start your ASAB application with certain configuration, create a config file in `ini` format.

``` ini title="config.ini"
[web]
listen=0.0.0.0:7000

[logging]
level=DEBUG

[logging:file]
path=./log.txt
```

Now if you run the application with this configuration file:
``` bash
python app.py -c config.ini
```
You should see some differences:

- Now, your web server is running on [http://localhost:8000](http://localhost:8000)
- Logging is set to another level and it is stored in a file `log.txt`


Finally, go to the [next tutorial](../how-tos/03_rest_api.md) where we create a microservice with REST API.