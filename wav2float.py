#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Ce programme utilise python-wavefile et numpy pour convertir un fichier audio (argument 1)
# en fichier texte (argument 2) contenant les données audio sous forme de tableau au format suivant :
#       <temps écoulé (s)><ESPACE><signal moyen comme flottant entre -1. et 1.><SAUT DE LIGNE>
#
# Il supporte tout format audio accepté par libsndfile, ce qui inclut la plupart des formats audio non
# compressés ainsi que le Ogg Vorbis et le FLAC.

import numpy, sys, os, os.path
from wavefile import WaveReader

def generate_output_name(input_file_name, output_ext):
    input_basename, input_ext = os.path.splitext(input_file_name)
    output_file_name = input_basename+output_ext
    nonce = 2
    while os.path.isfile(output_file_name):
        output_file_name = input_basename+'.'+str(nonce)+output_ext
        nonce += 1
    return output_file_name

def print_manual_and_die():
    print "Usage : python wav2float.py <fichier_entrée> [<fichier_sortie>]"
    exit()

# Interface en ligne de commande
if (len(sys.argv) < 2):
    print_manual_and_die()
elif (len(sys.argv) == 2):
    input_file_name = sys.argv[1]
    output_file_name = generate_output_name(input_file_name, '.txt')
elif (len(sys.argv) == 3):
    input_file_name = sys.argv[1]
    output_file_name = sys.argv[2]
else:
    print "ERREUR : Trop d'arguments en ligne de commande."
    print_manual_and_die()

# Conversion de fichiers proprement dite
try:
    with WaveReader(input_file_name) as reader:
        with open(output_file_name, 'w') as writer:
            # Préparation au calcul du temps écoulé
            elapsed_time_in_samples = 0
            sample_duration = 1./reader.samplerate
            
            # Lecture du fichier audio, frame par frame (l'usage de flottants est implicite)
            for frame in reader.read_iter():
                # Calcul des instants où les échantillons audio seront lus
                elapsed_time = elapsed_time_in_samples*sample_duration
                frame_duration = frame.shape[1]*sample_duration
                sample_timings = numpy.linspace(elapsed_time, elapsed_time+frame_duration, frame.shape[1], endpoint=False)
                
                # Calcul du signal moyen sur l'ensemble des canaux audio (permet de bien gérer les fichiers stéréo, 5.1, etc...)
                average_signal = frame.mean(axis=0)
                
                # Ecriture des colonnes (temps, signal moyen) dans le fichier de sortie
                output_data = numpy.column_stack((sample_timings, average_signal))
                numpy.savetxt(writer, output_data, delimiter=" ", newline="\n")
                
                # Mise à jour du temps écoulé pour l'itération suivante
                elapsed_time_in_samples = elapsed_time_in_samples + frame.shape[1]
                
    # Affichage du nombre d'échantillons dans le fichier final (pour donner des tailles de tableau aux étudiants)
    print "{0} échantillons audio convertis avec succès !".format(elapsed_time_in_samples)
                
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
            
