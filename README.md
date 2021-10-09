# zoomwrap

A module containing classes that can be easily serialized to JSON for use with Zoom's APIs.

⚠️*This code still works, but was written poorly at a time when I was not as familiar with how Python modules are structured and written. Please keep this in mind if you use this package (and feel free to improve it).*

```py
import zoomwrap

client = zoomwrap.WebhookClient("your_endpoint_url", "your_auth_str")

msg = zoomwrap.Message(head=zoomwrap.messageElements.Head("hello, world"))
client.send(msg)

```

I have only tested this with Zoom's [incoming webhook API](https://zoomappdocs.docs.stoplight.io/incoming-webhook-chatbot) but it should work with the Chatbot API as well since they use the same object structures.

For convenience, there is a `WebhookClient` class with methods for sending API requests using your credentials. 

## Documentation
Currently, there is no documentaion for this module because it is still a heavy work in progress.  
For now, have a loop at Zoom's [incoming webhook API docs](https://zoomappdocs.docs.stoplight.io/incoming-webhook-chatbot) and their more detailed docs for both the Chatbot and Webhook APIs [here](https://marketplace.zoom.us/docs/guides/chatbots/customizing-messages).  
Most of the different types of messages and their attributes have been implemented in this module, with the exception of messages with buttons, because they only work with the Chatbot API.

## Contributions
This is my first pypi package and it is not very sophisticated (or neat, for that matter).
Contributions are certainly welcome but may not get checked often.
