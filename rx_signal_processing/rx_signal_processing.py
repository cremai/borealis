import sys
import os
import mmap
import time
import threading
import numpy as np
import posix_ipc as ipc
import zmq
import dsp

borealis_path = os.environ['BOREALISPATH']
if not borealis_path:
    raise ValueError("BOREALISPATH env variable not set")

if __debug__:
    sys.path.append(borealis_path + '/build/debug/utils/protobuf')
else:
    sys.path.append(borealis_path + '/build/release/utils/protobuf')

import rxsamplesmetadata_pb2
import sigprocpacket_pb2

sys.path.append(borealis_path + '/utils/')
import signal_processinging_options.signal_processinging_options as spo
from zmq_borealis_helpers import socket_operations as so

def printing(msg):
    """
    Pretty print function for the Signal Processing module.
    :param msg: The string to format nicely for printing
    """
    SIGNAL_PROCESSING = "\033[96m" + "SIGNAL PROCESSING: " + "\033[0m"
    sys.stdout.write(SIGNAL_PROCESSING + msg + "\n")

def main():

    sig_options = spo.SignalProcessingOptions()

    sockets = so.create_sockets([sig_options.dsp_to_radctrl_identity,
                                    sig_options.dsp_to_driver_identity,
                                    sig_options.dsp_to_exphan_identity,
                                    sig_options.dspbegin_to_brian_identity,
                                    sig_options.dspend_to_brian_identity,
                                    sig_options.dsp_to_dw_identity])

    dsp_to_radar_control = sockets[0]
    dsp_to_driver = sockets[1]
    dsp_to_experiment_handler = sockets[2]
    dspbegin_to_brian = sockets[3]
    dspend_to_brian = sockets[4]
    dsp_to_dw = sockets[5]

    #poller = zmq.Poller()
    #poller.register(dsp_to_radar_control, zmq.POLLIN)
    #poller.register(dsp_to_driver, zmq.POLLIN)
    #poller.register(dsp_to_experiment_handler, zmq.POLLIN)

    ringbuffer = None
    shm = ipc.SharedMemory(sig_options.ringbuffer_name)
    mapped_mem = mmap.mmap(shm.fd, shm.size)

    total_antennas = sig_options.main_antenna_count + sig_options.intf_antenna_count

    dm_rates = []
    dm_scheme_taps = []
    output_sample_rate = None
    offset_to_first_rx_sample = None
    rx_rate = sig_options.rx_rate

    first_time = True
    while True:

        # try:
        #     socks = dict(poller.poll())
        # except KeyboardInterrupt:
        #     sys.exit()

        reply = so.recv_bytes(dsp_to_radar_control, options.radctrl_to_dsp_identity, printing)

        sp_packet = sigprocpacket_pb2.SigProcPacket()
        sp_packet.ParseFromString(reply)

        rx_rate = sp_packet.rx_rate
        output_sample_rate = sp_packet.output_sample_rate
        mixing_freqs = []
        main_beam_angles = []
        intf_beam_angles = []

        slice_details = []
        for i,chan in enumerate(sp_packet.rxchannel):
            detail = {}

            mixing_freqs.append(chan.rxfreq)

            detail['slice_id'] = chan.slice_id
            detail['slice_num'] = i
            detail['first_range'] = chan.first_range
            detail['range_sep'] = chan.range_sep
            detail['tau_spacing'] = chan.tau_spacing

            lags = []
            for lag in chan.lag:
                lags.append([lag.pulse_1,lag.pulse_2])

            detail['lags'] = lags


            main_beams = []
            intf_beams = []
            for bd in chan.beam_directions:
                main_beam = []
                intf_beam = []
                for j,phase in enumerate(bd.phase):

                    p = phase.real_phase + 1j * phase.imag_phase
                    if j < sig_options.main_antenna_count:
                        main_beam.append(p)
                    else:
                        intf_beam.append(p)
                main_beams.append(main_beam)
                intf_beams.append(intf_beam)

            details['num_beams'] = len(main_beams)

            slice_details.append(details)
            main_beam_angles.append(main_beams)
            intf_beam_angles.append(intf_beams)



        max_num_beams = max([len(x) for x in main_beam_angles])

        def pad_beams(angles, ant_count):
            for x in angles:
                if len(x) < max_num_beams:
                    beam_pad = [0.0] * ant_count
                    for i in range(max_num_beams - len(x)):
                        x.append(beam_pad)

        pad_beams(main_beams, sig_options.main_antenna_count)
        pad_beams(intf_beams, sig_options.intf_antenna_count)




        message = "Need data to process"
        so.send_data(dsp_to_driver, sig_options.driver_to_dsp_identity, message)
        reply = so.recv_bytes(dsp_to_driver, sig_options.driver_to_dsp_identity)

        rx_metadata = rxsamplesmetadata_pb2.RxSamplesMetadata()
        rx_metadata.ParseFromString(reply)

        if first_time:
            shm = ipc.SharedMemory(sig_options.ringbuffer_name)
            mapped_mem = mmap.mmap(shm.fd, shm.size)
            ringbuffer = np.frombuffer(mapped_mem, dtype=np.complex64).reshape(total_antennas, -1)

            for stage in sp_packet.decimation_stages:
                dm_rates.append(stage.dm_rate)
                dm_scheme_taps.append(stage.filter_taps)

            first_time = False


        extra_samples = 0
        for dm,taps in zip(reversed(dm_rates), reversed(dm_scheme_taps)):
            extra_samples = (extra_samples * dm) + len(taps)/2

        total_dm_rate = np.prod(np.array(dm_rates))

        samples_needed = rx_metadata.numberofreceivesamples + 2 * extra_samples
        samples_needed = int(math.ceil(float(samples_needed)/float(total_dm_rate))) * total_dm_rate

        offset_to_first_rx_sample = int(sp_packet.offset_to_first_rx_sample * rx_rate)


        sample_time_diff = rx_metadata.sequence_start_time - rx_metadata.initialization_time
        sample_in_time = (sample_time_diff * rx_rate) + offset_to_first_rx_sample - extra_samples

        start_sample = int(math.fmod(sample_in_time, rx_metadata.ringbuffer_size))

        indices = np.arange(start_sample, samples_needed)

        request = so.recv_bytes(dspbegin_to_brian, sig_options.brian_to_dspbegin_identity)
        msg = 'Send start ack for sequence num #' + str(sp_packet.sequence_num())
        so.send_data(dspbegin_to_brian, sig_options.brian_to_dspbegin_identity)

        main_buffer = ringbuffer[:sig_options.main_antenna_count,:]
        main_sequence_samples = main_buffer.take(indices, axis=1, mode='wrap')

        processed_main_samples = dsp.DSP(main_sequence_samples, rx_rate, dm_rates, dm_scheme_taps,
                                    mixing_freqs, main_beam_angles)
        main_corrs = dsp.DSP.correlations_from_samples(processed_main_samples.beamformed_samples,
                            processed_main_samples.beamformed_samples, output_sample_rate,
                            slice_details)

        if sig_options.intf_antenna_count > 0:
            intf_buffer = ringbuffer[sig_options.main_antenna_count:,:]
            intf_sequence_samples = intf_buffer.take(indices, axis=1, mode='wrap')

            processed_intf_samples = dsp.DSP(intf_sequence_samples, rx_rate, dm_rates, dm_scheme_taps,
                                        mixing_freqs, intf_beam_angles)

            intf_corrs = dsp.DSP.correlations_from_samples(processed_intf_samples.beamformed_samples,
                            processed_intf_samples.beamformed_samples, output_sample_rate,
                            slice_details)
            cross_corrs = dsp.DSP.correlations_from_samples(processed_main_samples.beamformed_samples,
                            processed_intf_samples.beamformed_samples, output_sample_rate,
                            slice_details)

        request = so.recv_bytes(dspend_to_brian, sig_options.brian_to_dspend_identity)
        msg = 'Send end for sequence num #' + str(sp_packet.sequence_num())
        so.send_data(dspend_to_brian, sig_options.brian_to_dspend_identity)

















