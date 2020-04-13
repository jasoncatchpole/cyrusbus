# pylint: disable-all
#!/usr/bin/env python3

import unittest
import threading
import time
from cyrusbus import Bus


class TestBus(unittest.TestCase):
    def callback(self, bus, argument):
        self.called_bus = bus
        self.has_run = True
        self.argument = argument
        self.callback_count = self.callback_count + 1

    def setUp(self):
        self.bus = Bus()
        self.reset_test()

    def reset_test(self):
        self.has_run = False
        self.called_bus = None
        self.argument = ""
        self.callback_count = 0

    def test_can_haz_bus(self):
        assert self.bus

    def test_has_no_subscriptions(self):
        assert not self.bus.subscriptions

    def test_subscribe_is_chainable(self):
        bus = self.bus.subscribe('test.key', self.callback)
        assert bus == self.bus

    def test_can_subscribe_to_event(self):
        self.bus.subscribe('test.key', self.callback)
        expected = [{ 'key': 'test.key', 'callback': self.callback }]

        assert 'test.key' in self.bus.subscriptions
        assert self.bus.subscriptions['test.key']
        assert expected == self.bus.subscriptions['test.key']

    def test_subscribing_twice_with_same_subject_and_callback_ignores_second_call(self):
        self.bus.subscribe('test.key', self.callback).subscribe('test.key', self.callback)

        assert len(self.bus.subscriptions['test.key']) == 1, len(self.bus.subscriptions['test.key'])

    def test_subscribing_by_force(self):
        self.bus.subscribe('test.key', self.callback).subscribe('test.key', self.callback, force=True)

        assert len(self.bus.subscriptions['test.key']) == 2, len(self.bus.subscriptions['test.key'])

    def test_subscribe_to_all_events(self):
        self.bus.subscribe('*', self.callback)

        self.bus.publish('test.key1')
        assert self.has_run and self.argument == 'test.key1'

        self.has_run = False
        self.bus.publish('test.key2')
        assert self.has_run and self.argument == 'test.key2'


    def test_unsubscribe_is_chainable(self):
        bus = self.bus.unsubscribe('test.key', self.callback)
        assert bus == self.bus

    def test_unsubscribe_to_invalid_subject_does_nothing(self):
        self.bus.unsubscribe('test.key', self.callback)

        assert 'test.key' not in self.bus.subscriptions

    def test_unsubscribe_to_invalid_callback_does_nothing(self):
        self.bus.subscribe('test.key', self.callback)
        self.bus.unsubscribe('test.key', lambda obj: obj)

        assert len(self.bus.subscriptions['test.key']) == 1, len(self.bus.subscriptions['test.key'])

    def test_can_unsubscribe_to_event(self):
        self.bus.subscribe('test.key', self.callback).unsubscribe('test.key', self.callback)

        assert len(self.bus.subscriptions['test.key']) == 0, len(self.bus.subscriptions['test.key'])

    def test_unsubscribe_all_does_nothing_for_nonexistent_key(self):
        self.bus.subscribe('test.key', self.callback)
        self.bus.unsubscribe_all('other.key')

        assert len(self.bus.subscriptions['test.key']) == 1, len(self.bus.subscriptions['test.key'])

    def test_unsubscribe_all_is_chainable(self):
        bus = self.bus.unsubscribe_all('test.key')
        assert bus == self.bus

    def test_unsubscribe_all(self):
        self.bus.subscribe('test.key', self.callback)
        self.bus.subscribe('test.key', lambda obj: obj)

        self.bus.unsubscribe_all('test.key')

        assert len(self.bus.subscriptions['test.key']) == 0, len(self.bus.subscriptions['test.key'])

    def test_has_subscription(self):
        self.bus.subscribe('test.key', self.callback)

        assert self.bus.has_subscription('test.key', self.callback)

        self.bus.unsubscribe('test.key', self.callback)

        assert not self.bus.has_subscription('test.key', self.callback)

    def test_does_not_have_subscription_for_invalid_key(self):
        assert not self.bus.has_subscription('test.key', self.callback)

    def test_does_not_have_subscription_for_invalid_calback(self):
        self.bus.subscribe('test.key', self.callback)

        assert not self.bus.has_subscription('test.key', lambda obj: obj)

    def test_has_any_subscriptions_for_invalid_key(self):
        assert not self.bus.has_any_subscriptions('test.key')

    def test_has_any_subscriptions(self):
        self.bus.subscribe('test.key', self.callback)

        assert self.bus.has_any_subscriptions('test.key')

        self.bus.unsubscribe('test.key', self.callback)

        assert not self.bus.has_any_subscriptions('test.key')

    def test_can_publish(self):
        self.bus.subscribe('test.key', self.callback)

        self.bus.publish('test.key', argument="something")

        assert self.has_run
        assert self.argument == "something"
        assert self.called_bus == self.bus

    def test_can_publish_with_noone_listening(self):
        self.bus.publish('test.key', something="whatever")

    def test_publish_is_chainable(self):
        bus = self.bus.publish('test.key', something="whatever")
        assert bus == self.bus

    def test_subscribing_to_different_keys(self):
        self.bus.subscribe('test.key', self.callback)
        self.bus.subscribe('test.key2', self.callback)
        self.bus.subscribe('test.key3', self.callback)

        assert 'test.key' in self.bus.subscriptions
        assert 'test.key2' in self.bus.subscriptions
        assert 'test.key3' in self.bus.subscriptions

        assert self.bus.subscriptions['test.key']
        assert self.bus.subscriptions['test.key2']
        assert self.bus.subscriptions['test.key3']

    def test_can_reset_bus(self):
        self.bus.subscribe('test.key', self.callback)
        self.bus.subscribe('test.key2', self.callback)
        self.bus.subscribe('test.key3', self.callback)

        self.bus.reset()

        assert 'test.key' not in self.bus.subscriptions
        assert 'test.key2' not in self.bus.subscriptions
        assert 'test.key3' not in self.bus.subscriptions

    def test_only_one_instance_of_the_bus(self):
        bus_a = Bus.get_or_create('bus_a')
        bus_b = Bus.get_bus('bus_a')
        bus_c = Bus.get_or_create('bus_c')
        bus_d = Bus()

        assert bus_a is bus_b
        assert bus_a is not bus_c
        assert bus_d is not bus_a

    def test_get_or_create_only_once(self):
        bus_a = Bus.get_or_create('bus_a')
        bus_b = Bus.get_or_create('bus_a')

        assert bus_a is bus_b

    def test_delete_bus_instances(self):
        bus_x = Bus.get_or_create('bus_x')

        assert bus_x in Bus._instances.values()

        Bus.delete_bus('bus_x')

        assert bus_x not in Bus._instances.values()

        with self.assertRaises(KeyError):
            Bus.delete_bus('bus_x')

    def test_bus_is_not_specific(self):
        bus_y = Bus()
        bus_z = Bus.get_or_create('bus_z')

        assert bus_y is not bus_z

    def test_get_bus_name_none(self):
        bus_name = Bus.get_bus_name(self.bus)
        assert bus_name is None

    def test_get_bus_name_string(self):
        bus_x = Bus('bus_x')
        assert Bus.get_bus_name(bus_x) == 'bus_x'

    def test_subkey_subscriptions_simple(self):
        self.bus.subscribe('level1a.level2a', self.callback)

        # we have subscribed to a parent level thus we should receive this publish
        self.bus.publish('level1a.level2a.level3a', argument="something")

        assert self.has_run
        assert self.argument == "something"
        assert self.called_bus == self.bus
        assert self.callback_count == 1

    def test_subkey_subscriptions_no_start_match(self):
        # make sure that we only get publishes if the start of the key is an exact match
        self.reset_test()

        self.bus.subscribe('level1a.level2a', self.callback)
        self.bus.publish('blah.level1a.level2a.level3a', argument="something")

        assert not self.has_run
        assert self.argument == ""
        assert self.called_bus == None
        assert self.callback_count == 0

    def test_subkey_subscriptions_complex(self):
        self.reset_test()
        self.bus.subscribe('level1a.level2a', self.callback)
        self.bus.subscribe('level1a.level2a.level3a', self.callback)
        self.bus.subscribe('level1a.level2a.level3b', self.callback)

        # we have subscribed to a parent level thus we should receive this publish
        self.bus.publish('level1a.level2a.level3a', argument="something")

        assert self.has_run
        assert self.argument == "something"
        assert self.called_bus == self.bus
        assert self.callback_count == 2

        # following test should get callback for level1a.level2a and level1a.level2a.level3a
        self.reset_test()
        self.bus.publish('level1a.level2a.level3b', argument="something2")

        assert self.has_run
        assert self.argument == "something2"
        assert self.called_bus == self.bus
        assert self.callback_count == 2

        self.reset_test()
        self.bus.subscribe('level1a', self.callback)
        self.bus.publish('level1a.level2b', argument="something2")

        assert self.has_run
        assert self.argument == "something2"
        assert self.called_bus == self.bus
        assert self.callback_count == 1

    def test_messages_across_threads_thread_subscribe1(self):
        # in this example we create a thread and then from outside that thread we create a subscription to one of the
        # threads functions
        bus_a = Bus.get_or_create('bus_a')
        new_thread = ThreadClass1()
        new_thread.start()

        bus_a.subscribe('level1a.level2a', new_thread.message_callback)

        # we have subscribed to a parent level thus we should receive this publish
        bus_a.publish('level1a.level2a.level3a', argument="hello")

        #assert self.has_run
        assert new_thread.get_latest_argument() == "hello"
        assert new_thread.get_bus() == bus_a
        assert new_thread.get_latest_counter() == 1

        new_thread.stop()

    def test_messages_across_threads_thread_subscribe2(self):
        # in this example we create a thread and then from outside that thread we create a subscription to one of the
        # threads functions
        bus_a = Bus.get_or_create('bus_a')
        new_thread = ThreadClass2()
        new_thread.start()

        while not new_thread.running():
            time.sleep(0.05)

        # we have subscribed to a parent level thus we should receive this publish
        bus_a.publish('level1a.level2a.level3a', argument="hello_there")

        new_thread.stop()

        #assert self.has_run
        assert new_thread.get_latest_argument() == "hello_there"
        assert new_thread.get_bus() == bus_a
        assert new_thread.get_latest_counter() == 1

    def test_messages_across_threads_thread_publish(self):
        # in this example we create a thread and then from inside that thread we perform a publish which eventuates
        # in this main thread
        self.reset_test()
        bus_a = Bus.get_or_create('bus_a')
        bus_a.subscribe('level1a.level2a', self.callback)

        new_thread = ThreadClass3()
        new_thread.start()

        while not new_thread.running():
            time.sleep(0.05)
            
        new_thread.stop()

        assert self.has_run
        assert self.argument == "hello from thread"
        assert self.called_bus == bus_a
        assert self.callback_count == 1

class ThreadClass1(threading.Thread):
    """Inherits from Thread.
    This instance of the thread class has the subscription performed for it in another thread"""

    def __init__(self):
        super(ThreadClass1, self).__init__()
        self._should_stop = threading.Event()
        self._is_running = threading.Event()
        self._callback_counter = 0
        self._latest_argument = ""
        self._bus = None

    def run(self):
        print('Starting the Thread')
        self._is_running.set()
        while not self._should_stop.is_set():
            print(f'Thread Hello. Stopped = {self.stopped()}')
            time.sleep(0.05)
            print('Finishing the Thread')

    def stopped(self) -> bool:
        return self._should_stop.is_set()

    def running(self) -> bool:
        return self._is_running.is_set()

    def stop(self):
        print('Signalling the thread to quit processing')
        self._should_stop.set()

    def message_callback(self, bus, argument):
        self._bus = bus
        self._latest_argument = argument
        self._callback_counter = self._callback_counter + 1

    def get_latest_argument(self) -> str:
        return self._latest_argument

    def get_latest_counter(self) -> int:
        return self._callback_counter

    def get_bus(self) -> Bus:
        return self._bus

class ThreadClass2(threading.Thread):
    """Inherits from Thread.
    This instance of the thread class performs the subscribe in the run loop of the thread"""

    def __init__(self):
        super(ThreadClass2, self).__init__()
        self._should_stop = threading.Event()
        self._is_running = threading.Event()
        self._callback_counter = 0
        self._latest_argument = ""
        self._bus = Bus.get_or_create('bus_a')

    def run(self):
        print('Starting the Thread')
        self._is_running.set()
        self._bus.subscribe('level1a.level2a', self.message_callback)
        while not self._should_stop.is_set():
            print(f'Thread Hello. Stopped = {self.stopped()}')
            time.sleep(0.05)
            print('Finishing the Thread')

    def stopped(self) -> bool:
        return self._should_stop.is_set()

    def running(self) -> bool:
        return self._is_running.is_set()

    def stop(self):
        print('Signalling the thread to quit processing')
        self._should_stop.set()

    def message_callback(self, bus, argument):
        print(f'Got a message callback with argument {argument}')
        self._latest_argument = argument
        self._callback_counter = self._callback_counter + 1

    def get_latest_argument(self) -> str:
        return self._latest_argument

    def get_latest_counter(self) -> int:
        return self._callback_counter

    def get_bus(self) -> Bus:
        return self._bus

class ThreadClass3(threading.Thread):
    """Inherits from Thread.
    This instance of the thread class performs a publish in the run loop of the thread. This publish is caught
    in another thread's callback"""

    def __init__(self):
        super(ThreadClass3, self).__init__()
        self._should_stop = threading.Event()
        self._is_running = threading.Event()
        self._callback_counter = 0
        self._latest_argument = ""
        self._bus = Bus.get_or_create('bus_a')

    def run(self):
        print('Starting the Thread')
        self._is_running.set()
        self._bus.publish('level1a.level2a.level3a', argument="hello from thread")
        while not self._should_stop.is_set():
            print(f'Thread Hello. Stopped = {self.stopped()}')
            time.sleep(0.05)
            print('Finishing the Thread')

    def stopped(self) -> bool:
        return self._should_stop.is_set()

    def running(self) -> bool:
        return self._is_running.is_set()

    def stop(self):
        print('Signalling the thread to quit processing')
        self._should_stop.set()

    def message_callback(self, bus, argument):
        print(f'Got a message callback with argument {argument}')
        self._latest_argument = argument
        self._callback_counter = self._callback_counter + 1

    def get_latest_argument(self) -> str:
        return self._latest_argument

    def get_latest_counter(self) -> int:
        return self._callback_counter

    def get_bus(self) -> Bus:
        return self._bus

if __name__ == '__main__':
    unittest.main()
