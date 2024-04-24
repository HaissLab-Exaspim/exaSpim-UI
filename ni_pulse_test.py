import nidaqmx
import numpy as np
from pathlib import Path
from nidaqmx.system.device import Device
from time import sleep
from nidaqmx.constants import (Level, 
                               Edge, 
                               Slope, 
                               TaskMode, 
                               TerminalConfiguration, 
                               AOIdleOutputBehavior, 
                               AcquisitionType as AcqType, 
                               FrequencyUnits as Freq,
                               SourceSelection,
                               )
import matplotlib.pyplot as plt

dev_name = "Dev1"
samples_per_sec = 10000.0
livestream_frequency_hz = 15

class NI:
    def __init__(self):
        self.dev_name = 'Dev1'
        self.dev = Device(self.dev_name)
        self.dev.reset_device()
        sleep(2.0)
        self.samples_per_sec = 10000.0

        # self.period_time_s = (
        #     ( 20.44 * 10640 / 1.0e6)
        #     + 0.05
        #     + 0.05
        #     + 489.0 * 20.44 / 1.0e6
        # )
        self.ao_names_to_channels = {"Camera": 1, "Laser":2}
        # Total samples is the sum of the samples for every used laser channel.
        # self.daq_samples = round(self.samples_per_sec * self.period_time_s)
        self.daq_samples = 3273
        self.co_task = None
        self.ao_task = None

    def get_channel_physical_name(self, channel_nb , type = "ao") -> str :
        physical_name = f"/{self.dev_name}/{type}{channel_nb}"
        return physical_name
    
    def start(self):
        if self.ao_task:
            self.ao_task.start()
        if self.co_task:
            self.co_task.start()

    def stop(self, timeout = 1.0):
        """Stop the tasks. Try waiting first before stopping."""
        try:
            self.co_task.wait_until_done(timeout)
            print("Task finished properly")
        finally:
            if self.co_task:
                self.co_task.stop()
            if self.ao_task:
                self.ao_task.stop()

    def close(self):
        if self.co_task:
            self.co_task.close()
        if self.ao_task:
            self.ao_task.close()


    def configure(self):
        """Configure the NI card to play either `frame_count` frames or
        continuously.

        :param frame_count: the number of frames to play waveforms for. If
            left unspecified, `live` must be true.
        :param live: if True, play the waveforms indefinitely. `frame_count`
            must be left unspecified in this case. Otherwise, play the
            waveforms for the specified `frame_count`.
        """

        frequency = self.samples_per_sec/self.daq_samples
        self.close()    # If tasks exist then close them
        self.dev.reset_device()

        self.co_task = nidaqmx.Task('counter_output_task')

        co_chan = self.co_task.co_channels.add_co_pulse_chan_freq(
            self.get_channel_physical_name(channel_nb="0",type="ctr"), # counter 0
            units=Freq.HZ,
            idle_state=Level.LOW,
            initial_delay=0.0,
            freq=frequency,
            duty_cycle=0.5)
        
        co_chan.co_pulse_term = self.get_channel_physical_name(channel_nb="0",type="PFI")

        self.ao_task = nidaqmx.Task("analog_output_task")
        for channel_name, channel_index in self.ao_names_to_channels.items():
            physical_name = self.get_channel_physical_name(channel_index, type = "ao")
            print(f'Adding channel {physical_name}-{channel_name} to NI task')
            if "galvo" in channel_name.lower(): 
                # safeguard for negative/positive values to AO channels, used for galvos primarily
                # TODO :hard coded, need to make this config dependant
                min_val = -1
                max_val = 10
            else :
                min_val = -0.01 # safeguard for 0 to 5V values to AO channels
                max_val = 5.1
            print(f'Channel {physical_name} voltage boundary values are {min_val} to {max_val}')
            channel = self.ao_task.ao_channels.add_ao_voltage_chan(physical_name, min_val=min_val, max_val=max_val)
            channel.ao_term_cfg = TerminalConfiguration.RSE # change the default AO chanel electrical termination configuration
            channel.ao_dac_ref_src = SourceSelection.INTERNAL
            # channel.ao_dac_ref_allow_conn_to_gnd = True
            try : 
                channel.ao_idle_output_behavior = AOIdleOutputBehavior.HIGH_IMPEDANCE
            except Exception as e:
                print(f"Could not set AOIdleOutputBehavior to HIGH_IMPEDANCE on channel {physical_name} for {channel_name}."
                               f"\nError : {e}")

        self.ao_task.timing.cfg_samp_clk_timing(
            rate=self.samples_per_sec,
            active_edge=Edge.RISING,
            sample_mode=AcqType.FINITE,
            samps_per_chan=self.daq_samples)
        self.ao_task.triggers.start_trigger.retriggerable = True

        self.ao_task.triggers.start_trigger.cfg_dig_edge_start_trig(
            trigger_source= self.get_channel_physical_name(channel_nb="0",type="PFI"),
            trigger_edge=Slope.RISING)

        self.ao_task.out_stream.output_buf_size = self.daq_samples  # Sets buffer to length of voltages
        self.ao_task.control(TaskMode.TASK_COMMIT)


    def set_pulse_count(self, pulse_count: int = None):
        """Set the number of pulses to generate or None if pulsing continuously.

        :param pulse_count: The number of pulses to generate. If 0 or
            unspecified, the counter pulses continuously.
        :return:
        """
        print(f"Setting counter task count to {pulse_count} pulses.")
        self.co_task.timing.cfg_implicit_timing(
            sample_mode=AcqType.FINITE, samps_per_chan = pulse_count)

    def load_waveforms(self):
        data = np.load(Path.home() / "Documents" / "waveforms.values.npy")
        n_data = []
        for dat, chan in zip(data, self.ao_names_to_channels.keys()) :
            print(chan)
            if len(dat) < self.daq_samples : 
                raise ValueError(f"len(dat) {len(dat)} is smaller than daq_samples {self.daq_samples}")
            print(len(dat[:self.daq_samples]))
            n_data.append(dat[:self.daq_samples])
        
        return n_data

    def generate_waveforms(self):

        data = [0.0] * self.daq_samples
        third = round(self.daq_samples / 3)
        twothird = third * 2
        data[third:twothird] = [5.0] * third 
        data[-1] = 0

        if len(self.ao_names_to_channels) > 1:
            data = [list(np.array(data, dtype = float))] * len(self.ao_names_to_channels)

        return data

    def assign_waveforms(self, data):

        if self.ao_task :
            self.ao_task.control(TaskMode.TASK_UNRESERVE)   # Unreserve buffer
            self.ao_task.out_stream.output_buf_size = self.daq_samples  # Sets buffer to length of voltages
            self.ao_task.control(TaskMode.TASK_COMMIT)

        self.ao_task.write(data, auto_start = False)

    def plot(self, data):
        for dat, chan in zip(data, self.ao_names_to_channels.keys()) :
            print(type(dat[0]))
            fig = plt.figure()
            fig.gca().plot(dat)
            fig.savefig(Path.home() / "Documents" / f"test_plot_{chan}.pdf")


if __name__ == "__main__" :

    ni = NI()
    ni.configure()
    # data = ni.load_waveforms()
    data = ni.generate_waveforms()
    ni.plot(data)
    ni.assign_waveforms(data)
    ni.set_pulse_count(500)
    ni.start()    
    ni.stop(timeout = 4294967.0)
    ni.close()