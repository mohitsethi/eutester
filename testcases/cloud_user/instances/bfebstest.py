#!/usr/bin/python
from Queue import Queue
import unittest
import re
from instancetest import InstanceBasics

class BFEBSBasics(InstanceBasics):
    def __init__(self, extra_args = None):
        args = ['--imgurl']
        if extra_args:
            args.append(extra_args)
        super(BFEBSBasics, self).__init__(args)

    def clean_method(self):
        if self.reservation:
            self.tester.terminate_instances(self.reservation)
            self.reservation = None
        self.tester.sleep(10)
        super(BFEBSBasics, self).clean_method()


    def RegisterImage(self, zone= None):
        '''Register a BFEBS snapshot'''
        if zone is None:
            zone = self.zone
        if not self.args.imgurl:
            raise Exception("No imgurl passed to run BFEBS tests")
        if not self.reservation:
            self.reservation = self.tester.run_instance(keypair=self.keypair.name, group=self.group.name, zone=zone)
        for instance in self.reservation.instances:
            self.volume = self.tester.create_volume(azone=self.zone, size=2)
            self.volume_device = instance.attach_volume(self.volume)
            instance.sys("curl " +  self.args.imgurl + " > " + self.volume_device, timeout=800)
            snapshots = self.tester.create_snapshot(self.volume.id)
            if len(snapshots) == 1:
                snapshot = snapshots[0]
            else:
                Exception("Instead of getting 1 snapshot back we got " + len(snapshots) )
            image_id = self.tester.register_snapshot(snapshot)
        self.image = self.tester.get_emi(image_id)

    def LaunchImage(self, zone= None):
        '''Launch a BFEBS image'''
        if zone is None:
            zone = self.zone
        self.image = self.tester.get_emi(root_device_type="ebs")
        self.reservation = self.tester.run_instance(self.image,keypair=self.keypair.name, group=self.group.name, zone=zone)
        self.assertTrue( self.tester.ping(self.reservation.instances[0].public_dns_name), 'Could not ping instance')

    def StopStart(self, zone = None):
        '''Launch a BFEBS instance, stop it then start it again'''
        if zone is None:
            zone = self.zone
        self.image = self.tester.get_emi(root_device_type="ebs")
        if not self.reservation:
            self.reservation = self.tester.run_instance(self.image,keypair=self.keypair.name, group=self.group.name, zone=zone)
        self.assertTrue(self.tester.stop_instances(self.reservation))
        self.assertFalse( self.tester.ping(self.reservation.instances[0].public_dns_name, poll_count=2), 'Was able to ping stopped instance')
        self.assertTrue(self.tester.start_instances(self.reservation))
        self.tester.debug("Waiting 20s for instance to boot") 
        self.tester.sleep(20)
        self.assertTrue( self.tester.ping(self.reservation.instances[0].public_dns_name,  poll_count=2), 'Could not ping instance')

    def MultipleBFEBSInstances(self):
        """Run half of the available m1.small instances with a BFEBS image"""
        if self.reservation:
            self.tester.terminate_instances(self.reservation)
        self.image = self.tester.get_emi(root_device_type="ebs")
        self.MaxSmallInstances(self.tester.get_available_vms() / 2) 

    def ChurnBFEBS(self):
        """Start instances and stop them before they are running, increase time to terminate on each iteration"""
        if self.reservation:
            self.tester.terminate_instances(self.reservation)
        self.image = self.tester.get_emi(root_device_type="ebs")
        self.Churn(self.image.id)

if __name__ == "__main__":
    testcase = BFEBSBasics()
    ### Either use the list of tests passed from config/command line to determine what subset of tests to run
    list = testcase.args.tests or [ "RegisterImage",  "LaunchImage", "StopStart", "MultipleBFEBSInstances", "ChurnBFEBS" ]
    ### Convert test suite methods to EutesterUnitTest objects
    unit_list = [ ]
    for test in list:
        unit_list.append( testcase.create_testunit_by_name(test) )
        ### Run the EutesterUnitTest objects

    result = testcase.run_test_case_list(unit_list,clean_on_exit=True)
    exit(result)
