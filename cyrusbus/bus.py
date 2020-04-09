# pylint: disable-all
#!/usr/bin/env python3


class Bus:

    _instances = {}

    def __init__(self, name=None):
        if name:
            Bus._instances[name] = self
        self.reset()

    @staticmethod
    def get_or_create(name):
        """
        Gets a specific bus instance or creates a new instance and returnes this one if no instance with the name was given.

        :param name: The name of the bus instance which should be returned.
        :return: The bus instance with the given name.
        """
        bus = Bus.get_bus(name)

        if bus is None:
            return Bus(name)

        return bus

    @staticmethod
    def get_bus(name):
        """
        Returns a bus instance with the given name. If no bus instance was found None is returned.

        :param name: The name of the bus instance that should be returned.
        :return: The bus instance that was created with the given name or None if the name given is not connected with a bus.
        """
        return Bus._instances.get(name)

    @staticmethod
    def get_bus_name(instance):
        """
        Returns the bus name of an given bus instance.

        :param instance: The bus, which name should be returned.
        :return: The name of the bus instance.
        """
        for instances_key, bus_instance in Bus._instances.items():
            if instance is bus_instance:
                return instances_key
        return None

    @staticmethod
    def delete_bus(name):
        """
        Deletes a specific bus with the given name.

        :param name: The name of the bus instance.
        :return: True if the bus was successfully deleted.
        """

        try:
            del Bus._instances[name]
        except KeyError:
            raise KeyError("Bus called {} not found".format(name))


    def subscribe(self, key, callback, force=False):
        """
        This method subscribes an function to an eventkey.

        :param key: The event key. When someone published an event with the same key, this subscription will be triggered. Special key '*' can be used to subscribe to all events.
        :param callback: The callback function. This function will be executed when the given event is published.
        :param force: Force insert to execution queue. If True: the callback will be executed, even if the callback is subscribed more than once.
        :return: The busobject.
        """
        if key not in self.subscriptions:
            self.subscriptions[key] = []

        subscription = {
            'key': key,
            'callback': callback
        }

        if force or not self.has_subscription(key, callback):
            self.subscriptions[key].append(subscription)

        return self

    def unsubscribe(self, key, callback):
        """
        This method unsubscribes an function of the given eventkey.

        :param key: The event key.
        :param callback: The callback function.
        """
        if not self.has_subscription(key, callback):
            return self

        self.subscriptions[key].remove({
            'key': key,
            'callback': callback
        })

    def unsubscribe_all(self, key):
        """
        This method unsubscribes all callback functions of the given eventkey.

        :param key: The event key. When someone published an event with the same key, this subscription will be triggered.
        """
        if key not in self.subscriptions:
            return self

        self.subscriptions[key] = []

    def has_subscription(self, key, callback):
        """
        This method shows whether a function has subscriptions or not.

        :param key: The event key.
        :param callback: The callback function.
        :return: True if there is an subscription.
        """
        if key not in self.subscriptions:
            return False

        subscription = {
            'key': key,
            'callback': callback
        }

        return subscription in self.subscriptions[key]

    def has_any_subscriptions(self, key):
        """
        This method shows whether an eventkey has any subscriptions or not.

        :param key: The event key.
        :return: True if there are subscribers.
        """
        return key in self.subscriptions and len(self.subscriptions[key]) > 0

    def publish(self, key, *args, **kwargs):
        """
        Publishes an event. All subscribers to the event will be called.

        :param key: The event key to which the subscriptions should be triggered.
        :param *args: Additional arguments to give the callback functions.
        """
        if '*' in self.subscriptions:
            for subscriber in self.subscriptions['*']:
                subscriber['callback'](self, key, *args, **kwargs)

        key_found = False

        # iterate over all subscriptions and check to see whether we have any
        # matches between the specified key and any 
        for subscriber_key in self.subscriptions.keys(): # look through all keys in the dictionary
            if key.startswith(subscriber_key):           # see if given subscription matches any portion from start of key
                key_found = True
                for subscriber in self.subscriptions[subscriber_key]:
                    subscriber['callback'](self, *args, **kwargs)

        if not key_found:
            return self

    def reset(self):
        """
        Resets the eventbus. All subscribers will be cleared.
        """
        self.subscriptions = {}


    def __repr__(self):
        return "<Bus '{}' id '{}'>".format(Bus.get_bus_name(self), hex(id(self)))
