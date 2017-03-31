#!/usr/bin/python # REVIEW #37 Best way to call interpreter? there's also "/usr/bin/env python" that allows you to have python installed anywhere
# REVIEW #7 We need some kind of license at top of all files - or a referral to the license/copyright/etc
# The template for an experiment. # REVIEW # 7 Also need this to conform to docstring PEP 257 for modules (""" example """)
import sys
import math

import numpy as np
import json

sys.path.append("../radar_control/scan_classes/")
import scans
#from cpobject import CPObject, interfacing, if_type # REVIEW #33

# REVIEW #26 When we refer to comments about anything "cpobject" related, we know that naming scheme may be changed entirely.


# REVIEW #28 This could potentially be a global variable instead.
#interface_types = frozenset(['SCAN', 'INTTIME', 'INTEGRATION', 'PULSE'])
def if_type(): #REVIEW #26 Could just expand this to the full "interface_types"
    return frozenset(['SCAN', 'INTTIME', 'INTEGRATION', 'PULSE'])

def interfacing(cponum): # REVIEW #26 Could use a more informative name.
    if_list=[]
    for i in range(cponum): # REVIEW #26 i and j can have more meaningful names. Perhaps cpo1, cpo2, something like that. Could go for most places indexing is used.
        for j in range(i+1,cponum):
            if_list.append((i,j))
    if_keys=tuple(if_list) # REVIEW #33 Fairly sure this conversion to a tuple is unneeded for what is happening here.
    if_dict={}
    for num1,num2 in if_keys:
        if_dict[num1, num2]="NONE"
    # REVIEW #39 That for loop could just be
    #if_dict = dict((key,"NONE") for key in if_list)


    return if_dict

def selfcheck_piece(cpdict, configdata): #REVIEW #1 #26 Name and docstring could be more clear
    """
    Do some tests of the dictionaries in the experiment
    to ensure values in this component make sense.
    """
    error_count=0
    error_dict={}

    main_antenna_count = int(configdata['main_antenna_count']) #REVIEW #15 should probably make a config handler class. More in a further comment.

    # check none greater than 15, no duplicates # REVIEW #29 could say in this comment that none greater than main antenna count instead of 15.
    # REVIEW #0 Since we decided for now that we would receive on all antennas, the check for rxchannels should be equal to main+inter count.
    # REVIEW #26 Lets reflect our decision to not use the word channel.
    if len(cpdict['txchannels']) > main_antenna_count or len(cpdict['rxchannels'])> main_antenna_count: # REVIEW #31 looks like three lines are over 100 chars, consider editing to be under 100
        #REVIEW #39 These errors could just be appended to a list instead of using a dictionary.
        error_dict[error_count]="CP Object Has Too Many Antenna Channels" # REVIEW #34 Could include the actual value that caused the error. Goes for all error statements.
        error_count=error_count+1
    for i in range(len(cpdict['txchannels'])):
        if cpdict['txchannels'][i]>= main_antenna_count or cpdict['rxchannels'][i] >= main_antenna_count:
            error_dict[error_count]=""" Object Specifies Channel \
                Numbers Over {}""".format(main_antenna_count)
            error_count=error_count+1
        for j in range(i+1, len(cpdict['txchannels'])):
            if cpdict['txchannels'][i]== cpdict['txchannels'][j] or cpdict['rxchannels'][i]== cpdict['rxchannels'][j]:
                error_dict[error_count]="CP Object Has Duplicate Antennas"
                error_count=error_count+1

    # check sequence increasing
    if len(cpdict['sequence'])!=1:
        for i in range(1, len(cpdict['sequence'])):
            if cpdict['sequence'][i]<= cpdict['sequence'][i-1]:
                error_dict[error_count]="CP Object Sequence Not Increasing"
                error_count=error_count+1

    #check pulse_len and mpinc make sense (values in us)
    if cpdict['pulse_len'] > cpdict['mpinc']:
        error_dict['error_count']="CP Pulse Length Greater than MPINC"
        error_count=error_count+1
    if cpdict['pulse_len'] < 0.01:
        error_dict[error_count]="CP Pulse Length Too Small"
        error_count=error_count+1

    # check intn and intt make sense given mpinc, and pulse sequence.
    seq_len=cpdict['mpinc']*(cpdict['sequence'][-1]+1)

# TODO: Check these
#        self.intt=3000 # duration of the direction, in ms
#        self.intn=21 # max number of averages (aka full pulse sequences transmitted) in an integration time intt (default 3s)

    # check no duplicates in beam directions
    for i in range(len(cpdict['beamdir'])):
        for j in range(i+1,len(cpdict['beamdir'])):
            if cpdict['beamdir'][i]== cpdict['beamdir'][j]:
                error_dict[error_count]="CP Beam Direction Has Duplicates"
                error_count=error_count+1
            if cpdict['beamdir'][i] > cpdict['beamdir'][j]:
                error_dict[error_count]="CP Beam Directions Not in Order \
                    Clockwise (E of N is positive)"
                error_count=error_count+1

    if (not cpdict['scan']): # if empty
        error_dict[error_count]="Scan Empty"
        error_count=error_count+1

    # check beam numbers in scan exist
    for i in cpdict['scan']:
        if i>=len(cpdict['beamdir']):
            error_dict[error_count]="CP Scan Beam Direction DNE, not \
                Enough Beams in beamdir"
            error_count=error_count+1

    # check scan boundary not less than minimum required scan time.
    if cpdict['scanboundf']==1:
        if cpdict['scanbound'] < (len(cpdict['scan'])*cpdict['intt']):
            error_dict[error_count]="CP Scan Too Long for ScanBoundary"
            error_count=error_count+1

    #TODO other checks

    #freq=12300 # in kHz
    #clrfrqf=1 # flag for clear frequency search
    #clrfrqrange=300 # clear frequency range if searching
    # receiving params
    #xcf=1 # flag for cross-correlation
    #acfint=1 # flag for getting lag-zero power of interferometer
    #wavetype='SINE'
    #seqtimer=0
    # cpid is a unique value?

    return error_dict


class ExperimentPrototype(object):
    """Class combining control program objects, defining how they
    interface and some overall metadata

    :param cpid: unique id (RCP number)
    :param cponum: number of CPObjects in this control program.
    :
    """ # REVIEW #26 - the ordering of arguments in the documentation isn't consistent with the ordering in the __init__ function. cpid should go first based on the comment

    def __init__(self, cponum, cpid):

        self.cpid=cpid # REVIEW #40 use spaces around '=' signs - it's easier to read. Follow PEP 8 style guide. This applies to all
        # Unique ID for each new cp.
        self.cponum=cponum
        # Number of CPObjects in this program. # REVIEW #38 These comments are superfluous since the docstring tells all you need to know
        cpo_list=[]

        self.cpo_keys = [ "obj_id", "cpid", "txchannels", "rxchannels",  # REVIEW #26 Should this be named cpo_keys or something like radar_parameters, scan_parameters, scan_constructs. The idea being that an experiment will have a list of some lower level object (experiment_parameters will be a list of 'scans' or 'radar params' OR a scan parameter list will contain 1 or more sets of 'radar params')
            "sequence", "pulse_shift", "mpinc", "pulse_len", "nrang", "frang",
            "intt", "intn", "beamdir", "scan", "scanboundf", "scanbound",
            "txfreq", "rxfreq", "clrfrqf", "clrfrqrange", "xcf", "acfint",
            "wavetype", "seqtimer" ]

        for num in range(self.cponum): # REVIEW #39 You might just want to instantiate the dict and set all to None above, avoiding the for loop. You can also use a dictionary comprehension: http://stackoverflow.com/questions/1747817/create-a-dictionary-with-list-comprehension-in-python - in this way you can increment the obj_id we think
            cp_object = {} # I don't know what to call these anymore # REVIEW #6 should be labelled TODO
            for key in self.cpo_keys:
                cp_object[key] = None
            cp_object["obj_id"] = num
            cp_object["cpid"] = self.cpid

            cpo_list.append(cp_object)

        self.cpo_list=cpo_list

        # Load the config data
        with open('../config.ini') as config_data: # REVIEW #15 An option would be to make the config file location string an argument, and supply this as the default. Also, should probably make a config handler class to error check and give a first pass at the config options. Similar to Keith's C++ code.
            self.config=json.load(config_data)

        # Next some metadata that you can change, with defaults.
        # TODO: make default none and have a function that will
        #   calculate something appropriate if left blank.

        self.txctrfreq=12000 # in kHz.
        self.txrate=12000000 # sampling rate, samples per sec
        self.rxctrfreq=12000 # in kHz.
        # NOTE: rx sampling rate is set in config.

        self.xcf=1 # REVIEW #0 #28 correct if propogated to rawacf/iq file writing, otherwise should be boolean. Same for acfint
        # Get cross-correlation data in processing block.

        self.acfint=1
        # Determine lag-zero interferometer power in fitacf.

        self.interface=interfacing(self.cponum) # REVIEW #26 We got a bit confused if just looking at this line, is cponum the total number or the 'index' (specific identifier of cpo) so maybe the name needs updating to reflect this. cpo_count, num_cp_objects, 'total' something
        # Dictionary of how each cpo interacts with the other cpos.
        # Default is "NONE" for all, but must be modified in experiment.
        # NOTE keys are as such: (0,1), (0,2), (1,2), NEVER
        # includes (2,0) etc. The only interface options are:
        # if_types=frozenset(['NONE', 'SCAN', 'INTTIME', 'INTEGRATION',
        # 'SAME_SEQ', 'MULTI_SEQ']) # REVIEW #3 Where are SAME_SEQ and MULTI_SEQ below? also, does PULSE need to be in this list?

        """ #REVIEW #3 Perhaps this comment should go with the interfacing, or if_type method. Seems to be a better place.
        INTERFACING TYPES:

        NONE : Only the default, must be changed.
        SCAN : Scan by scan interfacing. cpo #1 will scan first
            followed by cpo #2 and subsequent cpo's.
        INTTIME : nave by nave interfacing (full integration time of
             one sequence, then the next). Time/number of sequences
            dependent on intt and intn in cp_object. Effectively
            simultaneous scan interfacing, interleaving each
            integration time in the scans. cpo #1 first inttime or
            beam direction will run followed by cpo #2's first inttime,
            etc. if cpo #1's len(scan) is greater than cpo #2's, cpo
            #2's last integration will run and then all the rest of cpo
            #1's will continue until the full scan is over. CPObject 1
            and 2 must have the same scan boundary, if any boundary.
            All other may differ.
        INTEGRATION : integration by integration interfacing (one
            sequence of one cp_object, then the next). CPObject #1 and
            CPO #2 must have same intt and intn. Integrations will
            switch between one and the other until time is up/nave is
            reached.
        PULSE : Simultaneous sequence interfacing, pulse by pulse
            creates a single sequence. CPO A and B might have different
            frequencies (stereo) and/or may have different pulse
            length, mpinc, sequence, but must have the same integration
            time. They must also have same len(scan), although they may
            use different directions in scan. They must have the same
            scan boundary if any. A time offset between the pulses
            starting may be set (seq_timer in cp_object). CPObject A
            and B will have integrations that run at the same time.
        """

    def __call__(self): # REVIEW #28 It seems this method is used to print stuff. try to use __repr__ or __str__ instead http://stackoverflow.com/questions/1436703/difference-between-str-and-repr-in-python
        print 'CPID [cpid]: {}'.format(self.cpid)
        print 'Num of CP Objects [cponum]: {}'.format(self.cponum)
        for i in range(self.cponum):
            print '\n'
            print 'CP Object : {}'.format(i)
            print self.cpo_list[i]
        print '\n'
        print 'Interfacing [interface]: {}'.format(self.interface)
        return None

    def build_Scans(self): # REVIEW #40 Function name does not adhere to PEP. Should not have caps.
        """ REVIEW #7 Just a note to update this documentation away from controlprogram
        Will run after a controlprogram instance is set up and
        modified - build iterable objects for radar_control
        """

        # Check interfacing
        self.selfcheck()
        self.check_interfacing()
        # Find separate scans.
        self.cpo_scans=self.get_scans() # REVIEW #32 We think its more clear to the reader to declare all members in the constructor so that we know what to expect. Just set them to None or empty container type.
        # Returns list of scan lists. Each scan list is a list of the
        #   cpo numbers for that scan.
        self.scan_objects=[] # REVIEW #32
        for scan_cpo_list in self.cpo_scans: # REVIEW #39 This could be converted to list comprehension to be more pythonic
            self.scan_objects.append(scans.Scan(self, scan_cpo_list))
        # Append a Scan instance, passing this controlprog, list of cpo # REVIEW #7
        #   numbers to include in scan.

    def selfcheck(self): # REVIEW #40 Perhaps add an underscore in between self and check
        """
        Check that the values in this experiment are valid
        """

        if (self.cponum<1):
            errmsg="Error: No objects in control program"
            sys.exit(errmsg) # REVIEW 6 Add a todo for error handling. Perhaps use exceptions instead.

        #TODO: somehow check if self.cpid is not unique

        for cpo in range(self.cponum):
            selferrs=selfcheck_piece(self.cpo_list[cpo],self.config)
            if (not selferrs): # REVIEW #39 unneeded parenthesis
                # If returned error dictionary is empty
                continue
            errmsg="Self Check Errors Occurred with Object Number : {} \nSelf \
                Check Errors are : {}".format(cpo, selferrs)
            sys.exit(errmsg) # REVIEW 6 Add a todo for error handling. Perhaps use exceptions instead.
        else: # no break (exit)
            print "No Self Check Errors. Continuing..."
        return None


    # REVIEW #30 Consider splitting interface/error checking into a seperate class. It would decouple this behaviour and could simplify the experiment significantly. The experiment handler would be able to make
    # sure that the experiment is error checked, and someone developing the experiment could just run their experiment through it in the interpretter or something.
    def check_interfacing(self):
        """
        Check that the keys in the interface are not NONE and are
        valid.
        """

        for key in self.interface.keys(): # REVIEW #39 There is a more pythonic way to iterate over dicts http://stackoverflow.com/questions/3294889/iterating-over-dictionaries-using-for-loops-in-python
            if self.interface[key]=="NONE": # REVIEW #34 Do you mean to say that interface type, not key, is default?
                errmsg='Interface keys are still default, must set key \
                    {}'.format(key)
                sys.exit(errmsg) # REVIEW 6 Add a todo for error handling. Perhaps use exceptions instead.

        for num1,num2 in self.interface.keys(): # REVIEW #39 There is a more pythonic way to iterate over dicts http://stackoverflow.com/questions/3294889/iterating-over-dictionaries-using-for-loops-in-python
            if ((num1>=self.cponum) or (num2>=self.cponum) or (num1<0) # REVIEW #15 Should you check ordering? Num 1 always less than num 2 based off your interfacing comments.
                    or (num2<0)):
                errmsg='Interfacing key ({}, {}) is not necessary and not \ # REVIEW #34 Maybe split these into two error checks/messages. One for invalid parameters and then one for unnecessary keys
                    valid'.format(num1, num2)
                sys.exit(errmsg) # REVIEW 6 Add a todo for error handling. Perhaps use exceptions instead.
            if self.interface[num1, num2] not in if_type():
                errmsg='Interfacing Not Valid Type between CPO {} and CPO \
                    {}'.format(num1, num2)
                sys.exit(errmsg) # REVIEW 6 Add a todo for error handling. Perhaps use exceptions instead.

        # TODO: add checks that verify interfacing makes sense - ie 0,1 is pulse by pulse, and 1,2 is scan therefore 0,2 must also be scan
        # Could also accept NONE at 0,2 in that ^^ example ??
        return None

    def get_scans(self):
        """Take my own interfacing and get info on how many scans and # REVIEW #1 Could use a more clear description.
            which cpos make which scans
        """
        scan_combos=[]

        for num1,num2 in self.interface.keys(): # REVIEW #39 There is a more pythonic way to iterate over dicts http://stackoverflow.com/questions/3294889/iterating-over-dictionaries-using-for-loops-in-python
            if (self.interface[num1, num2]=="PULSE" or
                    self.interface[num1, num2]=="INT_TIME" or
                    self.interface[num1, num2]=="INTEGRATION"):
                scan_combos.append([num1,num2])
            # Save the keys that are scan combos.

        scan_combos=sorted(scan_combos)
        #if [2,4] and [1,4], then also must be [1,2] in the scan_combos
        i=0 # REVIEW #3 This needs a detailed explaination with examples.
        while (i<len(scan_combos)):
            k=0
            while (k<len(scan_combos[i])):
                j=i+1
                while (j<len(scan_combos)):
                    if scan_combos[i][k]==scan_combos[j][0]:
                        add_n=scan_combos[j][1] # REVIEW #26 add_n  perhaps better name
                        scan_combos[i].append(add_n)
                        # Combine the indices if there are 3+ CPObjects
                        #   combining in same seq.
                        for m in range(0,len(scan_combos[i])-1):
                            # Try all values in seq_combos[i] except
                            #    the last value, which is = to add_n.
                            """
                            if scan_combos[i][m] > add_n:
                                .......
                            """
                            try:
                                scan_combos.remove([scan_combos[i][m],add_n]) # REVIEW #0 what happens if the item you try to remove is in the form [n,m] where n > m
                                # seq_combos[j][1] is the known last
                                #   value in seq_combos[i]
                            except ValueError: # REVIEW #3 This error needs to be either more detailed, or explain how it would happen.
                                errmsg='Interfacing not Valid: CPO {} and CPO \
                                    {} are combined in-scan and do not \
                                    interface the same with CPO {}'.format(
                                    scan_combos[i][m], scan_combos[i][k], add_n
                                    )
                                sys.exit(errmsg)
                        j=j-1
                        # This means that the former scan_combos[j] has
                        #   been deleted and there are new values at
                        #   index j, so decrement before
                        #   incrementing in for. #REVIEW #1 Do you mean while instead of for here?
                    j=j+1
                k=k+1
            i=i+1
        # now scan_combos is a list of lists, where a cp object occurs
        #   only once in the nested list.
        for cpo in range(self.cponum): # REVIEW #26
            found=False
            for i in range(len(scan_combos)):
                for j in range(len(scan_combos[i])):
                    if cpo==scan_combos[i][j]:
                        found=True
                        break
                if found==False:
                    continue
                break
            else: # no break
                scan_combos.append([cpo])
            # Append the cpo on its own, is not scan combined.

        # REVIEW 39 All the above can be rewritten as this. Else excutes in a similar manner
        # for cpo in range(self.cponum):
        #     for sc in scan_combos:
        #         if cpo in sc:
        #             break
        #     else:
        #         scan_combos.append([cpo])


        scan_combos=sorted(scan_combos)
        return scan_combos
