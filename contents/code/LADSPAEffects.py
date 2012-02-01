# -*- coding: utf-8 -*-
# copyright 2011  Nik Lutz nik.lutz@gmail.com
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

class LADSPAEffects:

    effects = { "mbeq" : {          "name" : "Multiband EQ",
                                    "plugin": "mbeq_1197",
                                    "control": "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0",
                                    "range" : [[-70, 30],[-70, 30],[-70, 30],
                                                [-70, 30],[-70, 30],[-70, 30],
                                                [-70, 30],[-70, 30],[-70, 30],
                                                [-70, 30],[-70, 30],[-70, 30],
                                                [-70, 30],[-70, 30],[-70, 30]],
                                    "scale" : [1,1,1, 1,1,1, 1,1,1, 1,1,1, 1,1,1],
                                    "labels" : ["50Hz","100Hz","156Hz",
                                                "220Hz","311Hz","440Hz",
                                                "622Hz","880Hz","1250Hz",
                                                "1750Hz","2500Hz","3500Hz",
                                                "5000Hz","10000Hz","20000Hz",] },

                "dj_eq_mono" : {    "name" : "DJ Equalizer",
                                    "plugin": "dj_eq_1901",
                                    "control": "0,0,0",
                                    "range" : [[-70, 6],[-70, 6],[-70, 6]],
                                    "scale" : [1,1,1],
                                    "labels" : ["Lo gain","Mid gain","Hi gain"]},
                "flanger" :    {    "name" : "Flanger",
                                    "plugin": "flanger_1191",
                                    "control": "6.325,2.5,0.33437,0",
                                    "range" : [[0.1, 25],[0, 10],[0, 100],[-1, 1]],
                                    "scale" : [100,10,10, 10],
                                    "labels" : ["Delay base","Max slowdown","LFO frequency", "Feedback"] },
                "pitchScale" :    {    "name" : "Pitch Scaler",
                                    "plugin": "pitch_scale_1193",
                                    "control": "1",
                                    "range" : [[0.5, 2]],
                                    "scale" : [100],
                                    "labels" : ["Co-efficient"]},
                "multivoiceChorus" : {"name" : "Multivoice Chorus",
                                    "plugin": "multivoice_chorus_1201",
                                    "control": "1,10,0.5,1,9,0",
                                    "range" : [[1, 8], [10, 40], [0, 2], [0, 5], [2, 30], [-20, 0]],
                                    "scale" : [1,10,10,10, 10, 10 ],
                                    "labels" : ["Voices", "Delay base", "Voice separation", "Detune", "LFO frequency", "Output attenuation"] } }

        ## GOOD
        #sink_name="sink_name=ladspa_output.dj_eq_1901.dj_eq."+str(self.ladspa_index)
        #plugin = "plugin=dj_eq_1901"
        #label = "label=dj_eq_mono"
        #control = "control=0,0,0"

        # fun!
        #sink_name="sink_name=ladspa_output.multivoice_chorus_1201.multivoiceChorus."+str(self.ladspa_index)
        #plugin = "plugin=multivoice_chorus_1201"
        #label = "label=multivoiceChorus"
        #control = "control=0,0,0,0,0,0"

        ## fun
        #sink_name="sink_name=ladspa_output.pitch_scale_1193.pitchScale."+str(self.ladspa_index)
        #plugin = "plugin=pitch_scale_1193"
        #label = "label=pitchScale"
        #control = "control=1.9"

        ##works but ..
        #sink_name="sink_name=ladspa_output.flanger_1191.flanger."+str(self.ladspa_index)
        #plugin = "plugin=flanger_1191"
        #label = "label=flanger"
        #control = "control=0,0,0,0"

        ## not working?
        #sink_name="sink_name=ladspa_output.df_flanger_1438.djFlanger."+str(self.ladspa_index)
        #plugin = "plugin=dj_flanger_1438"
        #label = "label=djFlanger"
        #control = "control=0,0,0,0"

        ## ..
        #sink_name="sink_name=ladspa_output.phasers_1217.autoPhaser."+str(self.ladspa_index)
        #plugin = "plugin=phasers_1217"
        #label = "label=autoPhaser"
        #control = "control=0,0,0,0,0"

        ## does not work
        #sink_name="sink_name=ladspa_output.dj_eq_1901.dj_eq."+str(self.ladspa_index)
        #plugin = "plugin=dj_eq_1901"
        #label = "label=dj_eq"
        #control = "control=0,0,0"

        ## no
        #sink_name="sink_name=ladspa_output.decay_1886.decay."+str(self.ladspa_index)
        #plugin = "plugin=decay_1886"
        #label = "label=decay"
        #control = "control=0"

        ## i dont hear it
        #sink_name="sink_name=ladspa_output.delay_1898.delay_n."+str(self.ladspa_index)
        #plugin = "plugin=delay_1898"
        #label = "label=delay_n"
        #control = "control=0,0"

        ## i dont hear it
        #sink_name="sink_name=ladspa_output.delay_1898.delay_l."+str(self.ladspa_index)
        #plugin = "plugin=delay_1898"
        #label = "label=delay_l"
        #control = "control=0,0"

        ## i dont hear it
        #sink_name="sink_name=ladspa_output.delay_1898.delay_c."+str(self.ladspa_index)
        #plugin = "plugin=delay_1898"
        #label = "label=delay_c"
        #control = "control=0,0"

        ## does not work (stereo)
        #sink_name="sink_name=ladspa_output.karaoke_1409.karaoke."+str(self.ladspa_index)
        #plugin = "plugin=karaoke_1409"
        #label = "label=karaoke"
        #control = "control=-50"

        ## not work (stereo)
        #sink_name="sink_name=ladspa_output.plate_1423.plate."+str(self.ladspa_index)
        #plugin = "plugin=plate_1423"
        #label = "label=plate"
        #control = "control=0,0,0"

        ## less fun
        #sink_name="sink_name=ladspa_output.pitch_scale_1194.pitchScaleHQ."+str(self.ladspa_index)
        #plugin = "plugin=pitch_scale_1194"
        #label = "label=pitchScaleHQ"
        #control = "control=1.9"
