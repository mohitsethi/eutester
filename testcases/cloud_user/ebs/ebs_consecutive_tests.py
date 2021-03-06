#!/usr/bin/env python

#
##########################
#                        #
#       Test Cases       #
#                        #
##########################
#
# [test_ebs_extended_test_suite]
#       Full suite of ebs related tests
#        Test Summary: 
#
#        -create a volume (do this first)
#        -run an instance (do this second, if this fails at least we know we could create a vol)
#        
#        Usage Tests: 
#        -negative -attempt to attach a volume to an instance in a separate cluster. 
#        -attach a single volume to an instance in the zones given, write random data and calc md5 of volumes
#        -detach the volume
#        -create multiple consecutive snapshots from an existin euvolume with calculated md5 sum
#        -create a single volume from each new snapshot
#        -attach each new volume created from the snapshots to an instance 
#        -calculate the md5sum of the new volumes vs the original verify they are the same
#        -remove all test volumes and snapshots used in this test
#        -terminate each test instance
#
#        Cleanup:
#        --remove all volumes, instance, and snapshots created during this test
#
#    @author: clarkmatthew

import unittest
from eutester.eutestcase import EutesterTestCase
from eutester.eutestcase import EutesterTestResult
from ebstestsuite import EbsTestSuite
import argparse
import os



if __name__ == "__main__":
    ## If given command line arguments, use them as test names to launch

    testcase= EutesterTestCase(name='ebs_extended_test')    
    testcase.setup_parser(description="Attempts to test and provide info on focused areas related to Eucalyptus EBS related functionality.", 
                          testlist=False)
    testcase.parser.add_argument('--snap_count', type=int, help='Number of snapshots to create per zone',default=5)
    testcase.parser.add_argument('--snap_delay', type=int, help='Delay in seconds between each snapshot created',default=0)
    testcase.parser.add_argument('--snap_progress', type=int, help='Number of 10 second polls to allow without increase in snapshot progress',default=60)
    testcase.parser.add_argument('--timepergig', type=int, help='Time allowed per gig size of volume during volume creation',default=300)
    testcase.parser.add_argument('--snap_attached', dest='snap_attached', action='store_true', default=False)
    testcase.parser.add_argument('--delete_to', type=int, help="Timeout for volume deletion",  default=120)
    testcase.get_args()
    ebstestsuite= testcase.do_with_args(EbsTestSuite)
    testcase.clean_method = ebstestsuite.clean_created_resources
    testlist = ebstestsuite.test_consecutive_concurrent(run=False, 
                                                    count=int(testcase.args.snap_count),
                                                    delay=testcase.args.snap_delay,
                                                    tpg=testcase.args.timepergig,
                                                    snap_attached = testcase.args.snap_attached,
                                                    delete_to = testcase.args.delete_to,
                                                    poll_progress=testcase.args.snap_progress)
    ret = testcase.run_test_case_list(testlist)
    print "ebs_extended_test exiting:("+str(ret)+")"
    exit(ret)

    
  
