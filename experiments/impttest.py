#!/usr/bin/python

# Updated 4 July 2019
# Incoherent Multiple Pulse Sequence Testing
#
# Ashton Reimer


# write an experiment that creates a new control program.
import os
import sys

BOREALISPATH = os.environ['BOREALISPATH']
#sys.path.append(BOREALISPATH + "/experiment_prototype")

#import test
import copy
from experiment_prototype.experiment_prototype import ExperimentPrototype
from experiment_prototype.decimation_scheme.decimation_scheme import DecimationStage, DecimationScheme
from experiments.test_decimation_schemes import *
# phases generated with
# import random
# random.seed('yolo')
# phases = [random.uniform(-180, 180) for x in range(8*30)]
phases = [132.1016619099944, -166.8402705636656, 23.755549755334414, -178.30338044666996, -51.191089024905125, -114.71321476873962, 101.93534977110085, 58.103942891348794, -58.42807671488053, 44.05115463657765, -139.12025608754138, -132.8485267441292, 47.663267611540704, -35.94616355980813, -101.38935328385828, 106.70830908138407, 114.24079436191812, 172.0292177374589, -178.6125177302123, -67.59106548930397, -55.543672313788804, -93.98419185021396, 156.0408743304451, -144.22897924585521, 174.93664909909478, 141.80148234687096, 42.09380962591749, -12.208423781091142, -41.44289706301859, -159.68896693692213, -127.82294764158993, 117.16797078925481, -87.8489345587803, 143.9275384656408, -143.05772314084103, 67.67664489607884, -56.176487414021295, 96.28226502509631, 111.79858838373877, 65.43244808371162, 23.29780283827168, -84.25694537598747, 97.60356228140188, 126.33873795545685, -120.84036954994613, 107.16869370939457, -17.84585235396085, -49.8245730746406, 120.204893318308, -155.3136941820597, -161.98619862627535, -31.747263739925273, 97.42754831255036, 76.96703481089037, 7.969306273712675, -36.450006447102, 101.40575404486839, -154.1634333749322, -44.4366289108477, -42.07815240377141, 160.9649428349852, -103.92737067010783, -28.356165669891368, -65.35732885645142, -84.75798678512248, 156.91752942745273, 154.14003779996602, 114.2969290081, -92.88527121555401, -29.389695314344777, 144.51393018689544, 38.838380836570764, 1.2070373374995143, 108.69639750343373, -51.152218980331924, -135.74646291429679, -11.463154284260554, -163.6796376143863, 70.89282195579011, -12.056789536988191, 97.47586320680779, -115.48918094483811, 93.62075534016873, 161.72198121627457, 47.670841949804554, 71.59294124864053, -4.175112011482497, 84.6235558406292, -71.81098661672178, 26.435144204501512, 45.370552171183476, -89.71934207463597, 111.5494079279863, -116.18252507699154, 29.38926000236117, -65.20940170437954, 60.508852172622596, -172.80380964303208, 25.881649676800038, 148.18632647694068, 13.33894498654871, -66.49516014095455, -146.92688320074774, 3.027742331981983, -103.1437418590558, -136.88965305179443, 111.69573297637658, -176.9513888462828, 69.51308738560942, 114.2964695848487, 132.01487426739493, 137.92785475883414, 104.1339589093518, -140.57470338364377, -129.72521492208227, 175.42423094272561, 19.58934855476943, -52.89704483687207, -120.66017694050396, -162.9906439526077, 153.54654129877719, -12.654220427784793, -141.2169500247515, -80.47366639833402, -75.53843027853303, 22.262840595980066, -30.976239357868224, 114.88035859118975, -61.153557132125854, 122.55582013693072, -124.47172421306405, -107.14473426814592, -174.8467555568455, 121.4641101563733, 154.64335415998306, -11.260956126534495, 27.506867596225078, -116.94383978818884, -46.768131578441626, -126.98873842398547, 135.20203502262484, 177.68817497062543, -58.77276396120216, 19.96249549177017, 158.81563601331993, -121.46472650163754, 31.15733269454256, 90.52830729893225, 138.41375899008347, 173.58633284854693, 105.55035198622545, 162.54805730972112, -126.02125068191376, 78.07324433214171, -113.27153341212929, -88.68198571774059, 104.05778217685094, -158.19608921752982, 102.19756201665393, 79.14412227512156, 132.75812240118643, 110.89891500429167, 78.65282101087826, 45.44093498361738, -29.470552372936368, -159.92131213047898, -48.04530174702697, -102.61765083739942, -30.290252110963593, 162.99910666234643, -98.11294946407276, 38.291645623406424, 26.536845414860608, 136.89792381945472, 113.7543983418189, -35.56826608501905, 80.47342194649127, -22.579272612254016, -47.03309732411634, 173.9984860922354, 94.79620522050828, -1.4614260100985064, -158.71952562310867, 11.926793652238871, -145.22179804322528, 72.86367297868563, 51.831479781577485, 50.05974523272906, -162.20835533448002, 169.76364980854345, -163.61912063409846, 133.51501074614873, -174.239554124591, -173.89790441757515, -139.05242165992618, 103.52061506700409, 44.8585016055944, -53.5344257524913, 158.32958823290738, 65.49005303925705, 19.603412697080643, 139.52822860583433, 79.70337652671515, 84.31474783299745, 161.5366125443349, -169.2166568870299, 46.76723498771062, 103.19389910288646, 49.87510616145204, 57.992112725683, -100.6679735482934, 137.73819116485788, 49.401012542138346, -60.4911358419843, -34.3345905326799, -61.89407552268331, -88.33292134249297, -29.24672061943903, -10.051545458016705, 71.85588923588628, 89.0413106057714, -122.88562773900387, 133.2405063649024, -104.65789017367644, -143.11024140388702, -164.9858099470971, 77.48233001120656, -96.61792965617259, 42.61617238564449, -122.76078496249859, -115.41345749972888, -130.50930090358935, 17.715231318039457, -143.60251317108117, -73.40684984346588, 146.16945498935286, -7.760520230860095, 56.24766702899575, 106.98945511357437, 9.229137039947062]

class ImptTest(ExperimentPrototype):

    def __init__(self):
        cpid = -3313
        output_rx_rate = 10.0e3/3
        rx_rate = 5.0e6

        tx_ant = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
        rx_main_ant = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
        rx_int_ant = [0, 1, 2, 3]
        #tx_ant = [0]
        #rx_main_ant = [0]
        #rx_int_ant = [0]
        default_slice = {  # slice_id = 0, the first slice
            "tx_antennas": tx_ant,
            "rx_main_antennas": rx_main_ant,
            "rx_int_antennas": rx_int_ant,
            "pulse_sequence": [0, 14, 22, 24, 27, 31, 42, 43],
            #"pulse_shift": None,
            "tau_spacing": 1500,  # us
            "pulse_len": 300,  # us
            "num_ranges": 75,  # range gates
            "first_range": 180,  # first range gate, in km
            "intt": 3000,
            "beam_angle": [1.75],
            "beam_order": [0],
            "scanboundflag": False,  # there is a scan boundary
            #"clrfrqflag": True,  # search for clear frequency before transmitting
            #"clrfrqrange": [13100, 13400],  # frequency range for clear frequency search,
            "txfreq" : 13100,
            # kHz including a clrfrqrange overrides rxfreq and txfreq so these are no
            # longer necessary as they will be set by the frequency chosen from the
            # range.
            #"xcf": True,  # cross-correlation processing
            #"acfint": True,  # interferometer acfs
        }

        katscan_slice = {
            "tx_antennas": tx_ant,
            "rx_main_antennas": rx_main_ant,
            "rx_int_antennas": rx_int_ant,
            "pulse_sequence": [0, 14, 22, 24, 27, 31, 42, 43],
            #"phase_": [0, 0, 0, 0, 0, 0, 0, 0],
            "tau_spacing": 1500,  # us
            "pulse_len": 300,  # us
            "num_ranges": 75,  # range gates
            "first_range": 180,  # first range gate, in km
            "intt": 3000,
            "beam_angle": [1.75],
            "beam_order": [0],
            "scanboundflag": False,  # there is a scan boundary
            #"clrfrqflag": True,  # search for clear frequency before transmitting
            #"clrfrqrange": [13100, 13400],  # frequency range for clear frequency search,
            "txfreq" : 13100,
            # kHz including a clrfrqrange overrides rxfreq and txfreq so these are no
            # longer necessary as they will be set by the frequency chosen from the
            # range.
            #"xcf": True,  # cross-correlation processing
            #"acfint": True,  # interferometer acfs
        }

        # set phases for each pulse on each sequence
        # 30 sequences of impt, each its own slice
        list_of_slices = list()
        interfacing_dict1 = dict()
        interfacing_dict2 = dict()
        for i in range(30):
            impt_slice = copy.deepcopy(default_slice)
            impt_slice['pulse_phase_offset'] = phases[i*8:8*(i+1)]
            if i == 0:
                list_of_slices.append(impt_slice)
            else:
                list_of_slices.append(impt_slice)
            interfacing_dict1[i] = 'INTEGRATION'
            interfacing_dict2[i] = 'SCAN'


        list_of_slices.append(katscan_slice)
        rxctrfreq = katscan_slice["txfreq"]
        txctrfreq = rxctrfreq
        super(ImptTest, self).__init__(cpid, txctrfreq=txctrfreq, rxctrfreq=rxctrfreq, decimation_scheme=create_test_scheme_9(),
            comment_string="Reimer IMPT Experiment")
        # add slices to experiment
        for i,exp_slice in enumerate(list_of_slices):
            if i == 0:
                self.add_slice(exp_slice)
            elif i == 30:   # katscan slice
                self.add_slice(exp_slice,interfacing_dict=interfacing_dict2)#{0: 'SCAN'})
            else:
                self.add_slice(exp_slice,interfacing_dict=interfacing_dict1) #{0: 'INTEGRATION'})


        # Other things you can change if you wish. You may want to discuss with us about
        # it beforehand.
        # These apply to the experiment and all slices as a whole.


        # self.txrate = 12000000 # Hz, sample rate fed to DAC

        # Update the following interface dictionary if you have more than one slice
        # dictionary in your slice_list and you did not specify the interfacing when
        # adding the slice. The keys in the interface dictionary correspond to the
        # slice_ids of the slices in your slice_list.
        # Take a look at the documentation for the frozenset interface_types in
        # experiment_prototype to understand the types of interfacing (PULSE,
        # INTEGRATION, INTTIME, or SCAN).

        # NOTE keys are as such: (0,1), (0,2), (1,2), NEVER includes (2,0) etc.

        # self.interface.update({
        #     (0, 1): 'SCAN'  # Full scan of one slice, then full scan of the next.
        # })
