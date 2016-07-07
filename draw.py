import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.patches import Circle, Rectangle, Arc

def draw_court(ax=None, color='black', lw=2, outer_lines=False):
    """
    from http://savvastjortjoglou.com/nba-shot-sharts.html
    """
    # If an axes object isn't provided to plot onto, just get current one
    if ax is None:
        ax = plt.gca()

    # Create the various parts of an NBA basketball court

    # Create the basketball hoop
    # Diameter of a hoop is 18" so it has a radius of 9", which is a value
    # 7.5 in our coordinate system
    hoop = Circle((0, 0), radius=7.5, linewidth=lw, color=color, fill=False)

    # Create backboard
    backboard = Rectangle((-30, -7.5), 60, -1, linewidth=lw, color=color)

    # The paint
    # Create the outer box 0f the paint, width=16ft, height=19ft
    outer_box = Rectangle((-80, -47.5), 160, 190, linewidth=lw, color=color,
                          fill=False)
    # Create the inner box of the paint, widt=12ft, height=19ft
    inner_box = Rectangle((-60, -47.5), 120, 190, linewidth=lw, color=color,
                          fill=False)

    # Create free throw top arc
    top_free_throw = Arc((0, 142.5), 120, 120, theta1=0, theta2=180,
                         linewidth=lw, color=color, fill=False)
    # Create free throw bottom arc
    bottom_free_throw = Arc((0, 142.5), 120, 120, theta1=180, theta2=0,
                            linewidth=lw, color=color, linestyle='dashed')
    # Restricted Zone, it is an arc with 4ft radius from center of the hoop
    restricted = Arc((0, 0), 80, 80, theta1=0, theta2=180, linewidth=lw,
                     color=color)

    # Three point line
    # Create the side 3pt lines, they are 14ft long before they begin to arc
    corner_three_a = Rectangle((-220, -47.5), 0, 140, linewidth=lw,
                               color=color)
    corner_three_b = Rectangle((220, -47.5), 0, 140, linewidth=lw, color=color)
    # 3pt arc - center of arc will be the hoop, arc is 23'9" away from hoop
    # I just played around with the theta values until they lined up with the
    # threes
    three_arc = Arc((0, 0), 475, 475, theta1=22, theta2=158, linewidth=lw,
                    color=color)

    # Center Court
    center_outer_arc = Arc((0, 422.5), 120, 120, theta1=180, theta2=0,
                           linewidth=lw, color=color)
    center_inner_arc = Arc((0, 422.5), 40, 40, theta1=180, theta2=0,
                           linewidth=lw, color=color)

    # List of the court elements to be plotted onto the axes
    court_elements = [hoop, backboard, outer_box, inner_box, top_free_throw,
                      bottom_free_throw, restricted, corner_three_a,
                      corner_three_b, three_arc, center_outer_arc,
                      center_inner_arc]

    if outer_lines:
        # Draw the half court line, baseline and side out bound lines
        outer_lines = Rectangle((-250, -47.5), 500, 470, linewidth=lw,
                                color=color, fill=False)
        court_elements.append(outer_lines)

    # Add the court elements onto the axes
    for element in court_elements:
        ax.add_patch(element)

    return ax


def find_shot_vals(shot_df, gridNum):
    gridNum = 30

    x = shot_df.LOC_X[shot_df['LOC_Y']<422.5]
    y = shot_df.LOC_Y[shot_df['LOC_Y']<422.5]

    hb_missed = plt.hexbin(x, y, gridsize=gridNum, extent=(-250,250,422.5,-50));
    plt.close()

    hb_next = {}

    for pt in range(4,-5,-1):
        x_next = shot_df.LOC_X[(shot_df['NEXT']==pt) & (shot_df['LOC_Y'] < 422.5)]
        y_next = shot_df.LOC_Y[(shot_df['NEXT']==pt) & (shot_df['LOC_Y'] < 422.5)]

        hb_next[pt] = plt.hexbin(x_next, y_next, gridsize=gridNum, extent=(-250,250,422.5,-50),cmap=plt.cm.Reds);
        plt.close()

    hb_val = sum( [hb_next[pt].get_array() * pt for pt in hb_next.keys()] )

    hb_avg = hb_val / hb_missed.get_array()
    hb_avg[np.isnan(hb_avg)] = 0

    return hb_avg, hb_missed


def shooting_plot(shot_df, plot_size=(12,11), gridNum=30, mymap=plt.get_cmap('Spectral')):

    from matplotlib.patches import Circle
    x = shot_df.LOC_X[shot_df['LOC_Y']<425.1]
    y = shot_df.LOC_Y[shot_df['LOC_Y']<425.1]

    (shotVals, shotNumber) = find_shot_vals(shot_df, gridNum)

    fig = plt.figure(figsize=plot_size)
    cmap = mymap
    ax = plt.axes([0.1, 0.1, 0.8, 0.8])
    draw_court(outer_lines=False)
    plt.xlim(-250,250)
    plt.ylim(422.5, -47.5)

    norm = mpl.colors.Normalize(vmin=-0.5, vmax = -0.1)

    import math
    def logistic(x):
        return 20 / (1 + math.exp(-0.18*(x-np.median(shotNumber.get_array()))))

    for i, shots in enumerate(shotVals):
        restricted = Circle(shotNumber.get_offsets()[i], radius=shotNumber.get_array()[i],
                            color=cmap(norm(shots)),alpha=0.8, fill=True)
        restricted.radius = logistic( np.sqrt(restricted.radius) )
        if restricted.radius > 240/gridNum: restricted.radius=240/gridNum
        ax.add_patch(restricted)

    ax2 = fig.add_axes([0.92, 0.1, 0.02, 0.8])
    cb = mpl.colorbar.ColorbarBase(ax2,cmap=cmap, orientation='vertical')
    cb.set_label('next-possession value')
    cb.set_ticks([0.0, 0.25, 0.5, 0.75, 1.0])
    cb.set_ticklabels(['-0.5','-0.4', '-0.3','-0.2', '-0.1'])

    plt.show()

    return ax
