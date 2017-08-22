"""
    materials.py is a subroutine of NumBAT that defines Material objects,
    these represent dispersive lossy refractive indices and possess
    methods to interpolate n from tabulated data.

    Copyright (C) 2016  Bjorn Sturmberg, Kokou Dossou
"""

import numpy as np
from scipy.interpolate import interp1d
import matplotlib
matplotlib.use('pdf')
import matplotlib.pyplot as plt

import json
import re

data_location = '../backend/material_data/'


class Material(object):
    """ Represents a material with:

            Refractive index []
            Density [kg/m3]
            Stiffness tensor component [Pa]
            Photoelastic tensor component []
            Acoustic loss tensor component [Pa s]

    """
    def __init__(self,data_file):

        self.load_data_file(data_file)


    def load_data_file(self, data_file, alt_path=''):  
        """
        Load data from json file.
        
        Args:
            data_file  (str): name of data file located in NumBAT/backend/material_data
            alt_path  (str): non standard path to data_file
        
        """
        with open(data_location+data_file+'.json','r') as fin:
            s_in = ''.join(fin.readlines())
            s_in = re.sub(r'//.*\n','\n', s_in)

            self._params = json.loads(s_in)

            self.file_name = self._params['file_name']  # Name of this file, will be used as identifier
            self.chemical = self._params['chemical']  # Chemical composition
            self.author = self._params['author']  # Author of data
            self.date = self._params['date']  # Year of data publication/measurement
            self.institution = self._params['institution']  # Source institution
            self.doi = self._params['doi']  # doi or, failing that, the http address

            self.n = self._params['n']  # Refractive index []
            self.s = self._params['s']  # Density [kg/m3]
            self.c_11 = self._params['c_11']  # Stiffness tensor component [Pa]
            self.c_12 = self._params['c_12']  # Stiffness tensor component [Pa]
            self.c_44 = self._params['c_44']  # Stiffness tensor component [Pa]
            self.p_11 = self._params['p_11']  # Photoelastic tensor component []
            self.p_12 = self._params['p_12']  # Photoelastic tensor component []
            self.p_44 = self._params['p_44']  # Photoelastic tensor component []
            self.eta_11 = self._params['eta_11']  # Acoustic loss tensor component [Pa s]
            self.eta_12 = self._params['eta_12']  # Acoustic loss tensor component [Pa s]
            self.eta_44 = self._params['eta_44']  # Acoustic loss tensor component [Pa s]

            try:  # full anisotropic tensor components
                self.c_11 = self._params['c_11']
                self.c_12 = self._params['c_12']
                self.c_13 = self._params['c_13']
                self.c_14 = self._params['c_14']
                self.c_15 = self._params['c_15']
                self.c_16 = self._params['c_16']
                self.c_21 = self._params['c_21']
                self.c_22 = self._params['c_22']
                self.c_23 = self._params['c_23']
                self.c_24 = self._params['c_24']
                self.c_25 = self._params['c_25']
                self.c_26 = self._params['c_26']
                self.c_31 = self._params['c_31']
                self.c_32 = self._params['c_32']
                self.c_33 = self._params['c_33']
                self.c_34 = self._params['c_34']
                self.c_35 = self._params['c_35']
                self.c_36 = self._params['c_36']
                self.c_41 = self._params['c_41']
                self.c_42 = self._params['c_42']
                self.c_43 = self._params['c_43']
                self.c_44 = self._params['c_44']
                self.c_45 = self._params['c_45']
                self.c_46 = self._params['c_46']
                self.c_51 = self._params['c_51']
                self.c_52 = self._params['c_52']
                self.c_53 = self._params['c_53']
                self.c_54 = self._params['c_54']
                self.c_55 = self._params['c_55']
                self.c_56 = self._params['c_56']
                self.c_61 = self._params['c_61']
                self.c_62 = self._params['c_62']
                self.c_63 = self._params['c_63']
                self.c_64 = self._params['c_64']
                self.c_65 = self._params['c_65']
                self.c_66 = self._params['c_66']
                self.p_11 = self._params['p_11']
                self.p_12 = self._params['p_12']
                self.p_13 = self._params['p_13']
                self.p_14 = self._params['p_14']
                self.p_15 = self._params['p_15']
                self.p_16 = self._params['p_16']
                self.p_21 = self._params['p_21']
                self.p_22 = self._params['p_22']
                self.p_23 = self._params['p_23']
                self.p_24 = self._params['p_24']
                self.p_25 = self._params['p_25']
                self.p_26 = self._params['p_26']
                self.p_31 = self._params['p_31']
                self.p_32 = self._params['p_32']
                self.p_33 = self._params['p_33']
                self.p_34 = self._params['p_34']
                self.p_35 = self._params['p_35']
                self.p_36 = self._params['p_36']
                self.p_41 = self._params['p_41']
                self.p_42 = self._params['p_42']
                self.p_43 = self._params['p_43']
                self.p_44 = self._params['p_44']
                self.p_45 = self._params['p_45']
                self.p_46 = self._params['p_46']
                self.p_51 = self._params['p_51']
                self.p_52 = self._params['p_52']
                self.p_53 = self._params['p_53']
                self.p_54 = self._params['p_54']
                self.p_55 = self._params['p_55']
                self.p_56 = self._params['p_56']
                self.p_61 = self._params['p_61']
                self.p_62 = self._params['p_62']
                self.p_63 = self._params['p_63']
                self.p_64 = self._params['p_64']
                self.p_65 = self._params['p_65']
                self.p_66 = self._params['p_66']
                self.eta_11 = self._params['eta_11']
                self.eta_12 = self._params['eta_12']
                self.eta_13 = self._params['eta_13']
                self.eta_14 = self._params['eta_14']
                self.eta_15 = self._params['eta_15']
                self.eta_16 = self._params['eta_16']
                self.eta_21 = self._params['eta_21']
                self.eta_22 = self._params['eta_22']
                self.eta_23 = self._params['eta_23']
                self.eta_24 = self._params['eta_24']
                self.eta_25 = self._params['eta_25']
                self.eta_26 = self._params['eta_26']
                self.eta_31 = self._params['eta_31']
                self.eta_32 = self._params['eta_32']
                self.eta_33 = self._params['eta_33']
                self.eta_34 = self._params['eta_34']
                self.eta_35 = self._params['eta_35']
                self.eta_36 = self._params['eta_36']
                self.eta_41 = self._params['eta_41']
                self.eta_42 = self._params['eta_42']
                self.eta_43 = self._params['eta_43']
                self.eta_44 = self._params['eta_44']
                self.eta_45 = self._params['eta_45']
                self.eta_46 = self._params['eta_46']
                self.eta_51 = self._params['eta_51']
                self.eta_52 = self._params['eta_52']
                self.eta_53 = self._params['eta_53']
                self.eta_54 = self._params['eta_54']
                self.eta_55 = self._params['eta_55']
                self.eta_56 = self._params['eta_56']
                self.eta_61 = self._params['eta_61']
                self.eta_62 = self._params['eta_62']
                self.eta_63 = self._params['eta_63']
                self.eta_64 = self._params['eta_64']
                self.eta_65 = self._params['eta_65']
                self.eta_66 = self._params['eta_66']
                self.anisotropic = True
            except KeyError:
                self.anisotropic = False


    def rotate_axis(self, theta, rotate_axis):
        """ Rotate crystal axis by theta radians.

            Args:
                theta  (float): Angle in radians

                rotate_axis  (str): Axis around which to rotate

            Returns:
                ``Material`` object with rotated tensor values
        """

        if self.anisotropic is False:            
            # STIFFNESS
            # unrotated values
            old_c_11 = self.c_11
            old_c_12 = self.c_12
            old_c_44 = self.c_44
            self.c_14 = self.c_15 = 0
            self.c_24 = self.c_25 = 0 
            self.c_34 = self.c_35 = self.c_36 = 0
            self.c_41 = self.c_42 = self.c_43 = self.c_45 = self.c_46 = 0
            self.c_51 = self.c_52 = self.c_53 = self.c_54 = self.c_56 = 0
            self.c_63 = self.c_64 = self.c_65 = 0
            # check isotropic values
            self.c_22 = self.c_11
            self.c_33 = self.c_11
            self.c_21 = self.c_12
            self.c_13 = self.c_12
            self.c_23 = self.c_12
            self.c_31 = self.c_32 = self.c_12
            self.c_55 = self.c_44
            self.c_66 = self.c_44
            self.c_16 = self.c_61 = 0 # only 4 comps change from zero to non-zero in rotation
            self.c_26 = self.c_62 = 0 # only 4 comps change from zero to non-zero in rotation   

            tensor = [[self.c_11, self.c_12, self.c_13, self.c_14, self.c_15, self.c_16],
                      [self.c_21, self.c_22, self.c_23, self.c_24, self.c_25, self.c_26],
                      [self.c_31, self.c_32, self.c_33, self.c_34, self.c_35, self.c_36],
                      [self.c_41, self.c_42, self.c_43, self.c_44, self.c_45, self.c_46],
                      [self.c_51, self.c_52, self.c_53, self.c_54, self.c_55, self.c_56],
                      [self.c_61, self.c_62, self.c_63, self.c_64, self.c_65, self.c_66]]
            tensor = np.array(tensor)
            tensor_rotated = rotate_tensor(tensor, theta, rotate_axis)
            print("original \n", tensor)
            print("matrix rotated \n", tensor_rotated)
            [[self.c_11, self.c_12, self.c_13, self.c_14, self.c_15, self.c_16],
            [self.c_21, self.c_22, self.c_23, self.c_24, self.c_25, self.c_26],
            [self.c_31, self.c_32, self.c_33, self.c_34, self.c_35, self.c_36],
            [self.c_41, self.c_42, self.c_43, self.c_44, self.c_45, self.c_46],
            [self.c_51, self.c_52, self.c_53, self.c_54, self.c_55, self.c_56],
            [self.c_61, self.c_62, self.c_63, self.c_64, self.c_65, self.c_66]] = tensor_rotated

            # rotated values
            self.c_11 = self.c_22 = 0.25*(old_c_11*(3+np.cos(4*theta)) + (old_c_12 + 2*old_c_44)*(1-np.cos(4*theta)))
            self.c_33 = old_c_11
            self.c_12 = self.c_21 = 0.25*(old_c_12*(3+np.cos(4*theta)) + (old_c_11 - 2*old_c_44)*(1-np.cos(4*theta)))
            self.c_13 = self.c_23 = self.c_31 = self.c_32 = old_c_12
            self.c_44 = self.c_55 = old_c_44
            self.c_66 = 0.25*(2*old_c_44*(1+np.cos(4*theta)) + (old_c_11 - old_c_12)*(1-np.cos(4*theta)))
            self.c_16 = self.c_61 = 0.25*np.sin(4*theta)*(2*old_c_44 + old_c_12 - old_c_11)
            self.c_26 = self.c_62 = 0.25*np.sin(4*theta)*(old_c_11 - old_c_12 - 2*old_c_44)

            # print("Kipplaus")
            # v_xy = v_yx = .361
            # v_yz = v_zy = .062 #.278
            # v_xz = v_zx = .278 #.062
            # E_x = 169e9
            # E_y = 169e9 #130e9
            # E_z = 130e9 #169e9
            # G_yz = 79.6e9
            # G_zx = 79.6e9 #50.9e9
            # G_xy = 50.9e9 #79.6e9         
            # Delta = (1- v_xy*v_yx - v_yz*v_zy - v_zx*v_xz - 2*v_xy*v_yz*v_zx)/(E_x*E_y*E_z)
            # self.c_11 = (1 - v_yz*v_zy)/(E_y*E_z*Delta)
            # self.c_12 = (v_yx + v_yz*v_zy)/(E_y*E_z*Delta)
            # self.c_13 = (v_zx + v_yx*v_zy)/(E_y*E_z*Delta)
            # self.c_21 = (v_xy + v_xz*v_zy)/(E_x*E_z*Delta)
            # self.c_22 = (1 - v_zx*v_xz)/(E_x*E_z*Delta)
            # self.c_23 = (v_zy + v_zx*v_xy)/(E_x*E_z*Delta)
            # self.c_31 = (v_xz + v_xy*v_yz)/(E_y*E_x*Delta)
            # self.c_32 = (v_yz + v_xz*v_yx)/(E_y*E_x*Delta)
            # self.c_33 = (1 - v_yx*v_xy)/(E_y*E_x*Delta)
            # self.c_44 = G_yz
            # self.c_55 = G_zx
            # self.c_66 = G_xy

            # print(self.c_11)
            # print(self.c_12)
            # print(self.c_13)
            # print(self.c_21)
            # print(self.c_22)
            # print(self.c_23)
            # print(self.c_31)
            # print(self.c_32)
            # print(self.c_33)
            # print(self.c_44)
            # print(self.c_55)
            # print(self.c_66)
            # print(self.c_16)
            # print(self.c_26)
            tensor = [[self.c_11, self.c_12, self.c_13, self.c_14, self.c_15, self.c_16],
                      [self.c_21, self.c_22, self.c_23, self.c_24, self.c_25, self.c_26],
                      [self.c_31, self.c_32, self.c_33, self.c_34, self.c_35, self.c_36],
                      [self.c_41, self.c_42, self.c_43, self.c_44, self.c_45, self.c_46],
                      [self.c_51, self.c_52, self.c_53, self.c_54, self.c_55, self.c_56],
                      [self.c_61, self.c_62, self.c_63, self.c_64, self.c_65, self.c_66]]
            tensor = np.array(tensor)
            print("manual rotated \n", tensor)
           
            # PHOTOELASTIC
            # # unrotated values
            # old_p_11 = self.p_11
            # old_p_12 = self.p_12
            # old_p_44 = self.p_44
            self.p_14 = self.p_15 = 0
            self.p_24 = self.p_25 = 0 
            self.p_34 = self.p_35 = self.p_36 = 0
            self.p_41 = self.p_42 = self.p_43 = self.p_45 = self.p_46 = 0
            self.p_51 = self.p_52 = self.p_53 = self.p_54 = self.p_56 = 0
            self.p_63 = self.p_64 = self.p_65 = 0
            # check isotropic values
            self.p_22 = self.p_11
            self.p_33 = self.p_11
            self.p_21 = self.p_12
            self.p_13 = self.p_12
            self.p_23 = self.p_12
            self.p_31 = self.p_32 = self.p_12
            self.p_55 = self.p_44
            self.p_66 = self.p_44
            self.p_16 = self.p_61 = 0
            self.p_26 = self.p_62 = 0

            tensor = [[self.p_11, self.p_12, self.p_13, self.p_14, self.p_15, self.p_16],
                      [self.p_21, self.p_22, self.p_23, self.p_24, self.p_25, self.p_26],
                      [self.p_31, self.p_32, self.p_33, self.p_34, self.p_35, self.p_36],
                      [self.p_41, self.p_42, self.p_43, self.p_44, self.p_45, self.p_46],
                      [self.p_51, self.p_52, self.p_53, self.p_54, self.p_55, self.p_56],
                      [self.p_61, self.p_62, self.p_63, self.p_64, self.p_65, self.p_66]]
            tensor = np.array(tensor)
            tensor_rotated = rotate_tensor(tensor, theta, rotate_axis)
            [[self.p_11, self.p_12, self.p_13, self.p_14, self.p_15, self.p_16],
            [self.p_21, self.p_22, self.p_23, self.p_24, self.p_25, self.p_26],
            [self.p_31, self.p_32, self.p_33, self.p_34, self.p_35, self.p_36],
            [self.p_41, self.p_42, self.p_43, self.p_44, self.p_45, self.p_46],
            [self.p_51, self.p_52, self.p_53, self.p_54, self.p_55, self.p_56],
            [self.p_61, self.p_62, self.p_63, self.p_64, self.p_65, self.p_66]] = tensor_rotated

            # # rotated values
            # self.p_11 = self.p_22 = 0.25*(old_p_11*(3+np.cos(4*theta)) + (old_p_12 + 2*old_p_44)*(1-np.cos(4*theta)))
            # self.p_33 = old_p_11
            # self.p_12 = self.p_21 = 0.25*(old_p_12*(3+np.cos(4*theta)) + (old_p_11 - 2*old_p_44)*(1-np.cos(4*theta)))
            # self.p_13 = self.p_23 = self.p_31 = self.p_32 = old_p_12
            # self.p_44 = self.p_55 = old_p_44
            # self.p_66 = 0.25*(2*old_p_44*(1+np.cos(4*theta)) + (old_p_11 - old_p_12)*(1-np.cos(4*theta)))
            # self.p_16 = self.p_61 = 0.25*np.sin(4*theta)*(2*old_p_44 + old_p_12 - old_p_11)
            # self.p_26 = self.p_62 = 0.25*np.sin(4*theta)*(old_p_11 - old_p_12 - 2*old_p_44)

            # ETA
            self.eta_14 = self.eta_15 = 0
            self.eta_24 = self.eta_25 = 0 
            self.eta_34 = self.eta_35 = self.eta_36 = 0
            self.eta_41 = self.eta_42 = self.eta_43 = self.eta_45 = self.eta_46 = 0
            self.eta_51 = self.eta_52 = self.eta_53 = self.eta_54 = self.eta_56 = 0
            self.eta_63 = self.eta_64 = self.eta_65 = 0
            # check isotropic values
            self.eta_22 = self.eta_11
            self.eta_33 = self.eta_11
            self.eta_21 = self.eta_12
            self.eta_13 = self.eta_12
            self.eta_23 = self.eta_12
            self.eta_31 = self.eta_32 = self.eta_12
            self.eta_55 = self.eta_44
            self.eta_66 = self.eta_44
            self.eta_16 = self.eta_61 = 0
            self.eta_26 = self.eta_62 = 0

            tensor = [[self.eta_11, self.eta_12, self.eta_13, self.eta_14, self.eta_15, self.eta_16],
                      [self.eta_21, self.eta_22, self.eta_23, self.eta_24, self.eta_25, self.eta_26],
                      [self.eta_31, self.eta_32, self.eta_33, self.eta_34, self.eta_35, self.eta_36],
                      [self.eta_41, self.eta_42, self.eta_43, self.eta_44, self.eta_45, self.eta_46],
                      [self.eta_51, self.eta_52, self.eta_53, self.eta_54, self.eta_55, self.eta_56],
                      [self.eta_61, self.eta_62, self.eta_63, self.eta_64, self.eta_65, self.eta_66]]
            tensor = np.array(tensor)
            tensor_rotated = rotate_tensor(tensor, theta, rotate_axis)
            [[self.eta_11, self.eta_12, self.eta_13, self.eta_14, self.eta_15, self.eta_16],
            [self.eta_21, self.eta_22, self.eta_23, self.eta_24, self.eta_25, self.eta_26],
            [self.eta_31, self.eta_32, self.eta_33, self.eta_34, self.eta_35, self.eta_36],
            [self.eta_41, self.eta_42, self.eta_43, self.eta_44, self.eta_45, self.eta_46],
            [self.eta_51, self.eta_52, self.eta_53, self.eta_54, self.eta_55, self.eta_56],
            [self.eta_61, self.eta_62, self.eta_63, self.eta_64, self.eta_65, self.eta_66]] = tensor_rotated

            # self.anisotropic = True        

        else:
            raise NotImplementedError("Have not implemented rotation of anisotropic tensors.")

# Arrag that converts between 4th rank tensors in terms of x,y,z and Voigt notation
to_Voigt = np.array([[0,5,4], [5,1,3], [4,3,2]]) #[[xx,xy,xz], [yx,yy,yz], [zx,zy,zz]]


def rotation_matrix_sum(i, j, k, l, tensor_orig, mat_R):
    tensor_prime_comp = 0
    for q in range(3):
        for r in range(3):
            V1 = to_Voigt[q,r]
            for s in range(3):
                for t in range(3):
                    V2 = to_Voigt[s,t]
                    tensor_prime_comp += mat_R[i,q] * mat_R[j,r] * mat_R[k,s] * mat_R[l,t] * tensor_orig[V1,V2]

    return tensor_prime_comp


def rotate_tensor(tensor_orig, theta, rotation_axis):
    if rotation_axis == 'x-axis':
        mat_R = np.array([[1,0,0], [0,np.cos(theta),-np.sin(theta)], [0,np.sin(theta),np.cos(theta)]])
    if rotation_axis == 'y-axis':
        mat_R = np.array([[np.cos(theta),0,np.sin(theta)], [0,1,0], [-np.sin(theta),0,np.cos(theta)]])
    if rotation_axis == 'z-axis':
        mat_R = np.array([[np.cos(theta),-np.sin(theta),0], [np.sin(theta),np.cos(theta),0], [0,0,1]])

    tensor_prime = np.zeros((6,6))
    for i in range(3):
        for j in range(3):
            V1 = to_Voigt[i,j]
            for k in range(3):
                for l in range(3):
                    V2 = to_Voigt[k,l]
                    tensor_prime[V1,V2] = rotation_matrix_sum(i,j,k,l,tensor_orig,mat_R)

    return tensor_prime


def isotropic_stiffness(E, v):
    """
    Calculate the stiffness matrix components of isotropic 
    materials, given the two free parameters.

    Ref: www.efunda.com/formulae/solid_mechanics/mat_mechanics/hooke_isotropic.cfm

    Args:
        E  (float): Youngs_modulus
        v  (float): Poisson_ratio
    """
    c_11 = E*(1-v)/((1+v)*(1-2*v))
    c_12 = E*(v)/((1+v)*(1-2*v))
    c_44 = (E*(1-2*v)/((1+v)*(1-2*v)))/2

    return c_11, c_12, c_44


Vacuum = Material("Vacuum")

Si_2016_Smith = Material("Si_2016_Smith")
Si_2015_Van_Laer = Material("Si_2015_Van_Laer")
Si_2013_Laude = Material("Si_2013_Laude")
Si_test_anisotropic = Material("Si_test_anisotropic")

SiO2_2016_Smith = Material("SiO2_2016_Smith")
SiO2_2015_Van_Laer = Material("SiO2_2015_Van_Laer")
SiO2_2013_Laude = Material("SiO2_2013_Laude")

As2S3_2017_Morrison = Material("As2S3_2017_Morrison")
As2S3_2016_Smith = Material("As2S3_2016_Smith")

GaAs_2016_Smith = Material("GaAs_2016_Smith")
