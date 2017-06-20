"""
    plotting.py is a subroutine of NumBAT that contains numerous plotting
    routines.

    Copyright (C) 2016  Bjorn Sturmberg
"""

import os
import numpy as np
from scipy import sqrt
import subprocess
from matplotlib.mlab import griddata
from scipy import interpolate
import matplotlib
matplotlib.use('pdf')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from mpl_toolkits.axes_grid1 import make_axes_locatable
# import matplotlib.cm as cm

try: plt.style.use('bjornstyle')
except (ValueError, IOError, AttributeError): "Preferred matplotlib style file not found."


# font = {'family' : 'normal',
#         'weight' : 'bold',
#         'size'   : 18}
# matplotlib.rc('font', **font)
linesstrength = 2.5
title_font = 25


#### Natural constants ########################################################
ASTM15_tot_I   = 900.084            # Integral ASTM 1.5 solar irradiance W/m**2
Plancks_h      = 6.62606957*1e-34   # Planck's constant
speed_c        = 299792458          # Speed of light in vacuum
charge_e       = 1.602176565*1e-19  # Charge of an electron
###############################################################################


#### Short utility functions ##################################################
def zeros_int_str(zero_int):
    """ Convert integer into string with '0' in place of ' '. """
    # if zero_int == 0:
    #     fmt_string = '0000'
    # else:
    #     string = '%4.0f' % zero_int
    #     fmt_string = string.replace(' ','0')
    string = '%4.0f' % zero_int
    fmt_string = string.replace(' ','0')
    return fmt_string

###############################################################################


def gain_specta(sim_AC, SBS_gain, SBS_gain_PE, SBS_gain_MB, alpha, k_AC,
                EM_ival1, EM_ival2, AC_ival, freq_min, freq_max, num_interp_pts=3000,
                pdf_png='png', save_txt=False, add_name=''):
    r""" Construct the SBS gain spectrum, built from Lorentzian peaks of the individual modes.
        Note the we use the spectral linewidth of the resonances

        .. math:: 

            \gamma = v_g \alpha
        where $v_g$ the group velocity of the mode and $\theta$ is the detuning frequency. 
        We transform from k-space of Eq. 91 to frequency space

        .. math:: 

            \Gamma =  \frac{2 \omega \Omega {\rm Re} (Q_1 Q_1^*)}{P_e P_e P_{ac}} \frac{1}{\alpha} \frac{\alpha^2}{\alpha^2 + \kappa^2},\\
            \Gamma =  \frac{2 \omega \Omega {\rm Re} (Q_1 Q_1^*)}{P_e P_e P_{ac}} \frac{1}{\alpha} \frac{\gamma^2}{\gamma^2 + \theta^2},
            

        Args:
            sim_AC : An AC :Struct: instance that has had calc_modes calculated

            SBS_gain  (array): Totlat SBS gain of modes.

            SBS_gain_PE  (array): Moving Bountary gain of modes.

            SBS_gain_MB  (array): Photoelastic gain of modes.

            alpha  (array): Acoustic loss of each mode.

            k_AC  (float): Acoustic wavevector.

            freq_min  (float): Minimum of frequency range.

            freq_max  (float): Maximum of frequency range.
            
        Keyword Args:
    """
    tune_steps = 5e4
    tune_range = 10 # GHz
    # Construct an odd range of frequencies that is guaranteed to include 
    # the central resonance frequency.
    detuning_range = np.append(np.linspace(-1*tune_range, 0, tune_steps),
                       np.linspace(0, tune_range, tune_steps)[1:])*1e9 # GHz
    # Line width of resonances should be v_g * alpha,
    # but we don't have convenient access to v_g, therefore
    # phase velocity as approximation to group velocity
    phase_v = 2*np.pi*sim_AC.Eig_values/k_AC
    linewidth = phase_v*alpha/(2*np.pi)

    interp_grid = np.linspace(freq_min, freq_max, num_interp_pts)
    interp_values = np.zeros(num_interp_pts)

    plt.figure()
    plt.clf()
    if AC_ival == 'All':
        for AC_i in range(len(alpha)):
            gain_list = np.real(SBS_gain[EM_ival1,EM_ival2,AC_i]
                         *linewidth[AC_i]**2/(linewidth[AC_i]**2 + detuning_range**2))
            freq_list_GHz = np.real(sim_AC.Eig_values[AC_i] + detuning_range)*1e-9
            plt.plot(freq_list_GHz, gain_list)
            if save_txt:
                save_array = (freq_list_GHz, gain_list)
                np.savetxt('gain_spectra-mode_comps%(add)s-%(mode)i.csv' 
                            % {'add' : add_name, 'mode' : AC_i}, 
                            save_array, delimiter=',')
            # set up an interpolation for summing all the gain peaks
            interp_spectrum = np.interp(interp_grid, freq_list_GHz, gain_list)
            interp_values += interp_spectrum
    plt.plot(interp_grid, interp_values, 'k', linewidth=3, label="Total")
    if save_txt:
        save_array = (interp_grid, interp_values)
        np.savetxt('gain_spectra-mode_comps%(add)s-Total.csv' 
                    % {'add' : add_name}, 
                    save_array, delimiter=',')
    plt.legend(loc=0)
    if freq_min and freq_max:
        plt.xlim(freq_min,freq_max)
    plt.xlabel('Frequency (GHz)')
    plt.ylabel('Gain (1/Wm)')


    if pdf_png=='png':
        plt.savefig('gain_spectra-mode_comps%(add)s.png' % {'add' : add_name})
    elif pdf_png=='pdf':
        plt.savefig('gain_spectra-mode_comps%(add)s.pdf' % {'add' : add_name})
    plt.close()

    plt.figure()
    plt.clf()
    if AC_ival == 'All':
        for AC_i in range(len(alpha)):
            gain_list = np.real(SBS_gain[EM_ival1,EM_ival2,AC_i]
                         *linewidth[AC_i]**2/(linewidth[AC_i]**2 + detuning_range**2))
            freq_list_GHz = np.real(sim_AC.Eig_values[AC_i] + detuning_range)*1e-9
            plt.plot(freq_list_GHz, 10*np.log10(np.exp(abs(gain_list)*6.5e-3))) 
            # 6.5e-3 is the estimated value of L_eff*P_pump/A_eff in https://arxiv.org/abs/1702.05233
            if save_txt:
                save_array = (freq_list_GHz, 20*np.log10(abs(gain_list)))
                np.savetxt('gain_spectra-mode_comps-dB%(add)s-%(mode)i.csv' 
                            % {'add' : add_name, 'mode' : AC_i}, 
                            save_array, delimiter=',')
            # set up an interpolation for summing all the gain peaks
            interp_spectrum = np.interp(interp_grid, freq_list_GHz, gain_list)
            interp_values += interp_spectrum
    plt.plot(interp_grid, 10*np.log10(np.exp(abs(interp_values)*6.5e-3)), 'k', linewidth=3, label="Total")
    if save_txt:
        save_array = (interp_grid, 10*np.log10(np.exp(abs(interp_values)*6.5e-3)))
        np.savetxt('gain_spectra-mode_comps-dB%(add)s-Total.csv' 
                    % {'add' : add_name}, 
                    save_array, delimiter=',')
    plt.legend(loc=0)
    if freq_min and freq_max:
        plt.xlim(freq_min,freq_max)
    plt.xlabel('Frequency (GHz)')
    plt.ylabel('Gain (dB)')

    if pdf_png=='png':
        plt.savefig('gain_spectra-mode_comps-dB%(add)s.png' % {'add' : add_name})
    elif pdf_png=='pdf':
        plt.savefig('gain_spectra-mode_comps-dB%(add)s.pdf' % {'add' : add_name})
    plt.close()


    interp_values = np.zeros(num_interp_pts)
    interp_values_PE = np.zeros(num_interp_pts)
    interp_values_MB = np.zeros(num_interp_pts)
    plt.figure()
    plt.clf()
    if AC_ival == 'All':
        for AC_i in range(len(alpha)):
            gain_list = np.real(SBS_gain[EM_ival1,EM_ival2,AC_i]
                         *linewidth[AC_i]**2/(linewidth[AC_i]**2 + detuning_range**2))
            freq_list_GHz = np.real(sim_AC.Eig_values[AC_i] + detuning_range)*1e-9
            interp_spectrum = np.interp(interp_grid, freq_list_GHz, gain_list)
            interp_values += interp_spectrum

            gain_list_PE = np.real(SBS_gain_PE[EM_ival1,EM_ival2,AC_i]
                         *linewidth[AC_i]**2/(linewidth[AC_i]**2 + detuning_range**2))
            interp_spectrum_PE = np.interp(interp_grid, freq_list_GHz, gain_list_PE)
            interp_values_PE += interp_spectrum_PE

            gain_list_MB = np.real(SBS_gain_MB[EM_ival1,EM_ival2,AC_i]
                         *linewidth[AC_i]**2/(linewidth[AC_i]**2 + detuning_range**2))
            interp_spectrum_MB = np.interp(interp_grid, freq_list_GHz, gain_list_MB)
            interp_values_MB += interp_spectrum_MB
    plt.plot(interp_grid, interp_values, 'k', linewidth=3, label="Total")
    plt.plot(interp_grid, interp_values_PE, 'r', linewidth=3, label="PE")
    plt.plot(interp_grid, interp_values_MB, 'g', linewidth=3, label="MB")
    plt.legend(loc=0)
    if freq_min and freq_max:
        plt.xlim(freq_min,freq_max)
    plt.xlabel('Frequency (GHz)')
    plt.ylabel('Gain (1/Wm)')

    if pdf_png=='png':
        plt.savefig('gain_spectra-MB_PE_comps%(add)s.png' % {'add' : add_name})
    elif pdf_png=='pdf':
        plt.savefig('gain_spectra-MB_PE_comps%(add)s.pdf' % {'add' : add_name})
    plt.close()

    if save_txt:
        save_array = (interp_grid, interp_values)
        np.savetxt('gain_spectra-MB_PE_comps%(add)s-Total.csv' 
                    % {'add' : add_name}, 
                    save_array, delimiter=',')
        save_array = (interp_grid, interp_values_PE)
        np.savetxt('gain_spectra-MB_PE_comps%(add)s-PE.csv' 
                    % {'add' : add_name}, 
                    save_array, delimiter=',')
        save_array = (interp_grid, interp_values_MB)
        np.savetxt('gain_spectra-MB_PE_comps%(add)s-MB.csv' 
                    % {'add' : add_name}, 
                    save_array, delimiter=',')

    plt.figure()
    plt.clf()
    plt.plot(interp_grid, 10*np.log10(np.exp(abs(interp_values)*6.5e-3)), 'k', linewidth=3, label="Total")
    plt.plot(interp_grid, 10*np.log10(np.exp(abs(interp_values_PE)*6.5e-3)), 'r', linewidth=3, label="PE")
    plt.plot(interp_grid, 10*np.log10(np.exp(abs(interp_values_MB)*6.5e-3)), 'g', linewidth=3, label="MB")
    plt.legend(loc=0)
    if freq_min and freq_max:
        plt.xlim(freq_min,freq_max)
    plt.xlabel('Frequency (GHz)')
    plt.ylabel('Gain (dB)')

    if pdf_png=='png':
        plt.savefig('gain_spectra-MB_PE_comps-dB%(add)s.png' % {'add' : add_name})
    elif pdf_png=='pdf':
        plt.savefig('gain_spectra-MB_PE_comps-dB%(add)s.pdf' % {'add' : add_name})
    plt.close()

    if save_txt:
        save_array = (interp_grid, 10*np.log10(np.exp(abs(interp_values)*6.5e-3)))
        np.savetxt('gain_spectra-MB_PE_comps-dB%(add)s-Total.csv' 
                    % {'add' : add_name}, 
                    save_array, delimiter=',')
        save_array = (interp_grid, 10*np.log10(np.exp(abs(interp_values_PE)*6.5e-3)))
        np.savetxt('gain_spectra-MB_PE_comps-dB%(add)s-PE.csv' 
                    % {'add' : add_name}, 
                    save_array, delimiter=',')
        save_array = (interp_grid, 10*np.log10(np.exp(abs(interp_values_MB)*6.5e-3)))
        np.savetxt('gain_spectra-MB_PE_comps-dB%(add)s-MB.csv' 
                    % {'add' : add_name}, 
                    save_array, delimiter=',')

    return interp_values


#### Standard plotting of spectra #############################################
def plt_mode_fields(sim_wguide, n_points=500, quiver_steps=50, 
                  xlim_min=None, xlim_max=None, ylim_min=None, ylim_max=None,
                  EM_AC='EM', stress_fields=False, pdf_png='png', add_name=''):
    """ Plot EM mode fields.
    NOTE: z component of EM field needs comes scaled by 1/(i beta),
    which must be reintroduced!

        Args:
            sim_wguide : A :Struct: instance that has had calc_modes calculated

        Keyword Args:
            n_points  (int): The number of points across unitcell to \
                interpolate the field onto.

            xlim_min  (float): Limit plotted xrange to xlim_min:(1-xlim_max) of unitcell

            xlim_max  (float): Limit plotted xrange to xlim_min:(1-xlim_max) of unitcell

            ylim_min  (float): Limit plotted yrange to ylim_min:(1-ylim_max) of unitcell

            ylim_max  (float): Limit plotted yrange to ylim_min:(1-ylim_max) of unitcell

            EM_AC  (str): Either 'EM' or 'AC' modes

            stress_fields  (bool): Calculate acoustic stress fields

            pdf_png  (str): File type to save, either 'png' or 'pdf' 

            add_name  (str): Add a string to the file name.
    """

    if EM_AC is not 'EM' and EM_AC is not 'AC':
        raise ValueError("EM_AC must be either 'AC' or 'EM'.")

    plt.clf()

    # field mapping
    x_tmp = []
    y_tmp = []
    for i in np.arange(sim_wguide.n_msh_pts):
        x_tmp.append(sim_wguide.x_arr[0,i])
        y_tmp.append(sim_wguide.x_arr[1,i])
    x_min = np.min(x_tmp); x_max=np.max(x_tmp)
    y_min = np.min(y_tmp); y_max=np.max(y_tmp)
    area = abs((x_max-x_min)*(y_max-y_min))
    n_pts_x = int(n_points*abs(x_max-x_min)/np.sqrt(area))
    n_pts_y = int(n_points*abs(y_max-y_min)/np.sqrt(area))
    # n_pts_x = 100
    # n_pts_y = 100
    v_x=np.zeros(n_pts_x*n_pts_y)
    v_y=np.zeros(n_pts_x*n_pts_y)
    i=0
    for x in np.linspace(x_min,x_max,n_pts_x):
        for y in np.linspace(y_min,y_max,n_pts_y):
            v_x[i] = x
            v_y[i] = y
            i+=1
    v_x = np.array(v_x)
    v_y = np.array(v_y)

    # unrolling data for the interpolators
    table_nod = sim_wguide.table_nod.T
    x_arr = sim_wguide.x_arr.T

    for ival in range(len(sim_wguide.Eig_values)):
        # dense triangulation with multiple points
        v_x6p = np.zeros(6*sim_wguide.n_msh_el)
        v_y6p = np.zeros(6*sim_wguide.n_msh_el)
        v_Ex6p = np.zeros(6*sim_wguide.n_msh_el, dtype=np.complex128)
        v_Ey6p = np.zeros(6*sim_wguide.n_msh_el, dtype=np.complex128)
        v_Ez6p = np.zeros(6*sim_wguide.n_msh_el, dtype=np.complex128)
        v_triang6p = []

        i = 0
        for i_el in np.arange(sim_wguide.n_msh_el):
            # triangles
            idx = np.arange(6*i_el, 6*(i_el+1))
            triangles = [[idx[0], idx[3], idx[5]],
                         [idx[1], idx[4], idx[3]],
                         [idx[2], idx[5], idx[4]],
                         [idx[3], idx[4], idx[5]]]
            v_triang6p.extend(triangles)

            for i_node in np.arange(6):
                # index for the coordinates
                i_ex = table_nod[i_el, i_node]-1
                # values
                v_x6p[i] = x_arr[i_ex, 0]
                v_y6p[i] = x_arr[i_ex, 1]
                v_Ex6p[i] = sim_wguide.sol1[0,i_node,ival,i_el]
                v_Ey6p[i] = sim_wguide.sol1[1,i_node,ival,i_el]
    #             if EM_AC == 'EM':
    # # Note physical z-comp of EM modes is -i beta E_z, where E_z is FEM output sol
    #                 v_Ez6p[i] = -1j*sim_wguide.Eig_values[ival]*sim_wguide.sol1[2,i_node,ival,i_el]
    #             else:
                v_Ez6p[i] = sim_wguide.sol1[2,i_node,ival,i_el]
                i += 1

        v_E6p = np.sqrt(np.abs(v_Ex6p)**2 +
                        np.abs(v_Ey6p)**2 +
                        np.abs(v_Ez6p)**2)

        ### Interpolate onto triangular grid - honest to FEM elements
        # dense triangulation with unique points
        v_triang1p = []
        for i_el in np.arange(sim_wguide.n_msh_el):
            # triangles
            triangles = [[table_nod[i_el,0]-1,table_nod[i_el,3]-1,table_nod[i_el,5]-1],
                         [table_nod[i_el,1]-1,table_nod[i_el,4]-1,table_nod[i_el,3]-1],
                         [table_nod[i_el,2]-1,table_nod[i_el,5]-1,table_nod[i_el,4]-1],
                         [table_nod[i_el,3]-1,table_nod[i_el,4]-1,table_nod[i_el,5]-1]]
            v_triang1p.extend(triangles)

        # triangulations
        triang6p = matplotlib.tri.Triangulation(v_x6p,v_y6p,v_triang6p)
        triang1p = matplotlib.tri.Triangulation(x_arr[:,0],x_arr[:,1],v_triang1p)

        # building interpolators: triang1p for the finder, triang6p for the values
        finder = matplotlib.tri.TrapezoidMapTriFinder(triang1p)
        ReEx = matplotlib.tri.LinearTriInterpolator(triang6p,v_Ex6p.real,trifinder=finder)
        ImEx = matplotlib.tri.LinearTriInterpolator(triang6p,v_Ex6p.imag,trifinder=finder)
        ReEy = matplotlib.tri.LinearTriInterpolator(triang6p,v_Ey6p.real,trifinder=finder)
        ImEy = matplotlib.tri.LinearTriInterpolator(triang6p,v_Ey6p.imag,trifinder=finder)
        ReEz = matplotlib.tri.LinearTriInterpolator(triang6p,v_Ez6p.real,trifinder=finder)
        ImEz = matplotlib.tri.LinearTriInterpolator(triang6p,v_Ez6p.imag,trifinder=finder)
        AbsE = matplotlib.tri.LinearTriInterpolator(triang6p,v_E6p,trifinder=finder)
        # interpolated fields
        m_ReEx = ReEx(v_x,v_y).reshape(n_pts_x,n_pts_y)
        m_ReEy = ReEy(v_x,v_y).reshape(n_pts_x,n_pts_y)
        m_ReEz = ReEz(v_x,v_y).reshape(n_pts_x,n_pts_y)
        m_ImEx = ImEx(v_x,v_y).reshape(n_pts_x,n_pts_y)
        m_ImEy = ImEy(v_x,v_y).reshape(n_pts_x,n_pts_y)
        m_ImEz = ImEz(v_x,v_y).reshape(n_pts_x,n_pts_y)
        m_AbsE = AbsE(v_x,v_y).reshape(n_pts_x,n_pts_y)


        # Flip y order as imshow has origin at top left
        v_plots = [m_ReEx[:,::-1],m_ReEy[:,::-1],m_ReEz[:,::-1],m_ImEx[:,::-1],m_ImEy[:,::-1],m_ImEz[:,::-1],m_AbsE[:,::-1]]
        if EM_AC=='EM':
            v_labels = ["Re(E_x)","Re(E_y)","Re(E_z)","Im(E_x)","Im(E_y)","Im(E_z)","Abs(E)"]
        else:
            v_labels = ["Re(u_x)","Re(u_y)","Re(u_z)","Im(u_x)","Im(u_y)","Im(u_z)","Abs(u)"]

        # field plots
        plot_threshold = 1e-6 # set negligible components to explicitly zero
        plt.clf()
        fig = plt.figure(figsize=(15,15))
        for i_p,plot in enumerate(v_plots):
            ax = plt.subplot(3,3,i_p+1)
            if np.max(np.abs(plot[~np.isnan(plot)])) < plot_threshold:
                # im = plt.imshow(plot.T,cmap='viridis');
                im = plt.imshow(np.zeros(np.shape(plot.T)));
            else:
                im = plt.imshow(plot.T);
            # ax.set_aspect('equal')
            # no ticks
            plt.xticks([])
            plt.yticks([])
            # limits
            axes = plt.gca()
            xmin, xmax = axes.get_xlim()
            ymin, ymax = axes.get_ylim()
            width_x = xmax-xmin
            width_y = ymax-ymin
            if xlim_min != None:
                ax.set_xlim(xmin+xlim_min*width_x,xmax-xlim_max*width_x)
            if ylim_min != None:
                ax.set_ylim(ymin+ylim_min*width_y,ymax-ylim_max*width_y)
            # titles
            plt.title(v_labels[i_p],fontsize=title_font-4)
            # colorbar
            divider = make_axes_locatable(ax)
            cax = divider.append_axes("right", size="5%", pad=0.1)
            cbar = plt.colorbar(im, cax=cax)
            cbar.ax.tick_params(labelsize=title_font-10)


        if EM_AC=='AC':
            v_x_q = v_x.reshape(n_pts_x,n_pts_y)
            v_y_q = v_y.reshape(n_pts_x,n_pts_y)
            v_x_q = v_x_q[0::quiver_steps,0::quiver_steps]
            v_y_q = v_y_q[0::quiver_steps,0::quiver_steps]
            m_ReEx_q = m_ReEx[0::quiver_steps,0::quiver_steps]
            m_ReEy_q = m_ReEy[0::quiver_steps,0::quiver_steps]
            m_ImEx_q = m_ImEx[0::quiver_steps,0::quiver_steps]
            m_ImEy_q = m_ImEy[0::quiver_steps,0::quiver_steps]
            ax = plt.subplot(3,3,i_p+2)
            plt.quiver(v_x_q, v_y_q,
                (m_ReEx_q+m_ImEx_q), (m_ReEy_q+m_ImEy_q),      # data
                np.sqrt(np.real((m_ReEx_q+1j*m_ImEx_q)*(m_ReEx_q-1j*m_ImEx_q)
                +(m_ReEy_q+1j*m_ImEy_q)*(m_ReEy_q-1j*m_ImEy_q))),  #colour the arrows based on this array
                linewidths=(0.2,), edgecolors=('k'), pivot='mid', headlength=5) # length of the arrows
            ax.set_aspect('equal')
            plt.xticks([])
            plt.yticks([])
            axes = plt.gca()
            xmin, xmax = axes.get_xlim()
            ymin, ymax = axes.get_ylim()
            if xlim_min != None:
                ax.set_xlim(xlim_min*xmax,(1-xlim_max)*xmax)
            if ylim_min != None:
                ax.set_ylim((1-ylim_min)*ymin, ylim_max*ymin)
            plt.title('Transverse',fontsize=title_font-4)

        if EM_AC=='EM':
            n_eff = sim_wguide.Eig_values[ival] * sim_wguide.wl_m / (2*np.pi)
            if np.imag(sim_wguide.Eig_values[ival]) < 0:
                k_str = r'k$_z = %(re_k)f6 %(im_k)f6 i$'% \
                    {'re_k' : np.real(sim_wguide.Eig_values[ival]),
                    'im_k' : np.imag(sim_wguide.Eig_values[ival])}
                n_str = r'n$_{eff} = %(re_k)f6 %(im_k)f6 i$'% \
                    {'re_k' : np.real(n_eff), 'im_k' : np.imag(n_eff)}
            else:
                k_str = r'k$_z = %(re_k)f6 + %(im_k)f6 i$'% \
                    {'re_k' : np.real(sim_wguide.Eig_values[ival]),
                    'im_k' : np.imag(sim_wguide.Eig_values[ival])}
                n_str = r'n$_{eff} = %(re_k)f6 + %(im_k)f6 i$'% \
                    {'re_k' : np.real(n_eff), 'im_k' : np.imag(n_eff)}
            # plt.text(10, 0.3, n_str, fontsize=title_font)
        else:
            n_str = ''
            if np.imag(sim_wguide.Eig_values[ival]) < 0:
                k_str = r'$\Omega/2\pi = %(re_k)f6 %(im_k)f6 i$ GHz'% \
                    {'re_k' : np.real(sim_wguide.Eig_values[ival]*1e-9),
                    'im_k' : np.imag(sim_wguide.Eig_values[ival]*1e-9)}
            else:
                k_str = r'$\Omega/2\pi = %(re_k)f6 + %(im_k)f6 i$ GHz'% \
                    {'re_k' : np.real(sim_wguide.Eig_values[ival]*1e-9),
                    'im_k' : np.imag(sim_wguide.Eig_values[ival]*1e-9)}
        # plt.text(10, 0.5, k_str, fontsize=title_font)
        plt.suptitle(k_str + '   ' + n_str+"\n", fontsize=title_font)
        # plt.tight_layout(pad=2.5, w_pad=0.5, h_pad=1.0)
        fig.set_tight_layout(True)

        if not os.path.exists("fields"):
            os.mkdir("fields")
        if pdf_png=='png':
            plt.savefig('fields/%(s)s_field_%(i)i%(add)s.png' %
                {'s' : EM_AC, 'i' : ival, 'add' : add_name})
                #, bbox_inches='tight') - this caused error in Q calc... ?
        elif pdf_png=='pdf':
            plt.savefig('fields/%(s)s_field_%(i)i%(add)s.pdf' %
                {'s' : EM_AC, 'i' : ival, 'add' : add_name}, bbox_inches='tight')
        else:
            raise ValueError("pdf_png must be either 'png' or 'pdf'.")
        plt.close()


        if EM_AC=='AC' and stress_fields is True:
            ### Interpolate onto rectangular Cartesian grid
            xy = list(zip(v_x6p, v_y6p))
            grid_x, grid_y = np.mgrid[x_min:x_max:n_pts_x*1j, y_min:y_max:n_pts_y*1j]
            m_ReEx = interpolate.griddata(xy, v_Ex6p.real, (grid_x, grid_y), method='linear')
            m_ReEy = interpolate.griddata(xy, v_Ey6p.real, (grid_x, grid_y), method='linear')
            m_ReEz = interpolate.griddata(xy, v_Ez6p.real, (grid_x, grid_y), method='linear')
            m_ImEx = interpolate.griddata(xy, v_Ex6p.imag, (grid_x, grid_y), method='linear')
            m_ImEy = interpolate.griddata(xy, v_Ey6p.imag, (grid_x, grid_y), method='linear')
            m_ImEz = interpolate.griddata(xy, v_Ez6p.imag, (grid_x, grid_y), method='linear')
            m_AbsE = interpolate.griddata(xy, v_E6p.real, (grid_x, grid_y), method='linear')
            dx = grid_x[-1,0] - grid_x[-2,0]
            dy = grid_y[0,-1] - grid_y[0,-2]
            m_Ex = m_ReEx + 1j*m_ImEx
            m_Ey = m_ReEy + 1j*m_ImEy
            m_Ez = m_ReEz + 1j*m_ImEz
            m_Ex = m_Ex.reshape(n_pts_x,n_pts_y)
            m_Ey = m_Ey.reshape(n_pts_x,n_pts_y)
            m_Ez = m_Ez.reshape(n_pts_x,n_pts_y)
            m_AbsE = m_AbsE.reshape(n_pts_x,n_pts_y)

            m_ReEx = np.real(m_Ex)
            m_ReEy = np.real(m_Ey)
            m_ReEz = np.real(m_Ez)
            m_ImEx = np.imag(m_Ex)
            m_ImEy = np.imag(m_Ey)
            m_ImEz = np.imag(m_Ez)

            del_x_Ex = np.gradient(m_Ex, dx, axis=0)
            del_y_Ex = np.gradient(m_Ex, dy, axis=1)
            del_x_Ey = np.gradient(m_Ey, dx, axis=0)
            del_y_Ey = np.gradient(m_Ey, dy, axis=1)
            del_x_Ez = np.gradient(m_Ez, dx, axis=0)
            del_y_Ez = np.gradient(m_Ez, dy, axis=1)
            del_z_Ex = 1j*sim_wguide.k_AC*m_Ex
            del_z_Ey = 1j*sim_wguide.k_AC*m_Ey
            del_z_Ez = 1j*sim_wguide.k_AC*m_Ez

            # Flip y order as imshow has origin at top left
            del_mat = np.array([del_x_Ex[:,::-1].real, del_x_Ey[:,::-1].real, del_x_Ez[:,::-1].real, del_x_Ex[:,::-1].imag, del_x_Ey[:,::-1].imag, del_x_Ez[:,::-1].imag, del_y_Ex[:,::-1].real, del_y_Ey[:,::-1].real, del_y_Ez[:,::-1].real, del_y_Ex[:,::-1].imag, del_y_Ey[:,::-1].imag, del_y_Ez[:,::-1].imag, del_z_Ex[:,::-1].real, del_z_Ey[:,::-1].real, del_z_Ez[:,::-1].real, del_z_Ex[:,::-1].imag, del_z_Ey[:,::-1].imag, del_z_Ez[:,::-1].imag])
            v_labels = ["Re(S_xx)","Re(S_xy)","Re(S_xz)","Im(S_xx)","Im(S_xy)","Im(S_xz)","Re(S_yx)","Re(S_yy)","Re(S_yz)","Im(S_yx)","Im(S_yy)","Im(S_yz)","Re(S_zx)","Re(S_zy)","Re(S_zz)","Im(S_zx)","Im(S_zy)","Im(S_zz)"]

            # field plots
            plt.clf()
            fig = plt.figure(figsize=(15,30))
            for i_p,plot in enumerate(del_mat):
                ax = plt.subplot(6,3,i_p+1)
                im = plt.imshow(plot.T);
                # no ticks
                plt.xticks([])
                plt.yticks([])
                # limits
                if xlim_min != None:
                    ax.set_xlim(xlim_min*n_points,(1-xlim_max)*n_points)
                if ylim_min != None:
                    ax.set_ylim((1-ylim_min)*n_points,ylim_max*n_points)
                # titles
                plt.title(v_labels[i_p],fontsize=title_font-4)
                # colorbar
                divider = make_axes_locatable(ax)
                cax = divider.append_axes("right", size="5%", pad=0.1)
                cbar = plt.colorbar(im, cax=cax, format='%.2e')
                cbar.ax.tick_params(labelsize=title_font-10)
            # plt.tight_layout(pad=0.4, w_pad=0.5, h_pad=1.0)
            fig.set_tight_layout(True)
            n_str = ''
            if np.imag(sim_wguide.Eig_values[ival]) < 0:
                k_str = r'$\Omega/2\pi = %(re_k)f6 %(im_k)f6 i$ GHz'% \
                    {'re_k' : np.real(sim_wguide.Eig_values[ival]*1e-9),
                    'im_k' : np.imag(sim_wguide.Eig_values[ival]*1e-9)}
            else:
                k_str = r'$\Omega/2\pi = %(re_k)f6 + %(im_k)f6 i$ GHz'% \
                    {'re_k' : np.real(sim_wguide.Eig_values[ival]*1e-9),
                    'im_k' : np.imag(sim_wguide.Eig_values[ival]*1e-9)}
            plt.suptitle(k_str + '   ' + n_str, fontsize=title_font)

            if pdf_png=='png':
                plt.savefig('fields/%(s)s_S_field_%(i)i%(add)s.png' %
                    {'s' : EM_AC, 'i' : ival, 'add' : add_name})
            elif pdf_png=='pdf':
                plt.savefig('fields/%(s)s_S_field_%(i)i%(add)s.pdf' %
                    {'s' : EM_AC, 'i' : ival, 'add' : add_name}, bbox_inches='tight')
            plt.close()



#### Plot mesh #############################################
def plot_msh(x_arr, add_name=''):
    """ Plot EM mode fields.

        Args:
            sim_wguide : A :Struct: instance that has had calc_modes calculated

        Keyword Args:
            n_points  (int): The number of points across unitcell to \
                interpolate the field onto.
    """

    plt.clf()
    plt.figure(figsize=(13,13))
    ax = plt.subplot(1,1,1)
    for node in range(np.shape(x_arr)[1]):
        plt.plot(x_arr[0,node], x_arr[1,node], 'o')
    ax.set_aspect('equal')
    plt.savefig('msh_%(add)s.pdf' %
        {'add' : add_name}, bbox_inches='tight')
    plt.close()



### Plot nodal arrangement on mesh triangle.
# plt.figure(figsize=(13,13))
# el = 1
# plt.clf()
# for i in range(0,6):
#     print table_nod[i][el] - 1
#     x = x_arr[0,table_nod[i][el] - 1]
#     y = x_arr[1,table_nod[i][el] - 1]
#     print 'x1 = ', x_arr[0,table_nod[i][el] - 1]
#     print 'y1 = ', x_arr[1,table_nod[i][el] - 1]
#     plt.plot(x, y, 'o')
#     plt.text(x+0.001, y+0.001, str(i))
# plt.savefig('triangle_%i.png' %el)
# plt.close()
