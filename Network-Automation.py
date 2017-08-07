#!/usr/bin/env python
# --*coding:utf8*--

import time
import threading
from base_tools import get_command, load_info_from_json
from network_tools import InterfaceTools
from multiprocessing import Pool, Process, Queue

# Get the username and the password
# Get the command from a file, and exclued the empty lines
# Get the devices information from a json file.
# username, password = get_username_and_password()
COMMANDS = get_command("router-command.txt")
DEVICES = load_info_from_json("Devices.json")
DEVICES_CONNECTION_INFORMATION = load_info_from_json("Connection Information.json")


class MainBase(object):
    """
    MainBase for some tools.
    """
    @staticmethod
    def get_interfaces_tools_handler(device):
        return InterfaceTools(devices_info=device, commands=COMMANDS)

    @staticmethod
    def write_queen(queen, message):
        queen.put(message)

    @staticmethod
    def read_queen(queen):
        while True:
            message = queen.get(True)
            if message:
                return message


class ByMultiProcessAndMessage(MainBase):
    """
the first way of doing thing.
1. how to run the task
    - specify the device, which the task will be execute on the device
    - specify the task,
2.if there is a lot of devices need to do the same task, then
    - creating a processes pool, each process is allocate to a device to run the task
    - specify a queue, after finishing the task on all devices send a message to the queue.
3.if there is more than one task, then doing the task one by one, the tasks is specify in a list.
    - get the Queue message before next task start, and the message must be True. 

Because of the sub process can not share the Memory with the main process, so need to create a device handler
each time the sub process started. 
So There still need extra time to create the device handler.
    """

    def task_run(self, device, task):
        device_handler = self.get_interfaces_tools_handler(device)
        task_attr = getattr(device_handler, task)
        if task_attr:
            task_attr()

    def pooling_task_and_write_queen(self, task, devices, queen):
        print("starting task %s" % task)
        p = Pool(4)
        for device in devices.values():
            try:
                p.apply_async(self.task_run, args=(device, task,))
            except Exception as e:
                self.write_queen(queen, False)
                raise e
        self.write_queen(queen, True)
        p.close()
        p.join()

    def action_by_messages(self, devices):
        queen = Queue()
        tasks = ["do_no_shutdown_all_interface",
                 "do_make_neighbor_description",
                 "do_shutdown_unused_interface",
                 "do_add_ip_address_to_interface"]
        next_task = True
        for task in tasks:
            if next_task:
                self.pooling_task_and_write_queen(task, devices, queen)
                next_task = self.read_queen(queen)
                print(next_task)
            else:
                print("something wrong just happened....")
                break


class BySeqDeviceSeqTask(MainBase):
    """
The second way:
Running the task one by one on each device.
    """
    def interfaces_actions_by_seq(self, device):
        device_handler = self.get_interfaces_tools_handler(device)
        device_handler.do_no_shutdown_all_interface()
        device_handler.do_make_neighbor_description()
        device_handler.do_shutdown_unused_interface()
        device_handler.do_add_ip_address_to_interface()


class ByMultiDeviceSeqTask(BySeqDeviceSeqTask):
    """
    The thrid way:
    Running the task one by one on each device, but each device has a process.
    """
    def multideviceway(self, devices):
        p = Pool(4)
        for device in devices.values():
            p.apply_async(self.interfaces_actions_by_seq, args=(device,))
        p.close()
        p.join()


class ByMultiThreading(BySeqDeviceSeqTask):
    """
    The fourth way:
    Running the task one by one on each device, but each device has a thread.
    """
    def action_by_multi_threading(self, devices):
        threads = []
        for device in devices.values():
            threads.append(threading.Thread(target=self.interfaces_actions_by_seq, args=(device,)))
        for _, thread in enumerate(threads):
            print("Starting the Thread %s..." % str(_))
            try:
                thread.start()
            except AttributeError as e:
                print(e)
        for _, thread in enumerate(threads):
            thread.join()
            print("Stop the Thread %s..." % str(_))


class ByMultiThreadingAndMessage(MainBase):
    """"""
    @staticmethod
    def task_run(device_handler, task):
        task_attr = getattr(device_handler, task)
        if task_attr:
            task_attr()

    def pooling_task_and_write_queen(self, task, devices_handlers, queen):
        print("starting task %s" % task)
        t_pools = []
        for device_handler in devices_handlers:
            try:
                t = threading.Thread(target=self.task_run, args=(device_handler, task,))
                t.start()
                t_pools.append(t)
            except Exception as e:
                raise e
        for t in t_pools:
            t.join()
        self.write_queen(queen, True)

    def make_handlers(self, devices):
        devices_handlers = []
        for device in devices.values():
            devices_handlers.append(self.get_interfaces_tools_handler(device))
        return devices_handlers

    def action_by_messages(self, devices):
        task_queue = Queue()
        tasks = ["do_no_shutdown_all_interface",
                 "do_make_neighbor_description",
                 "do_shutdown_unused_interface",
                 "do_add_ip_address_to_interface"]
        next_task = True
        devices_handlers = self.make_handlers(devices)
        for task in tasks:
            if next_task:
                self.pooling_task_and_write_queen(task, devices_handlers, task_queue)
                next_task = self.read_queen(task_queue)
                print(next_task)
            else:
                print("something wrong just happened....")
                break


def main_by_seq():
    start = time.time()
    print("starting the Tasks...")
    action = BySeqDeviceSeqTask()
    for device in DEVICES.values():
        action.interfaces_actions_by_seq(device)
    end = time.time()
    print("ending the Tasks by %0.2f seconds.." % (end-start))


def main_by_multiprocessing_pools():
    start = time.time()
    print("starting the Tasks...")
    action = ByMultiDeviceSeqTask()
    action.multideviceway(DEVICES)
    end = time.time()
    print("ending the Tasks by %0.2f seconds.." % (end-start))


def main_by_threading():
    start = time.time()
    print("starting the Tasks...")
    action = ByMultiThreading()
    action.action_by_multi_threading(DEVICES)
    end = time.time()
    print("ending the Tasks by %0.2f seconds.." % (end-start))


def main_by_multiprocess_message():
    start = time.time()
    print("starting the Tasks...")
    action = ByMultiProcessAndMessage()
    action.action_by_messages(DEVICES)
    end = time.time()
    print("ending the Tasks by %0.2f seconds.." % (end-start))


def main_by_threading_message():
    start = time.time()
    print("starting the Tasks...")
    action = ByMultiThreadingAndMessage()
    action.action_by_messages(DEVICES)
    end = time.time()
    print("ending the Tasks by %0.2f seconds.." % (end-start))


if __name__ == '__main__':
    # main_by_seq()
    #main_by_multiprocessing_pools()
    # main_by_threading()
    main_by_multiprocess_message()
    # main_by_threading_message()

