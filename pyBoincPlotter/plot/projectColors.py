
# This file is part of the py-boinc-plotter,
# which provides parsing and plotting of boinc statistics and
# badge information.
# Copyright (C) 2013 obtitus@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# END LICENCE
""" from http://boinc.netsoft-online.com/e107_plugins/forum/forum_viewtopic.php?3
"""
colors = {'climateprediction.net': (0,139,69),
          'Predictor@Home': (135,206,235),
          'SETI@home': (65,105,225),
          'Einstein@Home': (255,165,0),
          'rosetta@home': (238,130,238),
          'PrimeGrid': (205,197,191),
          'LHC@home': (255,127,80),
          'World Community Grid': (250,128,114),
          'BURP': (0,255,127),
          'SZTAKI Desktop Grid': (205,79,57),
          'uFluids': (0,0,0),
          'SIMAP': (143,188,143),
          'Folding@Home': (3,50,204),
          'MalariaControl': (30,144,255),
          'The Lattice Project': (0,100,0),
          'Pirates@Home': (127,255,0),
          'BBC Climate Change Experiment': (205,173,0),
          'Leiden Classical': (140,34,34),
          'SETI@home Beta': (152,245,255),
          'RALPH@Home': (250,240,230),
          'QMC@HOME': (144,238,144),
          'XtremLab': (130,130,130),
          'HashClash': (255,105,180),
          'cpdn seasonal': (255,255,255),
          'Chess960@Home Alpha': (165,42,42),
          'vtu@home': (255,0,0),
          'LHC@home alpha': (205,133,63),
          'TANPAKU': (189,183,107),
          'other': (255,193,37),
          'Rectilinear Crossing Number': (83,134,139),
          'Nano-Hive@Home': (193,205,193),
          'Spinhenge@home': (255,240,245),
          'RieselSieve': (205,183,158),
          'Project Neuron': (139,58,98),
          'RenderFarm@Home': (210,105,30),
          'Docking@Home': (178,223,238),
          'proteins@home': (0,0,255),
          'DepSpid': (139,90,43),
          'ABC@home': (222,184,135),
          'BOINC alpha test': (245,245,220),
          'WEP-M+2': (0,250,154),
          'Zivis Superordenador Ciudadano': (255,239,219),
          'SciLINC': (240,248,255),
          'APS@Home': (205,91,69),
          'PS3GRID': (0,139,139),
          'Superlink@Technion': (202,255,112),
          'BRaTS@Home': (255,106,106),
          'Cosmology@Home': (240,230,140),
          'SHA 1 Collision Search': (255,250,205),
          # Made up by me
          'MindModeling@Beta': (221, 221, 221)}

for key in colors:
    colors[key] = (colors[key][0]/256., 
                   colors[key][1]/256., 
                   colors[key][2]/256.)
