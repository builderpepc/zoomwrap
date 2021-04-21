import requests
try:
    import ujson as json
except:
    import json
from typing import List, Union, Iterable, Sequence
try:
    import regex as re
except:
    import re
import datetime
import traceback

URL_REGEX = re.compile(r"^(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)?[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?$")
URL_WITH_PROTOCOL_REGEX = re.compile(r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#()?&//=]*)")

def send_rich_msg(data: dict, endpoint: str, auth: str, verbose: bool = True):
    r = requests.post(endpoint+"?format=full",
        data=json.dumps(data),
        headers = {
            'Authorization': auth,
            'Content-Type': 'application/json'
        }
    )
    try:
        r.raise_for_status()
    except:
        if verbose:
            traceback.print_exc()
            print("Response: " + r.text)
        else:
            r.raise_for_status()


def check_text(text: str):
    if isinstance(text, str) and not bool(text):
        raise ValueError("Any text cannot be an empty string. Use a space instead?")
        
def check_url(url: str, mode: str = "any"):
    return isinstance(url, str) and (mode == "with-prefix" or re.match(URL_REGEX, url) != None) and (mode == "any" or re.match(URL_WITH_PROTOCOL_REGEX, url) != None)

class Style:
    def __init__(self, color: str = None, bold: bool = False, italic: bool = False):
        self.color = color # Hex color with '#' symbol
        self.bold = bold
        self.italic = italic

    def to_dict(self):
        ret = {'bold': self.bold, 'italic': self.italic}
        if self.color != None:
            ret['color'] = self.color
        
        return ret
        
class exceptions:

    class MissingComponentError(BaseException):
        """
        Raised when an optional argument is provided that depends on another optional argument that is not provided.
        """
        pass

class bodyElements:

    class Text:
        # In Zoom's docs, this type is called "message"
        def __init__(self, text: str, link: str = None, style: Style = None, editable: bool = False):
            self.text = text
            self.style = style
            self.editable = editable
            self.link = link
            
            self.validate()

        def validate(self):
            check_text(self.text)

            if isinstance(self.link, str):
                if (not self.link.startswith("http://")) and (not self.link.startswith("https://")):
                    self.link = "http://" + self.link
                if not check_url(self.link, mode="with-prefix"):
                    raise ValueError("Text link must be a valid URL with protocol; was given \"{}\"".format(self.link))

            elif self.link != None:
                raise TypeError("Text link must be a string")

            if self.style != None and not isinstance(self.style, Style):
                raise TypeError("Text style must be a Style object")

            if not isinstance(self.editable, bool):
                raise TypeError("Text editability must be a boolean")

        def to_dict(self):
            self.validate()

            ret = {'type': 'message', 'text': self.text, 'editable': self.editable}
            if self.style != None:
                ret['style'] = self.style.to_dict()

            if self.link != None:
                ret['link'] = self.link

            return ret

    class Attachment:
        def __init__(self, resource_url: str, img_url: str, title: str, titleStyle: Style = None, description: str = None, descriptionStyle: str = None, ext: str = None, size: int = None):
            self.resource_url = resource_url
            self.img_url = img_url
            self.title = title
            self.titleStyle = titleStyle
            self.description = description
            self.descriptionStyle = descriptionStyle
            self.ext = ext
            if isinstance(self.ext, str):
                self.ext = self.ext.lower()
            self.size = size # In bytes

            self.validate()

        def validate(self):

            if (not check_url(self.resource_url)) or (not check_url(self.img_url)):
                raise ValueError("resource_url and img_url must be valid URLs")

            if self.ext != None and not isinstance(self.ext, str):
                raise TypeError("Attachment extension must be a string")

            VALID_EXTENSIONS = ['pdf', 'txt', 'doc', 'xlsx', 'zip', 'jpeg', 'png']
            if self.ext != None and (self.ext not in VALID_EXTENSIONS):
                raise ValueError("Attachment extension must be one of the following strings: " + str(VALID_EXTENSIONS))

            if self.descriptionStyle != None and self.description == None:
                raise exceptions.MissingComponentError("Style for a description was given, but no description was provided")

            if not isinstance(self.title, str):
                raise TypeError("Attachment title must be a string")

            if self.description != None and not isinstance(self.description, str):
                raise TypeError("Attachment description must be a string")

            if self.titleStyle != None and not isinstance(self.titleStyle, Style):
                raise TypeError("Attachment title style must be a Style object")

            check_text(self.title)
            if isinstance(self.description, str):
                check_text(self.description)

            if self.descriptionStyle != None and not isinstance(self.descriptionStyle, Style):
                raise TypeError("Attachment description style must be a Style object")

            if self.size != None and not isinstance(self.size, int):
                raise TypeError("Attachment size must be an integer")

        def to_dict(self):
            self.validate()

            ret = {'type': 'attachments', 'resource_url': self.resource_url, 'img_url': self.img_url, 'information': {'title': {'text': self.title} } }

            if self.titleStyle != None:
                ret['information']['title']['style'] = self.titleStyle.to_dict()

            if self.description != None:
                ret['information']['description'] = {}
                ret['information']['description']['text'] = self.description

                if self.descriptionStyle != None:
                    ret['information']['description']['style'] = self.descriptionStyle.to_dict()

            if self.ext != None:
                ret['information']['ext'] = self.ext

            if self.size != None:
                ret['information']['size'] = self.size

            return ret

    class Section:
        def __init__(self, elements: Sequence['bodyElements'], sidebar_color: str = None, footer: 'bodyElements.Section.Footer' = None):
            self.elements = elements
            if any(isinstance(x, type(self)) for x in self.elements):
                raise ValueError("Section elements cannot be sections")
            self.sidebar_color = sidebar_color
            self.footer = footer

            self.validate()

        class Footer:
            def __init__(self, text: str = None, icon_url: str = None, unix_timestamp: Union[datetime.datetime, int, float] = None):
                self.text = text
                self.icon_url = icon_url
                self.unix_timestamp = unix_timestamp

                self.validate()

            def validate(self):
                check_text(self.text)
                if self.icon_url != None and not check_url(self.icon_url):
                    raise ValueError("Section footer icon url must be a valid URL")
                
                if self.unix_timestamp != None and (not isinstance(self.unix_timestamp, int)) and (not isinstance(self.unix_timestamp, float)):
                    if isinstance(self.unix_timestamp, datetime.datetime):
                        pass
                    else:
                        try:
                            test_timestamp = int(float(self.unix_timestamp))
                        except:
                            raise TypeError("Section footer timestamp must be a datetime.datetime or an integer (date in milliseconds)")

                            

            def to_dict(self):
                self.validate()

                ret = {}

                if self.text != None:
                    ret['footer'] = self.text

                if self.icon_url != None:
                    ret['footer_icon'] = self.icon_url

                if self.unix_timestamp != None:
                    if not isinstance(self.unix_timestamp, datetime.datetime):
                        ret['ts'] = int(float(self.unix_timestamp))
                    else:
                        ret['ts'] = int(datetime.datetime.timestamp(self.unix_timestamp) * 1000)

                return ret

        def validate(self):
            if (not isinstance(self.elements, Sequence)) or isinstance(self.elements, str):
                raise TypeError("Section elements must be a sequence of bodyElements subclasses")

            else:
                if len(self.elements) < 1:
                    raise ValueError("Sections require at least one element")

            VALID_SECTION_ELEMENTS = [bodyElements.Text, bodyElements.Attachment, bodyElements.Fields]
            if any(x not in VALID_SECTION_ELEMENTS for x in VALID_SECTION_ELEMENTS):
                raise TypeError("Section elements must be one of the following: " + ', '.join([str(z) for z in VALID_SECTION_ELEMENTS]))

            if self.footer != None:
                if not isinstance(self.footer, bodyElements.Section.Footer):
                    raise TypeError("Section footer must be an instance of bodyElements.Section.Footer")

                self.footer.validate()

        def to_dict(self):
            self.validate()

            ret = {'type': 'section', 'sections': []}

            if self.sidebar_color != None:
                ret['sidebar_color'] = self.sidebar_color

            if self.footer != None:
                ret.update(self.footer.to_dict())

            for x in self.elements:
                ret['sections'].append(x.to_dict())
            
            return ret

    class Fields:
        def __init__(self, items: Sequence['bodyElements.Fields.Field'] = []):
            self.items = items

        class Field:
            def __init__(self, key, value, short: bool = None, editable: bool = False, style: Style = None):
                self.key = key
                self.value = value
                self.short = short # Unsure what this does, but it is in Zoom's documentation
                self.editable = editable
                self.style = style

            def to_dict(self):
                ret = {'key': self.key, 'value': self.value, 'editable': self.editable}

                if self.short != None:
                    ret['short'] = self.short

                if self.style != None:
                    ret['style'] = self.style.to_dict()

                return ret

        def to_dict(self):
            ret = {'type': 'fields', 'items': []}
            for x in self.items:
                ret['items'].append(x.to_dict())

            return ret

class messageElements:

    class SubHead:
        def __init__(self, text: str, style: Style = None):
            self.text = text
            self.style = style

        def to_dict(self):
            ret = {'text': self.text}
            if self.style != None:
                ret['style'] = self.style.to_dict()

            return ret

    class Head:
        def __init__(self, text: str, style: Style = None, sub_head: 'messageElements.SubHead' = None):
            self.text = text
            self.style = style
            self.sub_head = sub_head

        def to_dict(self):
            ret = {'text': self.text}
            if self.style != None:
                ret['style'] = self.style.to_dict()

            if self.sub_head != None:
                ret['sub_head'] = self.sub_head.to_dict()

            return ret

    class Body:
        def __init__(self, elements: Sequence[bodyElements] = []):
            self.elements = elements

        def to_dict(self):
            ret = []
            for x in self.elements:
                ret.append(x.to_dict())

            return ret

class Message:
    def __init__(self, allow_markdown: bool = False, head: messageElements.Head = None, body: messageElements.Body = None):
        self.allow_markdown = allow_markdown
        self.head = head
        self.body = body

    def to_dict(self):
        ret = {'content': {}}
        if self.head != None:
            ret['content']['head'] = self.head.to_dict()

        if self.allow_markdown == True:
            ret['is_markdown_support'] = True
        
        if self.body != None:
            body = []
            for x in self.body.elements:
                body.append(x.to_dict())
            ret['content']['body'] = body

        return ret

class WebhookClient:
    def __init__(self, endpoint: str, auth: str):
        if not check_url(endpoint):
            raise ValueError("Endpoint is not a valid URL")
        
        self.endpoint = endpoint
        self.auth = auth

    def send(self, message: Message):

        #if isinstance(message.body, messageElements.Body) and message.head == None and any(isinstance(x, bodyElements.Fields) for x in message.body.elements):
        #    raise ValueError("Fields element requires a message header")

        send_rich_msg(message.to_dict(), self.endpoint, self.auth)

    def send_raw(self, message: dict):
        send_rich_msg(message, self.endpoint, self.auth)

