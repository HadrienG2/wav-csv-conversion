#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Ce programme utilise python-wavefile, numpy et scipy pour convertir un tableau texte de données audio au format
# <temps (s)><espace><signal (-1 à 1)><saut de ligne>, tel que généré par wav2float, en fichier son au format
# WAV PCM 16 bit, mono-canal, à fréquence d'échantillonage de 44.1 kHz.

import numpy, scipy.interpolate
import sys, os, os.path
from wavefile import WaveWriter, Format

def generate_output_name(input_file_name, output_ext):
    input_basename, input_ext = os.path.splitext(input_file_name)
    output_file_name = input_basename+output_ext
    nonce = 2
    while os.path.isfile(output_file_name):
        output_file_name = input_basename+'.'+str(nonce)+output_ext
        nonce += 1
    return output_file_name

def print_manual_and_die():
    print "Usage : python float2wav.py <fichier_entrée> [<fichier_sortie>]"
    exit()

# Interface en ligne de commande
if (len(sys.argv) < 2):
    print_manual_and_die()
elif (len(sys.argv) == 2):
    input_file_name = sys.argv[1]
    output_file_name = generate_output_name(input_file_name, '.wav')
elif (len(sys.argv) == 3):
    input_file_name = sys.argv[1]
    output_file_name = sys.argv[2]
else:
    print "ERREUR : Trop d'arguments en ligne de commande."
    print_manual_and_die()

# Conversion de fichiers proprement dite
try:
    # Chargement des données depuis le fichier texte, création d'une version interpolée
    with open(input_file_name, 'r') as reader:
        input_time, input_signal = numpy.loadtxt(reader, dtype=float, delimiter=" ", unpack=True)
    interpolated_input = scipy.interpolate.interp1d(input_time, input_signal)
    
    # Interpolation sur une échelle temporelle échantillonnée à 44100 Hz
    output_sample_rate = 44100
    output_duration = input_time[-1]
    output_time = numpy.linspace(0, output_duration, round(output_duration*output_sample_rate), endpoint=True)
    output_signal = interpolated_input(output_time)
    
    # Conversion du signal résultant au format attendu par wavefile, puis écriture dans le fichier
    with WaveWriter(output_file_name, samplerate=output_sample_rate, channels=1, format=Format.WAV|Format.PCM_16) as writer:
        output_data = output_signal.reshape((1, output_signal.shape[0]))
        writer.write(output_data)
                
# Gestion des erreurs simples d'accès aux fichiers
except IOError:
    if not os.path.isfile(input_file_name):
        print "ERREUR : Le fichier d'entrée ("+input_file_name+") n'existe pas."
    elif not os.access(input_file_name, os.R_OK):
        print "ERREUR : Le fichier d'entrée ("+input_file_name+") n'est pas accessible."
    elif os.path.isfile(output_file_name) and not os.access(output_file_name, os.W_OK):
        print "ERREUR : Le fichier de sortie ("+output_file_name+") n'est pas accessible."
    else:
        raise  # Je ne sais pas vraiment ce qui s'est passé.
            
