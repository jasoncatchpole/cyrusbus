Introduction
------------

CyrusBus is a VERY lightweight publish/subscribe event bus for python applications.

It is worth noting that CyrusBus is 100% independent from other libraries and is 100% covered by tests. If you want to see how to use it (besides this documentation) just check the tests.

Installing CyrusBus
-------------------

You can install CyrusBus from PyPI (http://pypi.python.org/pypi), using PIP::

    pip install cyrusbus

That should be it. To verify it's installed, open the python interpreter and type::

    >>> import cyrusbus
    >>> cyrusbus.__version__
    '0.1.0'

Using CyrusBus
--------------

Using CyrusBus is as easy as it gets.

Import the Bus in your application::

    from cyrusbus import Bus

Create a new instance of the bus::

    bus = Bus()

Then start calling the methods as explained below.

Subscribe
=========

Subscribing is what allows you to handle events that go through the bus. You can subscribe to events using this syntax::

    bus.subscribe("event.key", callback)

The first parameter is the event key, meaning that when someone publishes an event with the same key, this subscription will be triggered.

The second parameter is the callback function. This is the function that will get executed when the given event is published. This function will be called with whatever arguments the publisher sent (the arguments will be unpacked). The callback function will also receive the bus as the first argument. It should have this form::

    def my_callback(self, bus, whatever, arguments, your, function, requires):
        //does something with the arguments.

.. warning::

    If you call subscribe twice with the same callback, CyrusBus will ignore the second call. The reason for this is because of duplicate callbacks to events. It's very puzzling, error-prone and hard to track when the message bus calls your callback twice or more. If you actually need your callback to be called two, three or n times, use the argument force, as explained below.

You can also supply a third parameter called force. This parameter is useful if you want to subcribe to something twice. This means that cyrusbus will call your callback method as many times as you subscribe. Just use this syntax::

    bus.subscribe("event.key", callback, force=True)

You can also subscribe to all events on the bus by using event key ``"*"``::

    bus.subscribe("*", my_callback)

Catch all event callback also gets the event key as its second argument::

    def my_callback(self, bus, key, whatever, arguments, your, function, requires):
        //does something with the arguments.

Unsubscribe
===========

In order to unsubscribe to a previously subscribed event, all you have to do is call on::

    bus.unsubscribe('event.key', callback)

The callback argument is needed so we can unsubscribe only your call. Since both subscribe and unsubscribe return the bus you can call::

    bus.unsubscribe('event.key', callback).subscribe('my_event_reference', callback)

Even though this is possible, it's not needed as subscribe will ignore any subsequent calls to it with the same subject and callback.

What if I want to unsubscribe all subscribers to a given event? You just call::

    bus.unsubscribe_all('event.key')


Find out if an event has been subscribed
========================================

If you subscribed to an event (refer to subscribe for more details), you can find out if it the subscription is active using has_subscription, like this::

    bus.has_subscription('event.key', callback)

Or if you want to know if the event has any subscribers, just call::

    bus.has_any_subscriptions('event.key')

Both return True if there are subscribers that meet the criteria or False otherwise.

Publish
=======

Publishing is the process that triggers all subscriptions to the given message. You can publish an event using this syntax::

    bus.publish("event.key", some="key", has="some", cool="value");

The first parameter is the event key, meaning that all subscriptions to this key should be triggered.

The arguments that will be passed to the event should be passed as arguments or keyword-arguments.

Reset
=====

Resetting the bus has proven very useful in the tests. Since it's already implemented we'll document it here. Resetting the bus means it "forgets" all subscriptions. You can reset the bus using this syntax::

    bus.reset();
    
The subscription hierarchy
=====

Another mode of operation supported is to exploit a hierarchy of subscriptions. This is best shown by an example::

    def my_level1a_callback(self, bus, whatever, arguments, your, function, requires):
        //Called for any level1a event
        
    def my_level2a_callback(self, bus, whatever, arguments, your, function, requires):
        //Called for any level2a event
        
    def my_level3a_callback(self, bus, whatever, arguments, your, function, requires):
        //Called for any level3a event
        
    // setup all the subscribes
    bus.subscribe("level1a", my_level1a_callback)
    bus.subscribe("level1a.level2a", my_level2a_callback)
    bus.subscribe("level1a.level2a.level3a", my_level3a_callback)
    
At this point we perform some publish operations and indicate which callbacks are called::

    // only "my_level1a_callback" will be called
    bus.publish("level1a", some="key", has="some", cool="value")
    
    // "my_level1a_callback" AND "my_level2a_callback" will be called
    bus.publish("level1a.level2a", some="key", has="some", cool="value")
    
    // "my_level1a_callback", "my_level2a_callback", AND "my_level3a_callback" will be called
    bus.publish("level1a.level2a.level3a", some="key", has="some", cool="value")
    
    // Only "my_level1a_callback" will be called as "level2b" does not match "level2a" for "my_level2a_callback"
    bus.publish("level1a.level2B", some="key", has="some", cool="value")
    
Only the start of the publish key matters when matching against a subscription. For example::

    // Only "my_level1a_callback" will be called
    bus.publish("level1a.BUT_NOT.level2a.level3a", some="key", has="some", cool="value")

Feature Request, Suggestions, Feedback
--------------------------------------

If you want to contribute with the project, even if it's just to ask for something not implemented yet, just contact me through GitHub or create an issue here in the project's repository.
